# -----------------------------------modules-----------------------------
from fastapi import FastAPI
from routes.main import web
from config.var_env import mode
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# -----------------------------------run---------------
app = FastAPI(title='Configrator YAML',
              description='Configuration of the YAML file', version='0.0.1')
# -----------------------------------cors---------------

templates = Jinja2Templates(directory='templates')
app.include_router(web)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="js")