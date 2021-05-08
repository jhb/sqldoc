from pprint import pformat

import fastapi
# from toml import dumps as safe_dump
# from toml import loads as safe_load
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi_chameleon import template
from nestedtext import loads, dumps, NestedTextError
from starlette import status
from starlette.requests import Request

import config
from sqldoc.helpers import convert, get_by_path, set_by_path

sqldoc = config.sqldoc
sg = config.sg

router = fastapi.APIRouter(default_response_class=fastapi.responses.HTMLResponse)


@router.get('/')
@template(template_file='index.pt')
def index():
    return dict(docs=sqldoc.query_docs(), pformat=pformat)


@router.get('/edit/{docid}')
@router.get('/edit/{docid}/{subpath:path}')
@template(template_file='edit.pt')
def edit_get(docid: str, subpath: str = '') -> dict:
    if docid == 'new':
        doc = ''
    else:
        doc: dict = sqldoc.read_doc(docid)
        doc = {k: v for k, v in doc.items() if k != 'docid'}
        if subpath:
            doc = get_by_path(doc, subpath, config.delimiter)
        if type(doc) in [list, tuple, dict]:
            doc = dumps(doc, indent=2)
    return dict(doc=doc,
                docid=docid,
                error='')


@router.post('/edit/{docid}')
@router.post('/edit/{docid}/{subpath:path}')
@template(template_file='edit.pt')
def edit_post(docid: str,
              request: Request,
              doc: str = Form(default=''),
              subpath: str = ''):
    error = ''
    try:
        try:
            doc = loads(doc, top='any')
            if type(doc) is dict and docid in doc:
                del(doc['docid'])
        except NestedTextError:
            doc = doc

        if docid == 'new':
            if type(doc) == str:
                doc = dict(data=doc)
            sqldoc.create_doc(doc)
        else:
            old_doc: dict = sqldoc.read_doc(docid)
            if subpath:
                set_by_path(old_doc,doc,subpath,config.delimiter)
            else:
                old_doc = doc
            old_doc['docid'] = docid
            sqldoc.update_doc(old_doc)
        sqldoc.commit()
        return RedirectResponse(
                '/gui', status_code=status.HTTP_302_FOUND
        )

    except Exception as error:
        if type(doc) is dict:
            doc = {k: v for k, v in doc.items() if k != 'docid'}
        return dict(doc=doc,
                    docid=docid,
                    error=error)
