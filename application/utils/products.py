import os
import json
import httpx
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
from application.helpers.options import countries

class SearchProducts:

    def __init__(self,page,limit,query,category) -> None:
        self.page  = page
        self.limit = limit
        self.query = query
        self.category = category
        self.url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    def get_json(self):
        payload = {
            "from":self.page * self.limit,
            "size":self.limit,
            "query": {
                "bool": {
                    "filter": {
                        "bool": {
                            "must": [
                                {"term": {"is_selectable": True}}
                            ]
                        }
                    },
                    "must": {"exists": {"field": "image"}}
                }
            },
            "_source": {"exclude": ['source','decayed_total','total_score',
                    'categories','similar_products','deleted']},
            "sort": [{"decayed_total": "desc"}]
        }

        if self.query:
            payload['query']['bool']['minimum_should_match'] = 1
            payload['query']['bool']['should'] = [
                {"term": {"name": self.query}},
                {"term": {"synonyms.name": self.query}}
            ]

        if self.category:
            payload['query']['bool']['filter']['bool']['must'].append({"terms": {"categories": [self.category]}})

        print(json.dumps(payload))
        return payload

    async def call(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/product_types/_search",json=self.get_json(),auth=self.basic_auth)
        
        hits = response.json()['hits']['hits']
        hits = [hit['_source'] for hit in hits]

        return hits
    

class GetProduct:

    def __init__(self,item_id) -> None:
        self.item_id = item_id
        self.url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    async def get_categories(self,categories):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/categories/_search",json={
                "_source": {"includes": ["id","name","code"]},
                "query": {
                    "terms": {"id": categories}
                }
            },auth=self.basic_auth)

        if response.status_code == 200:
            return [rec['_source'] for rec in response.json()['hits']['hits']]

        raise HTTPException(500,'Internal Server Error')

 
    async def call(self):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.url}/product_types/_doc/{self.item_id}",auth=self.basic_auth)

        if response.status_code == 200:
            source = response.json()['_source']
            source['countries'] = [countries[item] for item in source['countries']]
            source['categories'] = await self.get_categories(source['categories'])

            return source
        
        raise HTTPException(500,'Internal Server Error')
        
