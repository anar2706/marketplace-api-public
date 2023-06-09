import os
import json
import math
import json
import requests
from datetime import datetime
from models import SellerCertificateTypes
from requests.auth import HTTPBasicAuth

class SellerCertificateMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item):
        record,created = SellerCertificateTypes.get_or_create(src_id=item['id'],source='tridge',
                name=item['_verboseName'],code=item['certificate']['code'] if item.get('certificate') else None,issuing_date=item['issuingDate'],
                number=item['certificateNumber'])
        
        if created:
            created_at = datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
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
            "sort": [{"id": "asc"}]
        }

        response_count = requests.get(f"{self.source_url}/tridge-sellercertifications/_count",auth=self.basic_auth)
        print(response_count.content)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-sellercertifications/_search",json=search_data,auth=self.basic_auth)
                if response.status_code == 200:
                    content = json.loads(response.content)
                    hits = content['hits']['hits']
                
                    for hit in hits:
                        last_id = hit['sort'][0]
                        item = hit['_source']
                        record  = self.create_record(item)
                        item_id = record.id
                        
                        if not item:
                            continue

                        payload = {
                            'id':item_id,
                            'code':item['certificate']['code'] if item.get('certificate') else None,
                            'name':item['_verboseName'],
                            'organization':item['issuingOrganization'],
                            'validFrom':item['validFrom'],
                            'validTo':item['validTo'],
                            'number':item['certificateNumber'],
                            'issuing_date':item['issuingDate'],
                            'is_deleted':item['isDeleted'],
                            'source':{
                                'id':item['id'],
                                'name':'tridge'
                            }
                        }

                        record.payload = payload
                        record.save()

                        response = requests.post(f"{self.dest_url}/seller_certifications/_doc/{item_id}",json=payload)



