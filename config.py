import mariadb
from sqldoc_mariadb import Sqldoc
from sqlgraph import SqlGraph


conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",
            port=3306)

sqldoc: Sqldoc = None
sg: SqlGraph = None
