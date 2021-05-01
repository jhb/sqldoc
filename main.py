from fastapi import FastAPI
from fastapi import responses
import uvicorn
import config
from sqldoc_mariadb import Sqldoc
from sqlgraph import SqlGraph

app = FastAPI()
config.sqldoc = Sqldoc(config.conn,debug=False)
config.sg = SqlGraph(config.sqldoc)

import api
import gui

app.include_router(api.router, prefix='/api', tags=['api'])
app.include_router(gui.router, prefix='/gui', tags=['gui'])

if __name__ == '__main__':
    uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=True)
