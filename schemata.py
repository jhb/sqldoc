from pprint import pprint


registry = {}

def add(key,obj):
    print(key)
    if key in registry:
        raise Exception('key taken')
    if isinstance(obj,(list,tuple,dict)):
        newobj = {}
        for k,v in obj.items():
            if type(v) is type:
                newobj[k]=v
            else:
                newobj[k]=registry[v]
        obj = newobj
    registry[key]=obj

def walk(obj, keyf, valf, keyr=None, valr=None, path='', separator='.'):
    if keyr is None: keyr = {}
    if valr is None: valr = {}
    object_type = type(obj)
    if object_type==dict:
        for k,v in obj.items():
            subpath = path and path+'.'+k or k
            keyr[subpath]=keyf(subpath,k,v,separator)
            walk(v, keyf, valf, keyr, valr, subpath, separator)
    elif object_type in [list,tuple]:
        for i,v in enumerate(obj):
            subpath= path and path+'.'+str(i) or str(i)
            walk(v, keyf, valf, keyr, valr, subpath, separator)
    else:
        valr[path]=valf(path,obj,separator)
    return keyr,valr

def validate_value(path,value,separator='.'):
    name = path.split(separator)[-1]
    if name in registry:
        print('vv',path, name,registry[name],value)
    else:
        return None

def validate_key(path,key,value,separator='.'):
    name = path.split(separator)[-1]
    if name in registry:
        print('kv', path, name, key, registry[name], value)
    else:
        return None


class Field:
    ...

class Schema:
    ...



if __name__ == '__main__':

    add('_docid',str)
    add('_source',str)
    add('_target',str)
    add('content_type',str)
    add('content_data',str)
    add('content',dict(content_type='content_type',
                       content_data='content_data'))
    add('edge',dict(_docid='_docid',
                    _source=str,
                    _target=str,
                    content='content'))

    from comparisons import part_of_full

    edge = {'_docid': 'c556a24098af4be69871d5e26cde5664',
     '_source': 'ea7a97d43d5b4846ba2bf707b775ff4d',
     '_target': '7518d0c8f58040e8934c49af189c28c5',
     'relation': 'likes',
     'content': {'content_type':'text',
                 'content_data':'bla bla'
                 }}

    edgetype = registry['edge']
    pprint(edgetype)
    pprint(edge)
    print(part_of_full(registry['edge'],edge,True))
    keyr,valr = walk(edge, validate_key, validate_value)
    print(keyr)
    print(valr)