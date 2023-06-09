import os
import json
import math
import json
import time
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from application.helpers.core import send_log_slack_message
from models import Sellers,SellerProducts,Supplies,ProductTypes,SellerCertificateTypes

class SellerMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def get_product_score(self,score_id):
        response = requests.get(f"{self.source_url}/tridge-sellerprofilescores/_doc/{score_id}",auth=self.basic_auth)
        
        if response.status_code == 200:
            content = response.json()['_source']
            return content['totalProfileScore']        

        return None

    def create_record(self,item):
        record,created = Sellers.get_or_create(src_id=item['id'],source='tridge')
        
        if created:
            try:
                created_at = datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
            except ValueError:
                created_at = datetime.now()
                
            record.created = created_at.timestamp()
            record.save()
            print(f'created {record.id}')

        else:
            print(f'exists {record.id}')

        return record
    
    
    def relate_supplies(self,item,item_id,payload):
        supplies = [i['id'] for i in item['supplies']]
        records = Supplies.select().where(Supplies.src_id.in_(supplies),
            Supplies.source=='tridge')
        
        for record in records:
            record_id = record.id
            cat_resp = requests.get(f"{self.dest_url}/supplies/_doc/{record_id}")
            
            if cat_resp.status_code == 200:
                payload['supplies'].append(record_id)
                record.seller_id = item_id
                record.save()

            else:
                print(f'Supply {record_id}')
                raise Exception()
            
    def relate_products(self,item,item_id,payload):
        products = [i['id'] for i in item['supplyingProducts']]
        records = ProductTypes.select().where(ProductTypes.src_id.in_(products),
            ProductTypes.source=='tridge').dicts()
        
        for record in records:
            record_id = record['id']
            cat_resp = requests.get(f"{self.dest_url}/product_types/_doc/{record_id}")
            
            if cat_resp.status_code == 200:
                payload['supplying_products'].append(record_id)
                record, created = SellerProducts.get_or_create(seller_id=item_id,product_id=record_id)
                
                if created:
                    record.created = time.time()

            else:
                print(f'Product {record_id}')
                raise Exception()
            
    def relate_certificates(self,item,item_id,payload):
        certificates = [i['id'] for i in item['certificates']]
        records = SellerCertificateTypes.select().where(SellerCertificateTypes.src_id.in_(certificates),
            SellerCertificateTypes.source=='tridge')
        
        for record in records:
            record_id = record.id
            cat_resp = requests.get(f"{self.dest_url}/seller_certifications/_doc/{record_id}")
            
            if cat_resp.status_code == 200:
                payload['certificates'].append(record_id)
                record.seller_id = item_id
                record.save()

            else:
                print(f'Certificate {record_id}')
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

        response_count = requests.get(f"{self.source_url}/tridge-sellers/_count",auth=self.basic_auth)
        print(response_count.content)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-sellers/_search",json=search_data,auth=self.basic_auth)
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
                            'code':item['code'],
                            'created':item['createdAt'],
                            'updated':item['updatedAt'],
                            'country':item['country']['name'],
                            'summary':item['summary'],
                            'profile_score':None,
                            'profile_status':item['profileStatus'],
                            'exporting_countries':[item['name'] for item in item['exportingCountries']],
                            'supplying_products':[], # Implement
                            'certificates':[],  # Implement,
                            'establishment':item['establishment'],
                            'validation_status':item['validationStatus'],
                            'annual_revenue_amount':item['annualRevenueAmount'],
                            'has_warehouse':item['hasWarehouse'],
                            'has_export_experience':item['hasExportExperience'],
                            'export_ratio':item['exportRatio'],
                            'adjusted_supplier_directory_score':item['adjustedSupplierDirectoryScore'],
                            'decayed_total_score':item['decayedTotalScore'],
                            'business_types':item['businessTypes'],
                            'sales_employee_count':item['salesEmployeeCount'],
                            'supply_count':item['supplyCount'],
                            'facility_count':item['facilityCount'],
                            'employee_count':item['employeeCount'],
                            'images':[item['image'] for item in item['images']],
                            'supplies':[],
                            'source':{
                                'id':item['id'],
                                'name':'tridge'
                            }
                        }
                        
                        if item.get('profileScore'):
                            payload['profile_score'] = self.get_product_score(item['profileScore']['id'])

   
                        self.relate_supplies(item,item_id,payload)
                        self.relate_products(item,item_id,payload)
                        self.relate_certificates(item,item_id,payload)

                        record.payload = payload
                        record.save()
                        response = requests.post(f"{self.dest_url}/sellers/_doc/{item_id}",json=payload)
                        
                        if not response.ok:
                            send_log_slack_message(response.content)
                            print(f'Failed {item_id}')


