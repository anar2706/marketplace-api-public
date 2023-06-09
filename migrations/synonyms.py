import os
import json
import math
import json
import requests
from datetime import datetime
from models import ProductSynonyms
from requests.auth import HTTPBasicAuth

class ProductSynonym:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item,item_id):
        record,created = ProductSynonyms.get_or_create(src_id=item_id,source='tridge')
        
        if created:
            record.name = item['name']
            record.product_id = item['productId']
            record.product_name = item['product']['name']
            record.created = datetime.now().timestamp()
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
        response_count = requests.get(f"{self.source_url}/tridge-productsynonyms/_count",auth=self.basic_auth)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-productsynonyms/_search",json=search_data,auth=self.basic_auth)
                
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
                            'product_id':item['productId'],
                            'product_name':item['product']['name'],
                            'source':{
                                'id':hit['_id'],
                                'name':'tridge'
                            }
                        }

                        record.save()

                        response = requests.post(f"{self.dest_url}/product_synonyms/_doc/{item_id}",json=payload)


