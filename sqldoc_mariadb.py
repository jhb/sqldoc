import itertools
import uuid
from datetime import datetime
from pprint import pprint

import mariadb
from dateutil.parser import parse
import dateutil
from objectkeys import flatten_obj, assemble_obj

class Sqldoc:

    def __init__(self, conn, do_setup=False):
        self.conn = conn
        self.autocommit = False
        if do_setup:
            self.setup_tables()

        self.to_sql_map = dict(str=str,
                               int=int,
                               float=float,
                               dt=parse,
                               text=str,
                               blob=self.to_blob)

        self.from_sql_map = dict(s = 'str',
                                 i = 'int',
                                 f = 'float',
                                 d = 'dt',
                                 t = 't',
                                 b = 'blob')

    def commit(self):
        self.conn.commit()

    def cursor(self, *args, **kwargs):
        return self.conn.cursor(*args, **kwargs)

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
                    `type` char,
                   `str` varchar(256),
                   `int` integer,
                   `float` float,
                   `dt` datetime,
                   `text` text,
                   `blob` blob
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

    def to_blob(self, value):
        if len(value) > 1024:
            return value
        else:
            return None

    def to_sql(self):
        return

    def store_obj(self, obj, oid=None):
        if oid is None:
            oid = uuid.uuid4().hex
        rows = []
        data = []
        for key, value in itertools.chain(flatten_obj(obj), (('_oid', oid),)):
            row = {'oid':  oid,
                   'path': key,
                   'rev':  '.'.join(reversed(key.split('.'))),
                   'name': key.split('.')[-1],
                   'type': str(type(value))[8]}
            for fname, f in self.to_sql_map.items():
                try:
                    v = f(value)
                except (ValueError, TypeError):
                    v = None
                row[fname] = v
            rows.append(row)
            data.append(tuple(row.values()))
        cur = self.cursor()
        cur.executemany("insert into search values (null, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s);", data)
        newobj = dict(obj)
        newobj['_oid']=oid
        return oid,newobj

    def read_obj(self,oid):
        cur = self.cursor(dictionary=True)
        cur.execute("select * from search where oid=%s", (oid,))
        items = []
        for row in cur.fetchall():
            colname = self.from_sql_map.get(row['type'],'str')
            value = row[colname]
            items.append((row['path'],row[colname]))
        obj = assemble_obj(items)
        return obj


if __name__ == '__main__':
    conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",

            port=3306)

    sqldoc = Sqldoc(conn, True)

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
                    "g": [1, 2, 3],
                    "h": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    }

    oid, obj1 = sqldoc.store_obj(obj)
    sqldoc.commit()
    obj2 = sqldoc.read_obj(oid)
    assert obj2==obj1
