from fastapi.responses import JSONResponse,HTMLResponse
from requests import get
from time import sleep
from fastapi import Request, WebSocket, WebSocketDisconnect,APIRouter
from websockets.exceptions import ConnectionClosed
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from models.dic import datosBase
from models.model import manager,classRegisters,Listener
from os import getenv
load_dotenv()
web = APIRouter()

templates = Jinja2Templates(directory='templates')
@web.get('/', response_class=HTMLResponse)
async def main(request: Request):
    listRegisters = classRegisters.pr['data']
    for i in listRegisters:
        i['category'] = datosBase[i['register']]
    listRegisters.sort(key=lambda x: x['category'])
    data = []
    newCat = [x['category'] for x in listRegisters if True]
    newlist = sorted(set(newCat))
    for i in newlist:
        data.append([x for x in listRegisters if x['category'] in i])
    try:
        get(classRegisters.url+classRegisters.path, timeout=2)
        serverOn = True
    except:
        serverOn = False
    context = {'request': request, 'data': data, 'server': serverOn}
    return templates.TemplateResponse('index.html', context=context)


@web.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    if not classRegisters.modbusClient.is_open:
        for _ in range(2):
            if not classRegisters.modbusClient.open():
                sleep(1)
        if not classRegisters.modbusClient.is_open:
            await manager.disconnect(websocket)
    listener = Listener(classRegisters)
    try:
        sleep(0.5)
        async for message in listener.listen():
            await manager.broadcast(message)

    except (WebSocketDisconnect, ConnectionClosed):
        print('desc')
        await manager.disconnect(websocket)
        classRegisters.modbusClient.close()
        
    except Exception as e:
        await manager.disconnect(websocket)
        print(e, 'sal')
        pass
# Esto se cambiara por la base de datos local
@web.get('/get_registers/{reg}', response_class=JSONResponse)
async def main(reg: str):
    cli =getenv('CLIENT')
    print(cli)
    response=get(f"http://141.147.133.37/get_registers/{cli}/{reg}")
    print(response)
    # response=get(f"http://127.0.0.1:8000/get_register/{cli}/{reg}")
    return JSONResponse(content=response.json())
