import datetime
from collections import UserDict
from copy import deepcopy
from pprint import pprint
from typing import Any, Union
from comparisons import part_of_full

registry = {}


class ValidationError(Exception):
    ...

class Registry(UserDict):
    """The registry for property and schema definitions"""

    def __init__(self):
        super().__init__()
        self.props = set()
        self.schemata = set()

    def add(self, key: str, obj: Union[type, list, tuple]):
        """Adds a definition. Props and schemata share a namespace, to avoid
        confusion in the data. A key is either defined or not, and should always
        mean one thing only"""

        if key in self:
            raise Exception(f'key {key} already taken')
        if isinstance(obj, list):
            obj = tuple(list)

        if isinstance(obj, tuple):
            self.schemata.add(key)
        else:
            self.props.add(key)
        self[key] = obj

    def collect_keys(self, key: str):
        """helper methods"""
        out = set()
        definition = self[key]
        if key in self.props:
            out.add(key)
        else:
            for d in definition:
                out = out.union(self.collect_keys(d))
        return out

    def matches_schema(self, obj: Any, key: str):
        """check if an obj matches a schema"""
        schema_keys = self.collect_keys(key)
        return set(obj.keys()).issuperset(schema_keys)

    def find_schemata(self, obj: Any):
        """find all schemata for an object"""
        return sorted([k for k in self.schemata if self.matches_schema(obj, k)])

    def convert(self, obj: Any, path: str = '', separator: str = '.'):
        """Return data,errors. Checks for schema validation."""
        obj = deepcopy(obj)
        errors = {}
        key = path.split(separator)[-1]
        if isinstance(obj, dict):
            for k, v in obj.items():
                subpath = path and path + separator + k or k
                new_value, e = self.convert(v, subpath, separator)
                obj[k] = new_value
                errors.update(e)
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                subpath = path and path + separator + str(i) or str(i)
                new_value, e = self.convert(v, subpath, separator)
                obj[i] = new_value
                errors.update(e)
        elif key in self:
            try:
                obj = self[key](obj) # the actual conversion
            except Exception as e:
                errors[path] = e
        else:
            obj, suberrors = self.guess(obj, path)
            errors.update(suberrors)

        if key in self.schemata and not self.matches_schema(obj, key):
            errors[path] = f"Path '{path}' did not fit Schema '{key}'"

        return obj, errors

    def validate(self, obj: Any):
        """Throw an exception if it doesn't fit"""
        new, errors = self.convert(obj)
        if errors:
            raise ValidationError(errors)
        return new

    def guess(self, value: Any, path: str):
        errors = {}
        success = False
        for m in [datetime.datetime, float, int, str]:
            try:
                value = m(value)
                success = True
                break
            except Exception as e:
                pass
        if not success:
            errors[path] = f'could not convert at {path}'
        return value, errors



if __name__ == '__main__':
    r = Registry()

    r.add('_docid', str)
    r.add('_source', str)
    r.add('_target', str)
    r.add('name', str)
    r.add('age', int)
    r.add('street', str)
    r.add('city', str)
    r.add('address', ('street', 'city'))
    r.add('person', ('name', 'address'))
    r.add('content_type', str)
    r.add('content_data', str)
    r.add('content', ('content_type', 'content_data'))
    r.add('edge', ('node', '_source', '_target'))
    r.add('node',('_docid',))

    edge = {'_docid':   'c556a24098af4be69871d5e26cde5664',
            '_source':  'ea7a97d43d5b4846ba2bf707b775ff4d',
            '_target':  '7518d0c8f58040e8934c49af189c28c5',
            'relation': 'likes'}

    person = dict(name='Alice Alison',
                  age='50',
                  job='somejob',
                  other_address=dict(street='Somestreet',
                                     city='Middletown',
                                     age='10'),
                  address=dict(foo='bar',
                               city='somewhere',
                               age='blurb'),
                  street='Firststreet',
                  city='New York',
                  content=dict(content_type='text/plain',
                               content_data='somedata'))
    pprint(r.props)
    print(r.matches_schema(person, 'address'))
    print(r.find_schemata(person))
    print(r.find_schemata(edge))
    print(r.convert(person))
    print(person)
    try:
        print(r.validate(person))
    except ValidationError as e:
        print(e)
