from typing import Union, List

import fastapi

import config
from models import Document

sqldoc = config.sqldoc
sg = config.sg
# sqldoc.autocommit=True

router = fastapi.APIRouter()


@router.get('/', response_model= List[str])
def index(query: str = ''):
    return sqldoc.querydocids()


@router.post('/', response_model=Document)
def add(doc: Document):
    return sqldoc.create_doc(doc)


@router.get('/{_docid}', response_model=Document)
def get_doc(_docid):
    return sqldoc.read_doc(_docid)


@router.put('/{_docid}', response_model=Document)
def post_doc(_docid: str, doc: Document):
    doc['_docid'] = _docid
    return sqldoc.update_doc(doc)


@router.delete('/{_docid}')
def delete_doc(_docid):
    return None
