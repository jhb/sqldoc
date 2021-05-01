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


@router.get('/{docid}', response_model=Document)
def get_doc(docid):
    return sqldoc.read_doc(docid)


@router.put('/{docid}', response_model=Document)
def post_doc(docid: str, doc: Document):
    doc['docid'] = docid
    return sqldoc.update_doc(doc)


@router.delete('/{docid}')
def delete_doc(docid):
    return None
