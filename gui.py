from pprint import pformat

import fastapi
# from toml import dumps as safe_dump
# from toml import loads as safe_load
from fastapi import Form
from fastapi.responses import RedirectResponse
from fastapi_chameleon import template
from nestedtext import loads, dumps
from starlette import status
from starlette.requests import Request

import config
from sqldoc.helpers import convert

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
            for key in subpath.split(config.delimiter):
                doc = doc[convert(key)]
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
              subpath: str = '') -> RedirectResponse:
    e = ''
    try:
        doc = loads(doc)
        # doc['text']='foo\nbla\n\nblub\nbaz'

        if docid == 'new':
            sqldoc.create_doc(doc)
        else:
            doc['docid'] = docid
            sqldoc.update_doc(doc)
        sqldoc.commit()
        return RedirectResponse(
                '/gui', status_code=status.HTTP_302_FOUND
        )

    except Exception as e:
        return dict(doc=doc,
                    docid=docid,
                    error=e)
