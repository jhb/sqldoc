from sqldoc import config
from nestedtext import loads, dumps, NestedTextError
from pprint import pformat

sqldoc = config.sqldoc
sg = config.sg
reg = config.r

def get_title(doc):
    if 'edge' in reg.find_schemata(doc):
        sourcetitle = get_title(sqldoc.read_doc(doc['_source']))
        targettitle = get_title(sqldoc.read_doc(doc['_target']))
        return f"{sourcetitle} -{doc.get('relation','')}-> {targettitle}"



    for k in ['title','name','_docid']:
        if k in doc:
            return doc[k]


def get_routes(request,obj):
    routes = []
    for route in request.app.routes:
        if not "GET"in route.methods:
            continue
        if set(getattr(route,'tags',[])).intersection(obj['_schemata']):
            routes.append(route)
    print('get routes', routes)
    return routes



helpers = dict(dumps=dumps,
               get_title=get_title,
               pformat=pformat,
               reg=reg,
               get_routes = get_routes)