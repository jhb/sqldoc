import fastapi
from fastapi.responses import RedirectResponse

import api
from yaml import safe_dump, safe_load
from fastapi import Form

import config
from models import Document

from fastapi_chameleon import template
from starlette import status
from starlette.requests import Request

from pprint import pformat

sqldoc = config.sqldoc
sg = config.sg

router = fastapi.APIRouter(default_response_class=fastapi.responses.HTMLResponse)


@router.get('/')
@template(template_file='index.pt')
def index():
    return dict(docs=sqldoc.query_docs(), pformat=pformat)


@router.get('/edit/{docid}')
@template(template_file='edit.pt')
def edit_get(docid: str) -> dict:
    if docid == 'new':
        yaml_doc = ''
    else:
        doc: dict = sqldoc.read_doc(docid)
        yaml_doc = safe_dump({k: v for k, v in doc.items() if k != 'docid'})
    return dict(yaml_doc=yaml_doc,
                docid=docid,
                error='')


@router.post('/edit/{docid}')
@template(template_file='edit.pt')
def edit_post(docid: str, yaml: str = Form(default='')) -> RedirectResponse:
    e = ''
    try:
        doc = safe_load(yaml)
        if docid == 'new':
            sqldoc.create_doc(doc)
        else:
            doc['docid'] = docid
            sqldoc.update_doc(doc)
        sqldoc.commit()
        return RedirectResponse(
            '..', status_code=status.HTTP_302_FOUND
        )

    except Exception as e:
        return dict(yaml_doc=yaml,
                    docid=docid,
                    error=e)
