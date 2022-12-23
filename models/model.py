from pydantic import BaseModel
from fastapi import Form
from requests import post
from json import loads
from threading import Thread
from time import sleep
from pydantic import BaseModel
from fastapi import WebSocket
from pyModbusTCP.client import ModbusClient
from typing import List
from yaml import safe_load
import asyncio
from pyModbusTCP.utils import get_2comp
from dotenv import load_dotenv
from os import getenv
load_dotenv()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        await websocket.close()

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

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
                            try:
                                # post(self.url+self.path,json=self.regs, timeout=2)
                                pass
                            except:
                                pass
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

manager = ConnectionManager()

# implementación futura----------------------------------------------------------------


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls


@form_body
class Item(BaseModel):
    name: str
    another: str
