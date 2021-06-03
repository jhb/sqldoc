import datetime
from collections import UserDict
from copy import deepcopy
from pprint import pprint
from typing import Union, Any

import pytest
# 1
class ValidationError(Exception):

    def __repr__(self):
        return self.__class__.__name__

class Registry(UserDict):
    def __init__(self):
        super().__init__()
        self.props = set()
        self.schemata = set()
        self.aliases = set()

    def add(self, key: str, obj: Union[type, list, tuple, str]):
        """Adds a definition. Props and schemata share a namespace, to avoid
        confusion in the data. A key is either defined or not, and should always
        mean one thing only"""

        if key in self:
            raise Exception(f'key {key} already taken')

        if isinstance(obj, list):
            obj = tuple(list)

        if isinstance(obj, tuple):
            self.schemata.add(key)
        elif isinstance(obj,str):
            self.aliases.add(key)
        else:
            self.props.add(key)
        self[key] = obj
        return obj

    def convert(self, obj: Any, path: str = '', separator: str = '.', copy_unknown=False):
        """Return data,errors. Checks for schema validation."""
        obj = deepcopy(obj)
        errors = {}
        key = path.split(separator)[-1]

        if isinstance(obj, dict):
            for k, v in obj.items():
                subpath = path and path + separator + k or k
                new_value, e = self.convert(v, subpath, separator, copy_unknown)
                obj[k] = new_value
                errors.update(e)
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                subpath = path and path + separator + str(i) or str(i)
                new_value, e = self.convert(v, subpath, separator, copy_unknown)
                obj[i] = new_value
                errors.update(e)
        elif key in self:
            validator = self[key]
            while isinstance(validator,str):
                validator = self[validator]

            if isinstance(validator,(list,tuple)):
                errors[path]=f'validator {key} for {path} resolves to iterable'
            else:
                try:
                    obj = validator(obj)  # the actual conversion
                except Exception as e:
                    errors[path] = e
        elif copy_unknown:
            obj, suberrors = self.guess(obj, path)
            errors.update(suberrors)
        else:
            obj = ValidationError()
            errors[path]=f'no validator for {path}'
        return obj, errors

    def find_schemata(self, obj: Any):
        """find all schemata for an object"""
        return sorted([k for k in self.schemata if self.has_schema(obj, k)])



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

    def matches_schema(self, obj, key):
        print(obj,key)
        validator = self[key]
        if isinstance(validator,(list,tuple)):
            return not any(
                i not in obj or not self.matches_schema(obj[i], i)
                for i in validator
            )
        elif isinstance(validator,str):
            return self.matches_schema(obj,self[validator])
        else:
            try:
                validator(obj)
                return True
            except:
                return False

    def has_schema(self,obj,key,recursive=False):
        if self.matches_schema(obj,key):
            return True

        if isinstance(obj,dict):
            if recursive:
                return any(
                    self.has_schema(obj[k],key,recursive)
                    for k in obj
                )
            else:
                return key in obj and self.matches_schema(obj[key],key)

        elif isinstance(obj,(list,tuple)):
            if recursive:
                return any(
                    self.has_schema(i,key,recursive)
                    for i in obj
                )
            else:
                return False
        else:
            return self.matches_schema(obj,key)

    def validate(self, obj: Any, copy_unknown:bool=False):
        """Throw an exception if it doesn't fit"""
        new, errors = self.convert(obj,copy_unknown=copy_unknown)
        if errors:
            raise ValidationError(errors)
        return new



@pytest.fixture
def registry()->Registry:
    r = Registry()
    r.add('name', str)
    r.add('age', int)
    r.add('street', str)
    r.add('city', str)
    r.add('tags',list)
    r.add('address', ('street', 'city'))
    r.add('person', ('name', 'address'))
    r.add('home_adress','address')

    return r

@pytest.fixture
def sampledata():
    return dict(name='Joerg',
                age='48',
                home_address=dict(city='Bielefeld',
                                  street='somestreet'),
                other_address=dict(city='Bielefeld',
                                   street='otherstreet'),
                address=dict(city='Bielefeld',
                             street='rightstreet'),
                third_address=dict(city='Leipzig',
                                   foo='bar'),
                tags = ['foo','bar'])

@pytest.fixture
def no_address(sampledata):
    data = {k: v for k, v in sampledata.items() if k not in ['address']}
    return data

@pytest.mark.parametrize('key,expectation',[('person',True),
                                            ('address',False),
                                            ('tags',True)])
def test_matches_schema(registry,sampledata,key,expectation):
    result =  registry.matches_schema(sampledata,key) == expectation
    assert result

@pytest.mark.parametrize('key,expectation',[('person',True),
                                            ('address',True)])
def test_has_schema(registry,sampledata,key,expectation):
    result = registry.has_schema(sampledata,key) == expectation
    assert result

def test_has_schema_missing(registry,no_address):
    assert registry.has_schema(no_address,'address') == False

def test_has_schema_recursive(registry,no_address):
    assert registry.has_schema(no_address,'address',True) == True

def test_convert(registry,sampledata):
    newdata,errors = registry.convert(sampledata)
    assert isinstance(newdata['third_address']['foo'],ValidationError)
    assert errors

def test_convert_unknown(registry,sampledata):
    newdata, errors = registry.convert(sampledata,copy_unknown=True)
    assert newdata['third_address']['foo']=='bar'
    assert not errors

def test_jhb(registry,sampledata):
    registry.has_schema(sampledata,'address')

