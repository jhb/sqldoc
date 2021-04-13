import re

def flatten_doc(doc, delimeter='.',path = ""):
    if isinstance(doc, dict):
        for k, v in doc.items():
            for r in flatten_doc(v, delimeter,path + delimeter + k if path else k):
                yield r
    elif isinstance(doc, list) or isinstance(doc,tuple):
        for i, v in enumerate(doc):
            s = str(i)
            for r in flatten_doc(v, delimeter, path + delimeter+s if path else s):
                yield r
    else:
        yield path,doc

def convert(doc):
    try:
        return int(doc)
    except ValueError:
        return doc

def add_to_current(current,key,next):
    if type(current) == dict:
        current[key]=next
    else:
        current.append(next)
    return current

def assemble_doc(items, delimeter='.'):
    items = sorted(items)
    doc = {}
    for path,value in items:
        current = doc
        parts = path.split(delimeter)
        for i,part in enumerate(parts):
            part = convert(part)
            if i+1 == len(parts):  #last element
                add_to_current(current,part,value)
            else:
                try:
                    current = current[part]
                except (KeyError, IndexError, TypeError):
                    nextpart = parts[i + 1]
                    if type(convert(nextpart)) == int:
                        nextdoc = []
                    else:
                        nextdoc = {}

                    add_to_current(current,part,nextdoc)
                    current = current[part]
    return doc



def prepare_sql(fragment, tablename='search'):
    indent = ' ' * 8
    fragment = fragment.strip()
    fragment = '\n'.join(indent + f.strip() for f in fragment.split('\n'))
    fragment = fragment[len(indent):]
    parts = re.findall(r'''(\w+)\.(\w+)(\W)''', fragment)
    names = sorted(list({p[0] for p in parts}))

    tables = f',\n{indent}'.join([f'{tablename} as {n}' for n in names])

    sql = f"""
    select 
        distinct {names[0]}.oid
    from
        {tables}
    where
        {fragment}"""

    if len(names) > 1:
        _ = [f'{name}.oid = {names[i + 1]}.oid' for i, name in enumerate(names[:-1])]
        where = ' and \n    '.join(_)
        sql += f' and\n{indent}' + where
    sql = '\n'.join(l[4:] for l in sql.split('\n'))
    return sql



if __name__ == '__main__':
    from pprint import pprint
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
                    "y": "this is some text"
                },
            ],
            "g":[1,2,3]
        }
    }
    db = flatten_doc(doc,'.')
    pprint(assemble_doc(db)==doc)

    part = """
        s1.path='b' and
        s1.str='2' and
        s2.path='a' and
        s2.str='one'
    
    """

    sql = prepare_sql(part)
    print(sql)