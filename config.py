import mariadb
from sqldoc.sqldoc_mariadb import Sqldoc, InvalidReference
from sqldoc.sqlgraph import SqlGraph
from sqldoc.schemata import Registry


conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",
            port=3306)

sqldoc: Sqldoc = None
sg: SqlGraph = None
delimiter = '.'

view_registry = {}

def register_view(view,schemata):
    if not isinstance(schemata,(list,tuple)):
        schemata = (schemata,)
    for schemaname in schemata:
        registered = view_registry.setdefault(schemaname,[])
        if view not in registered:
            registered.append(view)

def valid_reference(value):
    if not sqldoc.read_doc(value):
        raise InvalidReference(value)
    return value



r = Registry()
r.add('_docid', str)
r.add('_source', valid_reference)
r.add('_target', valid_reference)
r.add('name', str)
r.add('age', int)
r.add('street', str)
r.add('city', str)
r.add('_schemata',tuple)
r.add('address', ('street', 'city'))
r.add('person', ('name', 'age'))
r.add('content_type', str)
r.add('content_data', str)
r.add('content', ('content_type', 'content_data'))
r.add('edge', ('node', '_source', '_target'))
r.add('node',('_docid',))
