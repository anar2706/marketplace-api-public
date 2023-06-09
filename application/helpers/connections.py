import os
import redis.asyncio as redis_async
import redis as redis_sync

class Redis_Con:

    @property
    def red(self):
        return redis_async.StrictRedis(
            host=os.environ['REDIS_HOST'], 
            password=os.environ['REDIS_PASSWORD'],
            port=6379, 
            db=1
        )
    


class Redis_Con_Sync:

    @property
    def red(self):
        return redis_sync.StrictRedis(
            host=os.environ['REDIS_HOST'], 
            password=os.environ['REDIS_PASSWORD'],
            port=6379, 
            db=1
        )