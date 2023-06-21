import os
import json
import math
import json
import requests
from datetime import datetime
from models import Regions
from requests.auth import HTTPBasicAuth

class RegionMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item):
        record,created = Regions.get_or_create(src_id=item['id'],source='tridge',
            name=item['nameRaw'],code=item['code'],country_id=item['countryId'])
        
        if created:
            created_at = datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
            record.created = created_at.timestamp()
            record.save()

        return record

    
    def call(self):
        search_data = {
            "size": 10000,
            "query": {
                "match_all" : {
                }
            },
            "sort": [{"_id": "asc"}]
        }
        
        response_count = requests.get(f"{self.source_url}/tridge-regions/_count",auth=self.basic_auth)
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-regions/_search",json=search_data,auth=self.basic_auth)
                
                if response.status_code == 200:
                    content = json.loads(response.content)
                    hits = content['hits']['hits']
                
                    for hit in hits:
                        last_id = hit['sort'][0]
                        item = hit['_source']
                        record  = self.create_record(item)
                        item_id = record.id
                        
                        payload = {
                            'id':item_id,
                            'name':item['nameRaw'],
                            'label':item['nameLabel'],
                            'code':item['code'],
                            'country_id':item['countryId'],
                            'tier':item['tier'],
                            'source':{
                                'id':item['id'],
                                'name':'tridge'
                            }
                        }

                        record.payload = payload
                        record.save()
                        response = requests.post(f"{self.dest_url}/regions/_doc/{item_id}",json=payload)


