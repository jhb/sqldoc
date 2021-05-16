

import fastapi
# from toml import dumps as safe_dump
# from toml import loads as safe_load
from fastapi import Form, Request
from fastapi.responses import RedirectResponse
from fastapi_chameleon import template
from nestedtext import loads, dumps, NestedTextError
from starlette import status
from starlette.requests import Request

from sqldoc import config
from sqldoc.helpers import convert, get_by_path, set_by_path
from sqldoc.schemata import ValidationError
from sqldoc.views.view_helpers import helpers

sqldoc = config.sqldoc
sg = config.sg
reg = config.r

router = fastapi.APIRouter(default_response_class=fastapi.responses.HTMLResponse)


forbidden = ['_docid','_schemata']


@router.get('/')
@template(template_file='index.pt')
def index():
    return {}


@router.get('/list')
@template(template_file='list.pt')
def list(request: Request, searchtext: str=''):
    fragment = ''
    if searchtext:
        if '=' in searchtext:
            fragment = searchtext
        else:
            fragment = f"attr.text='{searchtext}'"
    return dict(docs=sqldoc.query_docs(fragment), helpers=helpers,searchtext=searchtext,request=request)


@router.get('/edit/{_docid}')
@router.get('/edit/{_docid}/{subpath:path}')
@template(template_file='edit.pt')
def edit_get(request: Request, _docid: str, subpath: str = '', addschema: str = '') -> dict:
    if _docid == 'new':
        doc = {}
    else:
        doc: dict = sqldoc.read_doc(_docid)
        if subpath:
            doc = get_by_path(doc, subpath, config.delimiter)

    if addschema:
        existing = reg.find_schemata(doc)
        if addschema in reg and addschema not in existing:
            for key in reg.collect_keys(addschema):
                if key not in doc:
                    doc[key] = ''

    if type(doc) in [list, tuple, dict]:
        _ = {k: v for k, v in doc.items() if k not in forbidden}
        docstring = dumps(_, indent=2)
    else:
        docstring = doc



    return dict(docstring = docstring,
                doc=doc,
                _docid=_docid,
                error='',
                helpers=helpers,
                request = request)


@router.post('/edit/{_docid}')
@router.post('/edit/{_docid}/{subpath:path}')
@template(template_file='edit.pt')
def edit_post(_docid: str,
              request: Request,
              doc: str = Form(default=''),
              subpath: str = '',
              addschema: str = Form(default='')):
    error = ''
    try:
        try:
            doc = loads(doc, top='any')
            if not doc:
                doc = {}
            doc,errors = reg.convert(doc)
            if errors:
                raise Exception(errors)
            if type(doc) is dict and _docid in doc:
                del(doc['_docid'])
        except NestedTextError:
            doc = doc

        if addschema:
            existing = reg.find_schemata(doc)
            if addschema in reg and addschema not in existing:
                for key in reg.collect_keys(addschema):
                    if key not in doc:
                        doc[key]=''

        if _docid == 'new':
            if type(doc) == str:
                doc = dict(data=doc)
            doc['_schemata']=reg.find_schemata(doc)
            doc = sqldoc.create_doc(doc)
        else:
            old_doc: dict = sqldoc.read_doc(_docid)
            if subpath:
                set_by_path(old_doc,doc,subpath,config.delimiter)
            else:
                old_doc = doc
            old_doc['_docid'] = _docid
            old_doc['_schemata'] = reg.find_schemata(old_doc)
            doc = sqldoc.update_doc(old_doc)
        sqldoc.commit()
        _docid = doc['_docid']
        return RedirectResponse(
                f'/gui/edit/{_docid}', status_code=status.HTTP_302_FOUND
        )

    except Exception as error:

        if type(doc) in [list, tuple, dict]:
            _ = {k: v for k, v in doc.items() if k not in forbidden}
            docstring = dumps(_, indent=2)
        else:
            docstring = ''
        return dict(doc=doc,
                    docstring=docstring,
                    _docid=_docid,
                    error=error,
                    helpers=helpers,
                    request = request)
