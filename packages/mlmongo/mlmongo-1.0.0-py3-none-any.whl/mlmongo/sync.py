import asyncio
from threading import Thread, Lock
import time
from typing import Any, Generator
from pydantic import BaseModel
from pymongo import MongoClient

    
class Mongoer:
    def __init__(self, url:str, default_db:str, default_col:str, default_key_name:str=None):
        self.url = url
        self.client=None
        self._lock = Lock()
        self.default_db=default_db
        self.default_col=default_col
        self.default_key_name=default_key_name
    
    def _getClient(self):
        client = MongoClient(self.url)
        return client
        
    def getConnect(self, db: str=None, col:str=None):
        if self.client is None: 
            with self._lock:
                self.client=self._getClient()
        return self.client[db or self.default_db][col or self.default_col]
    
    def client_auto_reset(self, s=600):
        def temp():
            while True:
                time.sleep(s)
                with self._lock:
                    self.client.close()
                    self.client = self._getClient()
        Thread(target=temp, daemon=True).start()
            
    def find(self, query: dict, db:str=None, col:str=None, cig:dict=None, default_id:int=0)->dict|None:
        if default_id==0: cig = {'_id':0, **cig} if cig else {'_id':0}
        result = self.getConnect(db,col).find_one(query or {}, cig or {})
        return result
    
    def find_all(self, query: dict=None, db:str=None, col:str=None, cig=None,
                 sort_map: dict[str, int]=None, skip:int=None, limit:int=None)->Generator[dict, None, None]:
        cursor  = self.getConnect(db,col).find(query,  {'_id':0, **cig} if cig else {'_id':0})
        if sort_map: cursor=cursor.sort(sort_map)
        if skip: cursor=cursor.skip(skip)
        if limit: cursor=cursor.limit(limit)
        for dt in cursor:
            yield dt
    
    def find_onekey_all(self, key:str, query: dict=None, db:str=None, col:str=None)->list:
        cursor  = self.getConnect(db,col).find(query, {'_id':0, key:1})
        return [dt[key] for dt in cursor]

    def find_onecol(self, key:str, query: dict=None, db:str=None, col:str=None, default=None):
        dt  = (self.getConnect(db,col).find_one(query, {'_id':0, key:1})) or {}
        return dt.get(key, default)
    
    def count(self, query: dict=None, db:str=None, col:str=None,)->int:
        return self.getConnect(db,col).count_documents(query)

    def update_one(self, query: dict, data: BaseModel|dict, db:str=None, col:str=None, upsert=True)->dict:
        return self.getConnect(db,col).update_one(query, {'$set': data.model_dump() if isinstance(data,BaseModel) else data}, upsert=upsert).raw_result
    
    def update_by_id(self, id:Any, data:BaseModel|dict, db:str=None, col:str=None, upsert=True, key_name:str=None):
        assert key_name or self.default_key_name, '没有设置key_name'
        return self.update_one({key_name or self.default_key_name:id}, data, db=db, col=col, upsert=upsert)   
    
    def update(self, query: dict, dt: dict, db:str=None, col:str=None)->dict:
        return self.getConnect(db,col).update_many(query, {'$set': dt}).raw_result
    
    def del_field(self, query: dict, *fields: str, db:str=None, col:str=None)->dict:
        assert fields
        return self.getConnect(db,col).update_many(query, {'$unset':{f:'' for f in fields}}).raw_result
    
    def pop(self, query: dict,db:str=None, col:str=None)->dict|None:
        try:
            dt = self.getConnect(db,col).find_one_and_delete(query) or {}
            dt.pop('_id', None)
            return dt
        except asyncio.exceptions.CancelledError as e:
            raise e
        except Exception as e:
            return None
    
    def insert(self, data: BaseModel|dict, db:str=None, col:str=None, **kwargs):
        return self.getConnect(db,col).insert_one(data.model_dump( **kwargs) if isinstance(data, BaseModel) else data)
    
    def insert_many(self, datas: list[BaseModel|dict], db:str=None, col:str=None, **kwargs):
        if not datas: return None
        datas = [(data.model_dump(**kwargs) if isinstance(data, BaseModel) else data) for data in datas]
        return self.getConnect(db,col).insert_many(datas)
    
    def delete(self, query: dict, db:str=None, col:str=None)->dict:
        return self.getConnect(db,col).delete_many(query).raw_result
    
    def getChild(self, default_col:str)->'MongoerChild':
            return MongoerChild(self, default_col)

class MongoerChild(Mongoer):
    def __init__(self, mer: Mongoer, default_col:str):
        self._amer=mer
        self.client=mer.client
        self.default_db=mer.default_db
        self.default_col=default_col
        self.default_key_name=mer.default_key_name
        self._lock = mer._lock
    
    def _getClient(self):
        self._amer.client = self._amer._getClient()
        return self._amer.client
        
    def getConnect(self, db: str=None, col:str=None):
        if self.client is None: self.client=self._getClient()
        return self.client[db or self.default_db][col or self.default_col]
    
    def client_reset(self):
        raise ValueError('子类对象不能调用该方法')
            
    def client_auto_reset(self, **_):
        raise ValueError('子类对象不能调用该方法')