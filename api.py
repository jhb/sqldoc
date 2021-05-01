from typing import Union

import fastapi

import config
from models import Document

sqldoc = config.sqldoc
sg = config.sg
# sqldoc.autocommit=True

router = fastapi.APIRouter()


@router.get('/')
def index(query: str = ''):
    return sqldoc.querydocids()


@router.post('/')
def add(doc: Document):
    return sqldoc.create_doc(doc)


@router.get('/{docid}')
def get_doc(docid):
    return sqldoc.read_doc(docid)


@router.put('/{docid}')
def post_doc(docid: str, doc: Document):
    doc['docid'] = docid
    return sqldoc.update_doc(doc)


@router.delete('/{docid}')
def delete_doc(docid):
    return None
