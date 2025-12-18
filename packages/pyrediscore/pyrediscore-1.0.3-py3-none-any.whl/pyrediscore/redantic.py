from shutil import ExecError
from pydantic import BaseModel
import redis
import json
from typing import Optional
import inspect, re

from .utils import chunkify

MDEL_MAX_BATCH_SIZE = 10000
MADD_MAX_BATCH_SIZE = 10000

class StoreValidationError(Exception):
	pass
class KeyStoreError(Exception):
    pass
class StoreGetError(Exception):
    pass
class StoreKeyNotFound(Exception):
    pass
class StoreMgetError(Exception):
    pass
class StoreWipeError(Exception):
    pass
class RedisScanError(Exception):
    pass
class StoreKeyError(Exception):
    pass

valid_key = re.compile(
    r'^[a-zA-Z0-9_\.]+$'
)
def key_to_str(f):
    def wrapped(self, key, *args):
        try : 
            k = str(key)
            assert valid_key.fullmatch(k)
        except Exception :
            raise StoreKeyError(f"Cant properly stringify supplied key {key}")
        _ = f(self, k, *args)
        return _
    return wrapped

def validate_object(f):
    def wrapped(self, *args, **kwargs):
        if 'skip_check' in kwargs:
            if kwargs['skip_check']:
                _ = f(self, *args, **kwargs)
                return _

        if not isinstance(args[0], BaseModel):
            try :                
                for o in args[0]:
                    if not isinstance(o, BaseModel):
                        raise StoreValidationError(f"{o} is not a Pydantic Model instance")
            except TypeError:                
                raise StoreValidationError(f"{args[0]} is not a Pydantic Model instance")
        _ = f(self, *args, **kwargs)
        return _
    return wrapped

def assert_registration(f):
    def wrapped(self, *args, **kwargs):
        if 'skip_check' in kwargs:
            if kwargs['skip_check']:                
                _ = f(self, *args, **kwargs)
                return _
        
        if not isinstance(args[0], BaseModel):
            for o in args[0]:
                cls_name = type(o).__name__
                if not cls_name in self.models:
                    raise StoreValidationError(f"{cls_name} is not a registred Pydantic Model instance")
        else:
            cls_name = type(args[0]).__name__
            if not cls_name in self.models:
                raise StoreValidationError(f"{cls_name} is not a registred Pydantic Model instance")
        _ = f(self, *args, **kwargs)
        return _
    return wrapped

def _assert_model(model, field):
    if not issubclass(model, BaseModel):
        raise TypeError("Provided ORM is not a Pydantic BaseModel class")
    if field not in model.__fields__:
        raise ValueError(f"Provided identifier field {field} is not found in Pydantic BaseModel")
    return True

def assert_model_schema_eq(model, schema):
    if model.__fields__ != schema.__fields__:
        raise TypeError(f"Schema instance doesnot match Model class {model.__fields__} VS {schema.__fields__}")
    return True

class RedisStoreCreationError(Exception):
    pass

