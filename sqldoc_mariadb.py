import uuid
from datetime import datetime
from pprint import pprint

import mariadb
from dateutil.parser import parse

from helpers import flatten_doc, assemble_doc, prepare_sql


class AlreadyExisting(Exception):
    pass


class DocStorage:
    pass


class Sqldoc(DocStorage):

    def __init__(self, conn, do_setup=False, debug=False):
        self.conn = conn
        self.debug = debug
        self.autocommit = False
        if do_setup:
            self.setup_tables()
            self.setup_indexes()

        self.to_sql_map = dict(str=str,
                               int=int,
                               float=float,
                               dt=self.to_datetime,
                               text=str,
                               blob=self.to_blob)

        self.from_sql_map = dict(s='str',
                                 i='int',
                                 f='float',
                                 d='dt',
                                 t='t',
                                 b='blob')

    @staticmethod
    def docid(docid):
        if type(docid) != str:
            docid = docid['docid']
        return docid

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
                   `docid` varchar(32) not null,
                   `path`  varchar(256) not null,
                   `rev`   varchar(256) not null,
                   `name`  varchar(256) not null,
                    `type` char,
                   `str`   varchar(256),
                   `int`   integer,
                   `float` float,
                   `dt`    datetime(6),
                   `text`  text,
                   `blob`  blob
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
                "create index if not exists `type` on search (`type`);",
                "create index if not exists `str` on search (`str`);",
                "create index if not exists `int` on search (`int`);",
                "create index if not exists `float` on search (`float`);",
                "create index if not exists `dt` on search (`dt`);",
                "create fulltext index if not exists `text` on search (`text`);",

        ]
        cur = self.cursor()
        for s in finish:
            cur.execute(s)

    @staticmethod
    def to_blob(value):
        if len(value) > 1024:
            return value
        else:
            return None

    def to_sql(self):
        return

    @staticmethod
    def to_datetime(value):
        if type(value) is datetime:
            return value
        else:
            return parse(value)

    def create_doc(self, doc, docid=None, newdocid_on_conflict=False):
        doc = dict(doc)

        if docid is None:
            docid = doc.get('docid', uuid.uuid4().hex)

        existing = self.querydocids(f"attr.name='docid' and attr.str='{docid}'")
        if existing:
            if newdocid_on_conflict:
                docid = uuid.uuid4().hex
            else:
                raise AlreadyExisting(docid)

        doc['docid'] = docid
        rows = []
        data = []
        for key, value in flatten_doc(doc):
            row = {'docid': docid,
                   'path':  key,
                   'rev':   '.'.join(reversed(key.split('.'))),
                   'name':  key.split('.')[-1],
                   'type':  str(type(value))[8]}
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
        return doc

    def read_doc(self, docid, klass=dict):
        docid = self.docid(docid)
        cur = self.cursor(dictionary=True)
        cur.execute("select * from search where docid=%s", (docid,))
        items = []
        for row in cur.fetchall():
            colname = self.from_sql_map.get(row['type'], 'str')
            value = row[colname]
            items.append((row['path'], value))
        return assemble_doc(items)

    def del_doc(self, docid):
        docid = self.docid(docid)
        cur = self.cursor()
        cur.execute("delete from search where docid=%s", (docid,))

    def update_doc(self, doc):
        docid = doc['docid']
        self.del_doc(docid)
        return self.create_doc(doc)

    def querydocids(self, fragment):
        sql = prepare_sql(fragment)
        cur = self.cursor()
        if self.debug:
            print(sql)
        cur.execute(sql)
        return [r[0] for r in cur.fetchall()]

    def query_docs(self, fragment):
        docids = self.querydocids(fragment)
        return [self.read_doc(docid) for docid in docids]


def test():
    conn = mariadb.connect(
            user="sqldoc",
            password="sqldoc",
            database='sqldoc',
            host="127.0.0.1",

            port=3306)

    sqldoc = Sqldoc(conn, True)

    doc = {
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
                                    "y": "this is some rather random text"
                            },
                    ],
                    "g": [1, 2, 3],
                    "h": datetime.now()
            }
    }

    doc1 = sqldoc.create_doc(doc)
    sqldoc.commit()

    doc2 = sqldoc.read_doc(doc1['docid'])
    pprint(doc1)
    pprint(doc2)
    assert doc2 == doc1
    doc2['foo'] = 'bar'
    doc3 = sqldoc.update_doc(doc2)
    pprint(doc3)

    docid2 = sqldoc.querydocids('attr.path="a"')
    pprint(docid2)

    pprint(sqldoc.query_docs('attr.name="h"'))

    try:
        sqldoc.create_doc(doc3)
    except AlreadyExisting:
        pass

    doc4 = sqldoc.create_doc(doc3, newdocid_on_conflict=True)
    print(doc4['docid'])

    sqldoc.commit()  # needed for fulltext indexing
    print(sqldoc.querydocids("attr.name='y' and attr.text='random'"))

    sqldoc.commit()


if __name__ == '__main__':
    test()
