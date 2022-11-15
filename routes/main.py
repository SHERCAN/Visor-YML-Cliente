from pydantic import BaseModel
from fastapi import Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pyModbusTCP.client import ModbusClient
from typing import Dict, List
from yaml import safe_load
c = ModbusClient(host="localhost", port=502, unit_id=1,
                 auto_open=False, auto_close=False)
web = APIRouter()
templates = Jinja2Templates(directory='templates')
sola = {30: 'Grid',
        31: 'Grid',
        32: 'Grid',
        88: 'Inverter',
        33: 'Inverter',
        34: 'Inverter',
        35: 'Inverter',
        36: 'Load',
        37: 'Load',
        38: 'Grid',
        39: 'Grid',
        89: 'Grid',
        90: 'Grid',
        40: 'Inverter',
        41: 'Inverter',
        42: 'Generator',
        43: 'Grid',
        44: 'Grid',
        45: 'Grid',
        91: 'Grid',
        92: 'Grid',
        46: 'Grid',
        47: 'Inverter',
        48: 'Inverter',
        49: 'Inverter',
        50: 'Load',
        51: 'Load',
        52: 'Load',
        53: 'Load',
        54: 'Load',
        55: 'Generator',
        56: 'Battery',
        57: 'Battery',
        58: 'Battery',
        59: 'PV',
        60: 'PV',
        61: 'Battery',
        62: 'Battery',
        63: 'Load',
        64: 'Inverter',
        65: 'Grid',
        93: 'Generator',
        66: 'Generator',
        94: 'Configuration',
        95: 'Configuration',
        96: 'Configuration',
        97: 'Configuration',
        98: 'Configuration',
        99: 'Configuration',
        100: 'Configuration',
        101: 'Configuration',
        102: 'Configuration',
        103: 'Configuration',
        104: 'Configuration',
        105: 'Configuration',
        107: 'Configuration',
        108: 'Configuration',
        109: 'Configuration',
        110: 'Configuration',
        111: 'Configuration',
        112: 'Configuration',
        113: 'Configuration',
        114: 'Configuration',
        115: 'Configuration',
        116: 'Configuration',
        117: 'Configuration',
        118: 'Configuration',
        119: 'Configuration',
        120: 'Configuration',
        121: 'Configuration',
        122: 'Configuration',
        123: 'Configuration',
        124: 'Configuration',
        125: 'Configuration',
        126: 'Configuration',
        127: 'Configuration',
        128: 'Configuration',
        129: 'Configuration',
        130: 'Configuration',
        131: 'Configuration',
        132: 'Configuration',
        133: 'Configuration',
        135: 'Configuration',
        136: 'Configuration',
        29: 'Configuration',
        0: 'Configuration',
        137: 'Configuration',
        1: 'Configuration',
        2: 'Configuration',
        3: 'Configuration',
        4: 'Configuration',
        8: 'Configuration',
        12: 'Configuration',
        16: 'Configuration',
        20: 'Configuration',
        24: 'Configuration',
        5: 'Configuration',
        9: 'Configuration',
        13: 'Configuration',
        17: 'Configuration',
        21: 'Configuration',
        25: 'Configuration',
        139: 'Configuration',
        140: 'Configuration',
        141: 'Configuration',
        142: 'Configuration',
        143: 'Configuration',
        144: 'Configuration',
        6: 'Configuration',
        10: 'Configuration',
        14: 'Configuration',
        18: 'Configuration',
        22: 'Configuration',
        26: 'Configuration',
        7: 'Configuration',
        11: 'Configuration',
        15: 'Configuration',
        19: 'Configuration',
        23: 'Configuration',
        27: 'Configuration',
        145: 'Configuration',
        146: 'Configuration',
        147: 'Configuration',
        148: 'Configuration',
        149: 'Configuration',
        150: 'Configuration',
        151: 'Configuration',
        152: 'Configuration',
        153: 'Configuration',
        154: 'Configuration',
        155: 'Configuration',
        156: 'Configuration',
        157: 'Configuration',
        158: 'Configuration',
        28: 'Configuration',
        159: 'Configuration',
        106: 'Empty',
        134: 'Empty',
        138: 'Empty',
        }


class ModelSettings(BaseModel):
    dataframe: Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


def updateRegisters():
    with open('settings_clinet.yml', 'r') as file:
        pr = safe_load(file)
    listAddress = []
    dicc = {}
    for i in pr['data']:
        dicc[i['name']] = i['register']
    for i in pr['data']:
        listAddress.append(i['register'])
    listAddress.sort()
    listOut = []
    listOut1 = []
    i = 0
    a = 0
    while True:
        if listAddress[i] == a:
            listOut.append(listAddress[i])
            i += 1
            a += 1
        else:
            listOut1.append(listOut.copy())
            listOut.clear()
            a = listAddress[i]
        if i == len(listAddress):
            listOut1.append(listOut.copy())
            break
    regs = {}
    a = 0
    if c.open():
        for i in listOut1:
            modbusList = c.read_holding_registers(i[0], len(i))
            for e in modbusList:
                regs[listAddress[a]] = e
                a += 1
        c.close()
    else:
        pr['data'] = ''
    try:
        for i in pr['data']:
            i['value'] = regs[i['register']]
            i['category'] = sola[i['register']]
    except:
        i['value'] = None
    return pr['data']


@web.get('/', response_class=HTMLResponse)
async def main(request: Request):
    # try:
    # manager.disconnect(manager.active_connections[0])
    # except:
    #     print('error')
    #     pass
    # dataRegisters=updateRegisters()
    with open('settings_clinet.yml', 'r') as file:
        pr = safe_load(file)
    listRegisters = pr['data']
    for i in listRegisters:
        i['category'] = sola[i['register']]
    listRegisters.sort(key=lambda x: x['category'])
    data = []
    newCat = [x['category'] for x in listRegisters if True]
    newlist = sorted(set(newCat))
    for i in newlist:
        data.append([x for x in listRegisters if x['category'] in i])
    context = {'request': request, 'data': data}
    return templates.TemplateResponse('index.html', context=context)


@web.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    while websocket.client_state.CONNECTED:
        try:
            await manager.broadcast(updateRegisters())
        except (WebSocketDisconnect, ConnectionClosed):
            await manager.disconnect(websocket)
            break
        except Exception as e:
            print(e)
            break
