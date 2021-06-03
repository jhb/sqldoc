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
        if not (hasattr(route,'methods') and  "GET" in route.methods):
            continue
        print('tags',getattr(route,'tags',[]))
        if set(getattr(route,'tags',[])).intersection(obj.get('_schemata',{'node'})):
            routes.append(route)
    return routes


def extra_schema(doc):
    try:
        if type(doc)==str:
            doc=loads(doc)
        existing = reg.find_schemata(doc)
        possible = reg.schemata
        extra = list(set(possible) - set(existing))
    except Exception:
        extra = []
    return extra


helpers = dict(dumps=dumps,
               get_title=get_title,
               pformat=pformat,
               reg=reg,
               sqldoc = sqldoc,
               get_routes = get_routes,
               extra_schema = extra_schema)