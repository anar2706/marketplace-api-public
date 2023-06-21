
import os
import httpx
from requests.auth import HTTPBasicAuth

class AllCategories:

    def __init__(self) -> None:
        self.url   = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])


    async def call(self):
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.url}/categories/_search",json={
                "from":0,
                "size":50,
                "query": {
                    "bool": {
                        "must": [
                            {"range": {"selectable_product_count": {"gt": 0}}},
                            {"term": {"depth": {"value": "2"}}}
                        ]
                    }
                },
                "_source": {
                    "exclude": ['source']
                },
                "sort": [{"selectable_product_count": "desc"}]
            })

        hits = response.json()['hits']['hits']
        hits = [hit['_source'] for hit in hits]

        return hits