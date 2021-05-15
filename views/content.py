from sqldoc.views import BaseView

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

from sqldoc import config
from sqldoc.helpers import convert, get_by_path, set_by_path
from sqldoc.schemata import ValidationError

from sqldoc.views.view_helpers import helpers
from markdown import markdown

sqldoc = config.sqldoc
sg = config.sg
reg = config.r


router = fastapi.APIRouter(default_response_class=fastapi.responses.HTMLResponse)
#config.register_view(router,['content'])


@router.get('/edit/{_docid}', name='content')
@template(template_file='content.pt')
def edit_get(_docid: str):
    doc: dict = sqldoc.read_doc(_docid)
    converters = {'text/markdown':markdown}
    converted = converters.get(doc['content_type'],str)(doc['content_data'])
    return dict(doc=doc,helpers=helpers,converted=converted)

@router.post('/edit/{_docid}', name='content')
@template(template_file='content.pt')
def edit_post(_docid: str,content_type:str=Form(...),content_data:str=Form(...)):
    doc: dict = sqldoc.read_doc(_docid)
    doc['content_type']=content_type
    doc['content_data']=content_data
    sqldoc.update_doc(doc)
    sqldoc.commit()
    return RedirectResponse(
            f'/content/edit/{_docid}', status_code=status.HTTP_302_FOUND
    )



print(router.routes)
