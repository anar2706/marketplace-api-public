import os
import json
import math
import json
import time
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from models import ProductTypes,Categories,ProductCategories,ProductSynonyms

class ProductTypeMigrator:

    def __init__(self) -> None:
        self.source_url = os.environ['SOURCE_ELASTIC_URL']
        self.dest_url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['SOURCE_ELASTIC_USER'],os.environ['SOURCE_ELSATIC_PASSWORD'])

    def create_record(self,item):
        record,created = ProductTypes.get_or_create(src_id=item['id'],source='tridge')
        
        if created:
            created_at = datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z")
            record.created = created_at.timestamp()
            record.save()
            print(f'created {record.id}')

        else:
            print(f'exists {record.id}')

        return record
    

    def add_synonyms(self,item):
        synonyms = item['synonyms']
        item_ids = [item['id'] for item in synonyms]
        if not item_ids:
            return []

        records = ProductSynonyms.select().where(ProductSynonyms.src_id.in_(item_ids)).dicts()
        records = [{'id':record['id'],'name':record['name']} for record in records]
        return records


    def relate_categories(self,item,item_id,payload):
        categories = [item['category1Id'],item['category2Id'],item['category3Id']]
        for category in categories:
            category_id = Categories.select().where(Categories.src_id==category,
                    Categories.source=='tridge').dicts()
            
            if not category_id:
                continue
                
            category_id = category_id[0]['id']
            cat_resp = requests.get(f"{self.dest_url}/categories/_doc/{category_id}")
            if cat_resp.status_code == 200:
                payload['categories'].append(category_id)
                record, created = ProductCategories.get_or_create(product_id=item_id,category_id=category_id)
                
                if created:
                    record.created = time.time()

            else:
                print(f'Category {category_id}')
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
        response_count = requests.get(f"{self.source_url}/tridge-products/_count",auth=self.basic_auth)
        print(response_count.content)
        
        if response_count.status_code == 200:
            count = json.loads(response_count.content)['count']
            elastic_count = math.ceil(count/10000)
            last_id  = ''
            
            for _ in range(elastic_count):
                if last_id:
                    search_data['search_after'] = [last_id]

                response = requests.get(f"{self.source_url}/tridge-products/_search",json=search_data,auth=self.basic_auth)
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
                            'name':item['name'],
                            'code':item['code'],
                            'image':item['image'],
                            'deleted':item['isDeleted'],
                            'categories':[],
                            'similar_products':[], # Check Later
                            'synonyms':self.add_synonyms(item),
                            'thumbnail':item['imageThumbnail'],
                            'description':item['description'],
                            'total_score':item['totalScore'],
                            'decayed_total':item['decayedTotalScore'],
                            'is_selectable':item['isSelectable'],
                            'countries':[row['code'] for row in item['countries']],
                            'created_at':int(datetime.strptime(item['createdAt'],"%Y-%m-%dT%H:%M:%S.%f%z").timestamp()),
                            'updated_at':int(datetime.strptime(item['updatedAt'],"%Y-%m-%dT%H:%M:%S.%f%z").timestamp()),
                            'source':{
                                'id':item['id'],
                                'source':'tridge'
                            }
                        }
                        
                        self.relate_categories(item,item_id,payload)
                        record.payload = payload
                        record.save()

                        response = requests.post(f"{self.dest_url}/product_types/_doc/{item_id}",json=payload)



