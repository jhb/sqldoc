import mariadb
from sqldoc_mariadb import Sqldoc
from sqlgraph import SqlGraph
from schemata import Registry


conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",
            port=3306)

sqldoc: Sqldoc = None
sg: SqlGraph = None
delimiter = '.'

r = Registry()
r.add('_docid', str)
r.add('_source', str)
r.add('_target', str)
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
