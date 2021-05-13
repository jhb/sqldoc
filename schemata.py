registry = {}

def add(key,obj):
    if key in registry:
        raise Exception('key taken')
    if isinstance(obj,(list,tuple,dict)):
        obj = {k:registry[k] for k in obj}
    registry[key]=obj

class Field:
    ...

class Schema:
    ...


add('_docid',Field())
add('_source',Field())
add('_target',Field())
add('edge',dict(_source='',
                _target=''))

from comparisons import part_of_full

edge = {'_docid': 'c556a24098af4be69871d5e26cde5664',
 '_source': 'ea7a97d43d5b4846ba2bf707b775ff4d',
 '_target': '7518d0c8f58040e8934c49af189c28c5',
 'relation': 'likes'}

print(part_of_full(registry['edge'],edge))
print(registry['edge'])