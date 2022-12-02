from datetime import datetime
from requests import post, get
from json import loads
from threading import Thread
from time import sleep
from pydantic import BaseModel
from fastapi import Request, WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosed
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import APIRouter
from pyModbusTCP.client import ModbusClient
from typing import Dict, List
from yaml import safe_load
import asyncio
from pyModbusTCP.utils import get_2comp
from dotenv import load_dotenv
from os import getenv
load_dotenv()

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

    async def receive(self):
        try:
            for connection in self.active_connections:
                mm = loads(await connection.receive_text())
                registros = classRegisters.outRegisters.copy()
                try:
                    sal = [register['register']
                           for register in registros if mm['name'] == register['name']]
                    classRegisters.regsOut.update(
                        {'register': sal[0], 'value': mm['value']})
                except Exception as e:
                    print(e, 'ent')
        except:
            pass


manager = ConnectionManager()


class RegisterManager():
    def __init__(self):
        with open('settings_clinet.yml', 'r',  encoding='utf8') as file:
            self.pr = safe_load(file)
        self.modbusClient = ModbusClient(
            host=self.pr['server']['host'], port=self.pr['server']['port'], auto_open=False, auto_close=False)
        self.path = '/addData'
        # self.url = 'http://127.0.0.1:5000'+self.path
        self.url = 'http://141.147.133.37'
        # self.url = 'localhost:8000'
        self.listAddress = []
        self.dicc = {}
        self.listOut = []
        self.listOut1 = []
        self.outRegisters = []
        self.regs = {}
        self.regsOut = {}
        self.regWrite = None

    def updateRegisters(self):
        for i in self.pr['data']:
            self.dicc['write_type'] = i['write_type'] if i.get(
                'write_type') != None else None
            self.dicc['write_range'] = i['write_range'] if i.get(
                'write_range') != None else None
            self.outRegisters.append({'name': i['name'].replace(' ', ''),
                                      'value': 0,
                                      'register': i['register'],
                                      'scale': i['scale'],
                                      'write': i['write'],
                                      'write_type': self.dicc['write_type'],
                                      'write_range': self.dicc['write_range']})
            self.listAddress.append(i['register'])
        self.listAddress.sort()
        i = 0
        a = 0
        while True:
            if self.listAddress[i] == a:
                self.listOut.append(self.listAddress[i])
                i += 1
                a += 1
            else:
                self.listOut1.append(self.listOut.copy())
                self.listOut.clear()
                a = self.listAddress[i]
            if i == len(self.listAddress):
                self.listOut1.append(self.listOut.copy())
                break

    def __callme(self):
        control1 = True
        while True:
            sleep(0.1)
            a = 0
            if self.modbusClient.is_open:
                for i in self.listOut1:
                    modbusList = self.modbusClient.read_holding_registers(
                        i[0], len(i))
                    sleep(0.01)
                    if modbusList != None:
                        try:
                            for e in modbusList:
                                self.regs[self.listAddress[a]
                                          ] = get_2comp(e, 16)
                                a += 1
                            self.regs.update({'client': getenv('CLIENT')})
                            if str(datetime.now().strftime("%S")) == str("00") and control1:
                                try:
                                    print('datos', self.regs)
                                    post(self.url+self.path,
                                         json=self.regs, timeout=2)
                                except:
                                    pass
                                control1 = False
                            else:
                                control1 = True
                        except Exception as e:
                            print(e, 'ant')
                    else:
                        break
                try:
                    if self.regsOut != self.regWrite and len(self.regsOut.keys()) > 0:
                        self.regWrite = self.regsOut.copy()
                        self.modbusClient.write_single_register(
                            self.regsOut['register'], int(self.regsOut['value']))
                except:
                    pass
                for i in self.outRegisters:
                    i['value'] = round(
                        self.regs[i['register']]*i['scale'], 1)
            else:
                break

    def sendRegisters(self):
        t = Thread(target=self.__callme)
        t.start()


class Listener:
    def __init__(self, listReg: RegisterManager, polling_interval: float = 0.2) -> None:
        self.listReg = listReg
        self.polling_interval = polling_interval

    async def listen(self):
        loop = asyncio.get_running_loop()
        while True:
            asyncio.run_coroutine_threadsafe(manager.receive(), loop)
            lines = await loop.run_in_executor(None, self.poll)
            yield lines
            await asyncio.sleep(self.polling_interval)

    def poll(self):
        return self.listReg.outRegisters


classRegisters = RegisterManager()
classRegisters.updateRegisters()


@web.get('/', response_class=HTMLResponse)
async def main(request: Request):
    # get(classRegisters.url+'')
    listRegisters = classRegisters.pr['data']

    for i in listRegisters:
        i['category'] = sola[i['register']]
    listRegisters.sort(key=lambda x: x['category'])
    data = []
    newCat = [x['category'] for x in listRegisters if True]
    newlist = sorted(set(newCat))
    for i in newlist:
        data.append([x for x in listRegisters if x['category'] in i])
    try:
        # get(classRegisters.url+classRegisters.path, timeout=2)
        # falta crear el metodo para este
        serverOn = True
    except:
        serverOn = False
    context = {'request': request, 'data': data, 'server': serverOn}
    return templates.TemplateResponse('index.html', context=context)


@web.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    if not classRegisters.modbusClient.is_open:
        while not classRegisters.modbusClient.open():
            pass
        classRegisters.sendRegisters()
    listener = Listener(classRegisters)
    try:
        sleep(0.5)
        async for message in listener.listen():
            await manager.broadcast(message)

    except (WebSocketDisconnect, ConnectionClosed):
        print('desc')
        manager.disconnect(websocket)
        classRegisters.modbusClient.close()
    except Exception as e:
        manager.disconnect(websocket)
        print(e, 'sal')
        pass
