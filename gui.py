import fastapi
import api


import config
from models import Document


sqldoc = config.sqldoc
sg = config.sg

router = fastapi.APIRouter(default_response_class=fastapi.responses.HTMLResponse)


@router.get('/')
def index():
    return f"<div>{sqldoc.query_docs()}</div>"