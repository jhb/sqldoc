import math
import random
from dateutil.parser import parse
import uuid
import itertools
import mariadb


def walk_keys(obj, delimeter='.',path = ""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from walk_keys(v, delimeter,path + delimeter + k if path else k)
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            s = str(i)
            yield from walk_keys(v, delimeter, path + delimeter+s if path else s)
    else:
        yield path,obj

class Sqldoc:

    def __init__(self, conn, do_setup=False):
        self.conn = conn
        self.autocommit = False
        if do_setup:
            self.setup_tables()

        self.to_sql_map = dict( str=str,
                                int=int,
                                float=float,
                                dt=parse,
                                text=str,
                                blob=self.to_blob)

    def commit(self):
        self.conn.commit()

    def cursor(self):
        return self.conn.cursor()

    def setup_tables(self):
        setup = [
                'drop table if exists search',

                """
                create table search
                (
                   `id`    integer primary key auto_increment,
                   `oid` varchar(256) not null,
                   `path`  varchar(256) not null,
                   `rev`   varchar(256) not null,
                   `name`   varchar(256) not null,
                   `str` varchar(256),
                   `int` integer,
                   `float` float,
                   `dt` datetime,
                   `text` text,
                   `blob` blob,
                   `type` char
   
                    );""",

        ]
        cur = self.cursor()
        for s in setup:
            cur.execute(s)

    def setup_indexes(self):
        finish = [
                "create index if not exists `docid` on search(`docid`);",
                "create index if not exists `path` on search (`path`);",
                "create index if not exists `rev` on search (`rev`);",
                "create index if not exists `name` on search (`name`);",
                "create index if not exists `str` on search (`str`);",
                "create index if not exists `int` on search (`int`);",
                "create index if not exists `float` on search (`float`);",
                "create index if not exists `dt` on search (`dt`);",
                "create index if not exists `type` on search (`type`);",
                "create fulltext index if not exists `text` on search (`text`);",

        ]
        cur = self.cursor()
        for s in finish:
            cur.execute(s)

    def to_blob(self,value):
        if len(value)>1024:
            return value
        else:
            return None

    def to_sql(self):
        return

    def store_obj(self,obj,oid=None):
        if oid is None:
            oid = uuid.uuid4().hex
        rows = []
        data = []
        for key,value in itertools.chain(walk_keys(obj),(('_oid',oid),)):
            row = {'oid': oid,
                   'path': key,
                   'rev': '.'.join(reversed(key.split('.'))),
                   'name': key.split('.')[-1]}
            for fname,f in self.to_sql_map.items():
                try:
                    v = f(value)
                except (ValueError, TypeError):
                    v = None
                row[fname]=v
            row['type'] = str(type(value))[8]
            rows.append(row)
            data.append(tuple(row.values()))
        cur = self.cursor()
        cur.executemany("insert into search values (null, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s);", data)









if __name__ == '__main__':

    conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",

            port=3306)

    sqldoc = Sqldoc(conn,True)

    obj = {
        "a": "one",
        "b": 2,
        "c": {
            "d": "three",
            "e": 4.0,
            "f": [
                {
                    "x": "five",
                    "y": '2021-02-01 10:00:00'
                },
                {
                    "x": "six",
                    "y": "this is some text"
                },
            ],
            "g":(1,2,3)
        }
    }

    sqldoc.store_obj(obj)
    sqldoc.commit()













# cur = sqldoc.cursor()
#
# nums = '012345789'
# chars = 'abcdefghijklmnopqrstuvwxyz'
#
# # n = 10_000_000
# n = 10000
#
# for i in range(n):
#     data = []
#     elements = [random.choice(chars)]
#     elements.extend(random.choices(chars, k=random.randint(0, 6)))
#     path = '.'.join(elements)
#     rev = '.'.join(reversed(elements))
#     key = path[-1]
#     val = ''.join(random.choices(chars + '   ', k=random.randint(5, 60)))
#     docid = 'doc%s' % random.randint(1, math.ceil(n / 10))
#     data.append((docid, path, rev, key, val, val))
#     if (i % 10000 == 0):
#         print(i)
#
#     cur.executemany("insert into search values (null,%s,%s,%s,%s,%s,null, null, null, %s, 's');", data)
# if data:
#     cur.executemany("insert into search values (null,%s,%s,%s,%s,%s,null, null, null, %s, 's');", data)
#

conn.commit()