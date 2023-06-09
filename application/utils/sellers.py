import os
import httpx
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

class SearchSellers:

    def __init__(self,page,limit,category,product_id) -> None:
        self.page  = page
        self.limit = limit
        self.category = category
        self.product_id = product_id
        self.url  = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    async def get_category_products(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/product_types/_search",json={
                "query": {"terms": {"categories": [self.category]}},
                "stored_fields": [],
                "size":1000,
                "sort": [{"decayed_total": "desc"}]
            },auth=self.basic_auth)

            return [rec['_id'] for rec in response.json()['hits']['hits']]
        
    async def get_supplying_products(self,items):
        products = []
        {products.extend(item['supplying_products']) for item in items}
        products = list(set(products))
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/product_types/_search",json={
                "_source": {"includes": ["id","name","code"]},
                "query": {"terms": {"id": products}}
            },auth=self.basic_auth)

            return {rec['_source']['id']:rec['_source'] for rec in response.json()['hits']['hits']}
        

    async def get_json(self):
        payload = {
            "from":self.page * self.limit,
            "size":self.limit,
            "_source": {"exclude": ['source','certificates']},
            "sort": [
                {"adjusted_supplier_directory_score": "desc"},
                {"profile_score": "desc"},
                {"code.keyword": "asc"}
            ]
        }

        if self.product_id:
            payload["query"] = {"terms": {"supplying_products": [self.product_id]}}

        elif self.category:
            category_products = await self.get_category_products()
            payload["query"] = {"terms": {"supplying_products": category_products}}
        

        return payload

    async def call(self):
        async with httpx.AsyncClient() as client:
            json_payload = await self.get_json()
            response = await client.post(f"{self.url}/sellers/_search",json=json_payload,auth=self.basic_auth)
        
        hits = response.json()['hits']['hits']
        hits = [hit['_source'] for hit in hits]

        if not hits:
            raise HTTPException(404,'Sellers not found')
            
        products = await self.get_supplying_products(hits)
        for hit in hits:
            hit['supplying_products'] = [products[item] for item in products if item in hit['supplying_products']]

        return hits
    

class GetSeller:

    def __init__(self,code) -> None:
        self.code = code
        self.url  = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    async def get_supplying_products(self,source):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/product_types/_search",json={
                "_source": {"includes": ["id","name","code"]},
                "query": {"terms": {"id": source['supplying_products']}}
            },auth=self.basic_auth)

            return {rec['_source']['id']:rec['_source'] for rec in response.json()['hits']['hits']}
        
 
    async def call(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/sellers/_search",json={
            "query": {
                "term": {
                "code.keyword": {"value": self.code}}
            }},auth=self.basic_auth)

        if response.status_code == 200:
            hits = response.json()['hits']['hits']
            if not hits:
                raise HTTPException(404,'Seller not found')
            
            source = hits[0]['_source']
            if source.get('supplying_products'):
                products = await self.get_supplying_products(source)
                source['supplying_products'] = [products[item] for item in products if item in source['supplying_products']]
                
            return source
        
        raise HTTPException(500,'Service unavailable')