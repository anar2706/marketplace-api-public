import os
import httpx
from models import Supplies
from requests.auth import HTTPBasicAuth
from application.utils.general import timefn

class GetSellersSupplies:

    def __init__(self,page,limit,seller_code,product_id) -> None:
        self.page  = page
        self.limit = limit
        self.seller_code = seller_code
        self.product_id  = product_id
        self.url  = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    async def get_product_types(self,product_ids):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/product_types/_search/",json={
                "_source": {"includes": ["id","name","code","image"]},
                "query": {
                    "terms": {"id": product_ids}
                }
            })
            
            data = {item['_source']['id']: item['_source'] for item in response.json()['hits']['hits']}
            return data
        
    async def get_attributes(self,attributes):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/attributes/_search/",json={
                "_source": {"includes": ["id","name","verbose_name"]},
                "query": {
                    "terms": {"id": attributes}
                }
            })
            
            data = {item['_source']['id']: item['_source'] for item in response.json()['hits']['hits']}
            return data

    async def get_supplies(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/sellers/_search",json={
                "query": {
                    "term": {"code.keyword": {"value": self.seller_code}}
                }
            })
            return response.json()['hits']['hits'][0]['_source']['supplies']

    async def get_json(self):
        supply_ids = await self.get_supplies()

        payload = {
            "from":self.page * self.limit,
            "size":self.limit,
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [{"terms": {"id": supply_ids}}]
                        }
                    }
                }
            },
            "_source": {"exclude": ['source']},
            "sort": [
                {"name.keyword": "asc"}
            ]
        }

        if self.product_id:
            payload['query']['bool']['filter']['bool']['must'].append({"term": {"product_id": self.product_id}})

        print(payload)
    
        return payload

    async def call(self):
        async with httpx.AsyncClient() as client:
            json_payload = await self.get_json()
            response = await client.post(f"{self.url}/supplies/_search",json=json_payload,auth=self.basic_auth)
        
        hits = response.json()['hits']['hits']
        hits = [hit['_source'] for hit in hits]
        
        products   = await self.get_product_types([item['product_id'] for item in hits])
        
        attribute_ids = []
        for item in hits:
            attribute_ids.extend(item['attributes'])

        attributes = await self.get_attributes(list(set(attribute_ids)))
        
        for hit in hits:
            hit['attributes'] = [attributes[item] for item in attributes if item in hit['attributes']]
            hit['product'] = products[hit['product_id']]
            hit.pop('product_id',None)            

        return hits
    
