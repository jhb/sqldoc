from fastapi import FastAPI
from fastapi import responses
import fastapi_chameleon
import uvicorn
from sqldoc import config
from sqldoc_mariadb import Sqldoc
from sqlgraph import SqlGraph

dev_mode=True

app = FastAPI()
fastapi_chameleon.global_init('templates', auto_reload=dev_mode)
config.sqldoc = Sqldoc(config.conn,debug=True)
config.sg = SqlGraph(config.sqldoc)

import api
from views import content, gui

app.include_router(api.router, prefix='/api', tags=['api'])
app.include_router(gui.router, prefix='/gui', tags=['gui'])
app.include_router(content.router, prefix='/content', tags=['gui','content'])

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
