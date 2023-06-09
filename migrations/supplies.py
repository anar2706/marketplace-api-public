import os
import json
import math
import json
import time
import traceback
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from models import SupplyAttributes,ProductTypes,Supplies,Attributes,Countries
from application.helpers.core import send_log_slack_message


countries = Countries.select(Countries.code,Countries.name).dicts()
countries = {item['code']:item for item in countries}

class SupplyMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item):
        record,created = Supplies.get_or_create(src_id=item['id'],source='tridge')
        
        if created:
            try:
                created_at = datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
            except ValueError:
                created_at = datetime.now()
                
            record.created = created_at.timestamp()
            record.save()
            print(f'created {item["id"]} {record.id}')

        else:
            print(f'exists {item["id"]} {record.id}')

        return record
    
    def get_product_id(self,src_product_id):
        return ProductTypes.select().where(ProductTypes.src_id==src_product_id,
                ProductTypes.source=='tridge').dicts()[0]['id']

    def add_country(self,item,payload):
        if item.get('countryOfOrigin') and item['countryOfOrigin'].get('code'):
            country_code = item['countryOfOrigin']['code']
            record = countries[country_code]
            payload['country'] = {
                'code':record['code'],
                'name':record['name']
            }

    def relate_attributes(self,item,item_id,payload):
        attributes = [i['id'] for i in item['attributes']]
        attr_records = Attributes.select(Attributes.id).where(Attributes.src_id.in_(attributes),
                Attributes.source=='tridge').dicts()
        
        for record in attr_records:
            record_id = record['id']

            cat_resp = requests.get(f"{self.dest_url}/attributes/_doc/{record_id}")
            if cat_resp.status_code == 200:
                payload['attributes'].append(record_id)
                record, created = SupplyAttributes.get_or_create(supply_id=item_id,attribute_id=record_id)
                
                if created:
                    record.created = time.time()

            else:
                print(f'Supply {record_id}')
                raise Exception()
    
    def call(self):
        search_data = {
            "size": 10000,
            "query": {
                "match_all" : {
                }
            },
            "sort": [{"id": "asc"}]
        }
        response_count = requests.get(f"{self.source_url}/tridge-supplies/_count",auth=self.basic_auth)
        print(response_count.content)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-supplies/_search",json=search_data,auth=self.basic_auth)
                if response.status_code == 200:
                    content = json.loads(response.content)
                    hits = content['hits']['hits']
            
                    for hit in hits:
                        last_id = hit['sort'][0]
                        item = hit['_source']
                        record  = self.create_record(item)
                        item_id = record.id
                        
                        try:

                            payload = {
                                'id':item_id,
                                'name':item['productName'],
                                'code':item['code'],
                                'images':[], # Implement Later
                                'product_id':self.get_product_id(item['product']['id']),
                                'attributes':[],
                                'export':{
                                    'volume':item['export'],
                                    'unit':item['exportUnit'],
                                    'frequency':item['exportFrequency']
                                },
                                'capacity':{
                                    'volume':item['capacity'],
                                    'unit':item['capacityUnit'],
                                    'frequency':item['capacityFrequency']
                                },
                                'seasons':item['seasons'],
                                'description':item['productSpec'],
                                'created_at':item['createdAt'],
                                'updated_at':item['updatedAt'],
                                'source':{
                                    'id':item['id'],
                                    'source':'tridge'
                                }
                            }
                            

                            self.relate_attributes(item,item_id,payload)
                            self.add_country(item,payload)

                            record.payload = payload
                            record.save()
                            response = requests.post(f"{self.dest_url}/supplies/_doc/{item_id}",json=payload)

                        except Exception:
                            send_log_slack_message(traceback.format_exc())


