import asyncio
from typing import Any,AsyncGenerator
from pydantic import BaseModel
try:
    from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
except:
    raise ModuleNotFoundError('pip install motor')


def _limit(afunc):
    async def _main(self:'AMongoer', *args, **kwargs):
        async with self._sem:
            return await afunc(self, *args, **kwargs)
    
    return _main

def _limit_iterator(afunc):
    async def _main(self:'AMongoer', *args, **kwargs):
        async with self._sem:
            async for result in afunc(self, *args, **kwargs):
                yield result
    
    return _main

class AMongoer:
    def __init__(self, url:str, default_db:str, default_col:str, default_key_name:str=None, async_limit:int=300):
        self.url = url
        self.client=None
        self.default_db=default_db
        self.default_col=default_col
        self.default_key_name=default_key_name
        self._sem = asyncio.BoundedSemaphore(async_limit)
    
    def _getClient(self):
        client = AsyncIOMotorClient(self.url)
        client.get_io_loop = asyncio.get_running_loop
        return client
        
    def getConnect(self, db: str=None, col:str=None)->AsyncIOMotorCollection:
        if self.client is None: self.client=self._getClient()
        return self.client[db or self.default_db][col or self.default_col]
    
    async def client_reset(self):
        if self.client: self.client.close()
        self.client = self._getClient()
            
    async def client_auto_reset(self, s=600):
        while True:
            await asyncio.sleep(s)
            self.client.close()
            self.client = self._getClient()
        
    @_limit
    async def find(self, query: dict, db:str=None, col:str=None, cig:dict=None, default_id:int=0)->dict|None:
        if default_id==0: cig = {'_id':0, **cig} if cig else {'_id':0}
        result = await self.getConnect(db,col).find_one(query or {}, cig or {})
        return result

    @_limit_iterator 
    async def find_all(self, query: dict=None, db:str=None, col:str=None, cig=None,
                        sort_map: dict[str, int]=None, skip:int=None, limit:int=None)->AsyncGenerator[dict, None]:
        cursor  = self.getConnect(db,col).find(query,  {'_id':0, **cig} if cig else {'_id':0})
        if sort_map: cursor=cursor.sort(sort_map)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        async for dt in cursor:
            yield dt
            
    @_limit
    async def find_onekey_all(self, key:str, query: dict=None, db:str=None, col:str=None)->list:
        cursor  = self.getConnect(db,col).find(query, {'_id':0, key:1})
        return [dt[key] async for dt in cursor]
    
    @_limit
    async def find_onecol(self, key:str, query: dict, db:str=None, col:str=None, default=None):
        dt  = (await self.getConnect(db,col).find_one(query, {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    @_limit
    async def count(self, query: dict=None, db:str=None, col:str=None)->int:
        return await self.getConnect(db,col).count_documents(query)
    
    @_limit                                           
    async def update_one(self, query: dict, data: BaseModel|dict, db:str=None, col:str=None, upsert=True)->dict:
        return (await self.getConnect(db,col).update_one(query, {'$set': data.model_dump() if isinstance(data,BaseModel) else data}, upsert=upsert)).raw_result

    @_limit
    async def update_by_id(self, id:Any, data:BaseModel|dict, db:str=None, col:str=None, upsert=True, key_name:str=None):
        assert key_name or self.default_key_name, '没有设置key_name'
        return await self.update_one({key_name or self.default_key_name:id}, data, db=db, col=col, upsert=upsert)   
 
    @_limit
    async def update(self, query: dict, dt:dict, db:str=None, col:str=None)->dict:
        return (await self.getConnect(db,col).update_many(query, {'$set': dt})).raw_result

    @_limit
    async def del_field(self, query: dict, *fields: str, db:str=None, col:str=None)->dict:
        assert fields
        return (await self.getConnect(db,col).update_many(query, {'$unset':{f:'' for f in fields}})).raw_result
    
    @_limit
    async def pop(self, query: dict,db:str=None, col:str=None)->dict|None:
        try:
            dt = (await self.getConnect(db,col).find_one_and_delete(query)) or {}
            dt.pop('_id', None)
            return dt
        except asyncio.exceptions.CancelledError as e:
            raise e
        except Exception as e:
            return None

    @_limit
    async def insert(self, data: BaseModel|dict, db:str=None, col:str=None, **kwargs):
        return await self.getConnect(db,col).insert_one(data.model_dump( **kwargs) if isinstance(data, BaseModel) else data)

    @_limit
    async def insert_many(self, datas: list[BaseModel|dict], db:str=None, col:str=None, **kwargs):
        if not datas: return None
        datas = [(data.model_dump(**kwargs) if isinstance(data, BaseModel) else data) for data in datas]
        return await self.getConnect(db,col).insert_many(datas)

    @_limit
    async def delete(self, query: dict, db:str=None, col:str=None)->dict:
        return (await self.getConnect(db,col).delete_many(query)).raw_result
    
    def getChild(self, default_col:str)->'AMongoerChild':
        return AMongoerChild(self, default_col)
    
class AMongoerChild(AMongoer):
    def __init__(self, amer: AMongoer, default_col:str):
        self._amer=amer
        self.client=amer.client
        self.default_db=amer.default_db
        self.default_col=default_col
        self.default_key_name=amer.default_key_name
        self._sem = amer._sem
    
    def _getClient(self):
        self._amer.client = self._amer._getClient()
        return self._amer.client
        
    def getConnect(self, db: str=None, col:str=None)->AsyncIOMotorCollection:
        if self.client is None: self.client=self._getClient()
        return self.client[db or self.default_db][col or self.default_col]
    
    async def client_reset(self):
        raise ValueError('子类对象不能调用该方法')
            
    async def client_auto_reset(self, **_):
        raise ValueError('子类对象不能调用该方法')