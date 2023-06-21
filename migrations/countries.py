import os
import json
import math
import json
import requests
from datetime import datetime
from models import Countries
from requests.auth import HTTPBasicAuth

class CountryMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item,item_id):
        record,created = Countries.get_or_create(source='tridge',name=item['name'],
            code=item['code'],continent=item['continent'],zone_id=item['zoneId'])
        
        if created:
            created_at = datetime.strptime(item['activeChangedAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
            record.src_id = item_id
            record.created = created_at.timestamp()
            record.save()
            print(f'created {record.id}')

        else:
            print(f'exists {record.id}')

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
        
        response_count = requests.get(f"{self.source_url}/tridge-countries/_count",auth=self.basic_auth)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-countries/_search",json=search_data,auth=self.basic_auth)
                
                if response.status_code == 200:
                    content = json.loads(response.content)
                    hits = content['hits']['hits']
                
                    for hit in hits:
                        last_id = hit['sort'][0]
                        item = hit['_source']
                        record  = self.create_record(item,hit['_id'])
                        item_id = record.id
                        

                        payload = {
                            'id':item_id,
                            'name':item['name'],
                            'zone_id':item['zoneId'],
                            'code':item['code'],
                            'native_name':item['nativeName'],
                            'continent_code':item['continentCode'],
                            'continent':item['continent'],
                            'capital':item['capitalCity'],
                            'currency':item['currency'],
                            'languages':item['languages'],
                            'credit_rating':item['creditRating'],
                            'phone_prefix':item['phonePrefix'],
                            'zone':{
                                'id':item['zoneId'],
                                'name':item['zone']['name'] if item.get('zone') else None
                            } ,
                            'source':{
                                'id':hit['_id'],
                                'name':'tridge'
                            }
                        }

                        record.payload = payload
                        record.save()

                        response = requests.post(f"{self.dest_url}/countries/_doc/{item_id}",json=payload)


