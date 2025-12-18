import redis
import json, sys

from decorator import decorator

from marshmallow import Schema, fields, ValidationError


HOST = 'localhost'
PORT = 6379

class ConnectorSchema(Schema):
    host = fields.Str(missing="localhost")
    port = fields.Int(missing=6379)

def setDatabaseParameters(**kwargs):
    global HOST, PORT
    
    scheme = ConnectorSchema()
    data = scheme.load(kwargs)

    HOST = data['host']
    PORT = data['port']
    print(f"Set Database parameters to {HOST}:{PORT}")
    

@decorator
def connect(fn, *args, **kwargs):
    r = redis.Redis(host=HOST, port=PORT, db=0)
    return fn(r, *args, **kwargs)

@connect
def wipe(r, *args, **kwargs):
    print(f"Wiping redis stores content")
    r.flushdb()

@decorator
def delete(fn, r, *args, ignore=False, **kwargs):
    miss = []
    keys = fn(*args, **kwargs)
    for key in keys:
        _ = r.delete(key)       
        if int(str(_)) != 1:
            miss.append(key)
    if miss and not ignore:
        raise KeyError(f"{miss} to delete elements not found in redis store")
    return len(keys) - len(miss)
"""storeMany
mapping that is expected to be a dict. For MSET and MSETNX, the dict is a mapping of key-names -> values. For ZADD, the dict is a mapping of element-names -> score.

MSET, MSETNX and ZADD now look like:

def mset(self, mapping):

"""

""" pipelineStoreMany
https://stackoverflow.com/questions/22210671/redis-python-setting-multiple-key-values-in-one-operation
"""
@decorator
def store(fn, r, *args, **kwargs):
    #print(args)
    key, obj = fn(*args, **kwargs)
    if r.exists(key):
        raise KeyError(f"Store error: {key} already exists in store")

    r.set(key, json.dumps(obj))

@decorator
def storeMany(fn, r, *args, **kwargs):
    data = fn(*args, **kwargs)
    _ = { k:json.dumps(o) for k,o in data.items() }
    r.mset(_)

@decorator
def get(fn, r, *args, **kwargs):
    key, _deserializer = fn(*args, **kwargs)
    _ = r.get(key)

    if not _:
        raise KeyError(f"No key {key} found in store")

    if 'rawDecode' in kwargs:
        if kwargs['rawDecode']:
            return _.decode()
    
    if 'raw' in kwargs:    
        if kwargs['raw']:
            return _

    d = json.loads(_)
    return d \
        if _deserializer is None \
        else _deserializer(d)

@decorator
def mget(fn, r, *args, **kwargs):
    keyList, _deserializer = fn(*args, **kwargs)
    _d = r.mget(keyList)

    if kwargs['raw']:
        return [ _.decode() if _ else None for _ in _d ] # decode() element here

    d = [ json.loads(_) if _ else None for _ in _d ]
    if _deserializer is None:
        return d
    
    return [ _deserializer(_) if _ else None for _ in d ]
    
@decorator
def listKey(fn, r, *args, **kwargs):
    _pattern, _prefix = fn(*args, **kwargs)
    #print("###", _pattern, _prefix)
    for hitKey in r.scan_iter(match=_pattern, count=None, _type=None):
        hitKey = hitKey.decode()
        yield hitKey if kwargs['prefix'] else hitKey.replace(_prefix, '')