class RedisStore():
    def __init__(self, host:str, port:int, connection_check=True):
        self.host = host
        self.port = port
        self.db_num = 0
        self.models = {}
        self.connection = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        if connection_check:
            try:
                self.connection.ping()
            except Exception as e:
                raise RedisStoreCreationError(str(e))
                
    def load_model(self, model:BaseModel, uid:str):
        _assert_model(model, uid)
        self.models[model.__name__] = (model, uid)

    def generate_key(self, o):
        cls_name = type(o).__name__       
        uid = self.models[cls_name][1]
        _k = getattr(o, uid)
        return  f"{cls_name}:{_k}"

    @validate_object
    @assert_registration
    def add(self, object_to_store, replace=False):
        store_key = self.generate_key(object_to_store)
        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        if r.exists(store_key):
            if not replace:
                raise KeyStoreError(f"Key {store_key} already exists")
            self.mdel(store_key)
        r.set(store_key, json.dumps(object_to_store.dict()))
        return True
    
    def _scan(self, pattern):
        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        hit = [ hitKey.decode()\
                for hitKey in r.scan_iter(match=pattern, count=None, _type=None)\
              ]
        if not hit:
            raise RedisScanError(f"Following {pattern} scan result emtpy")
        return hit
    
    @assert_registration
    def _get_matching_model(self, obj):
        return self.models[ type(obj).__name__ ]

    def _get_fuzzy_key(self, uid:str):
        pattern=f"*:{uid}"
        try :
            keys_found = self._scan(pattern)
        except RedisScanError:
            raise StoreKeyNotFound(f"No such key {uid}")

        if len(keys_found) > 1:
            raise StoreGetError(f"Asked key {uid} has ambigious hits {keys_found} ")
        (model_name,_uid) = keys_found[0].split(':')
        return (model_name, _uid)
    def wipe(self):
        if not self.models:
            raise StoreWipeError("Not model registred, nothing to wipe")
        report = {}

        for ns in self.models:
            n_del = self._wipe_ns(ns)
            report[str(ns)] = n_del
        return report
    
    def _wipe_ns(self, ns):
        n_del = 0         
        try :
            key_to_del = self._scan(f"{ns}:*")
            n_del = self.mdel(*key_to_del)                   
        except RedisScanError as e:
            print(f"Nothing to wipe under {ns}:*")
        return n_del

    def wipe_ns(self, model_to_wipe)->int:
        for ns, model in self.models.items():          
            if model[0] == model_to_wipe:# Real equality check     
                n_del = self._wipe_ns(ns)       
                return n_del
        raise StoreWipeError(f"{model_to_wipe} is not a registred  model, no ns to wipe")        
    
    def delete(self, k, model:Optional[BaseModel]=None):
        ns = model.__name__ if model else self._get_fuzzy_key(k)[0]
        k_to_del = f"{ns}:{k}"
        #print("->", k_to_del)
       

        _ = self.mdel(k_to_del)
        return _ == 1

    def mdel(self, *k_list)->int:
        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        t_del = 0
        for chunk in chunkify(k_list):
            t_del += r.delete(*chunk)
        return t_del

    @key_to_str
    def get(self, _key:str, model:Optional[BaseModel] = None):
        if model is None:
            model_name = self._get_fuzzy_key(_key)[0]
        else:
            assert(issubclass(model, BaseModel))
            model_name = model.__name__
        
        key = f"{model_name}:{_key}"

        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        _d = r.get(key)
        if not _d:
            raise StoreKeyNotFound(f"No such key {key}")
        try :
            (Model, _) = self.models[model_name]
            o = Model.parse_raw(_d)
            return o
        except KeyError:
            raise StoreGetError(f"Asked key {_key} found but bound model {model_name} not registred")

    @validate_object
    @assert_registration
    def madd(self, iter_to_store, skip_check=False): # skip_check for mass bulk perf ?
        r = self.connection
        t_len = 0
        for chunk in chunkify(iter_to_store):
            _ = { f"{self.generate_key(o)}" : json.dumps(o.dict())\
                  for o in chunk\
                }
            t_len += len(chunk)   
            r.mset(_)

        return t_len

    def mget(self, key_iter, model:Optional[BaseModel]=None):
        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        if model:
            if not issubclass(model, BaseModel):
                raise StoreMgetError(f"The type you ask to limit search space is not a Pydantic model {model}")
            d = r.mget([f"{model.__name__}:{k}" for k in key_iter])   
            #print(d)       
            return [ model.parse_raw(_) if not _ is None else None for _ in d  ]

        else:
            full_keys = []
            models    = []
            try :
                for k in key_iter:
                    model_name = self._get_fuzzy_key(k)[0]
                    full_keys.append(f"{model_name}:{k}")
                    models.append(self.models[model_name][0])
            except KeyError:
                raise StoreMgetError(f"Asked key {k} found but bound model {model_name} not registred")
            d = r.mget(full_keys)
            return [ cls.parse_raw(_) if not _ is None else None for cls, _ in zip(models, d) ]
                
    def list_key(self, pattern:Optional[str]=None, model:Optional[BaseModel] = None, skip_prefix=False):
        _pattern = '*' if pattern is None else pattern
        _ns      = '*' if model is None else model.__name__
        
        #r = redis.Redis(host=self.host, port=self.port, db=self.db_num)
        r = self.connection
        for hitKey in r.scan_iter(match=f"{_ns}:{_pattern}", count=None, _type=None):
            hitKey = hitKey.decode()
            yield hitKey if not skip_prefix else re.sub(r'^([^:]+:)', '', hitKey)