import os
import httpx
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
from models import FavoriteSellers

class GetFavorites:

    def __init__(self,page,limit,user_id) -> None:
        self.page  = page
        self.limit = limit
        self.user_id = user_id
        self.url  = os.environ['ELASTIC_URL']
        self.basic_auth = HTTPBasicAuth(os.environ['ELASTIC_USER'],os.environ['ELSATIC_PASSWORD'])

    
    def get_favorites(self):
        records =  FavoriteSellers.select(FavoriteSellers.seller_id).where(FavoriteSellers.user_id==self.user_id) \
            .order_by(FavoriteSellers.created.desc()).dicts()
        
        return [rec['seller_id'] for rec in records]


    async def call(self):
        async with httpx.AsyncClient() as client:
            json_payload = {
                "query": {
                    "terms": {"id": self.get_favorites()}
                }
            }

            response = await client.post(f"{self.url}/sellers/_search",json=json_payload,auth=self.basic_auth)

        hits = response.json()['hits']['hits']
        hits = [hit['_source'] for hit in hits]
        return hits

        