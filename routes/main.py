from pydantic import BaseModel
from fastapi import Request, WebSocket, WebSocketDisconnect
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
sola={'Grid side voltage L1-N':'Grid',
'Grid side voltage L2-N':'Grid',
'Grid side voltage L1-L2':'Grid',
'Voltage at middle side of relay L1-L2':'Inverter',
'Inverter output voltage L1-N':'Inverter',
'Inverter output voltage L2-N':'Inverter',
'Inverter output voltage L1-L2':'Inverter',
'Load voltage L1':'Load',
'Load voltage L2':'Load',
'Empty Register':'',
'Grid side current L1':'Grid',
'Grid side current L2':'Grid',
'Grid external Limiter current L1':'Grid',
'Grid external Limiter current L2':'Grid',
'Inverter output current L1':'Inverter',
'Inverter output current L2':'Inverter',
'Gen or AC Coupled power input':'Generator',
'Grid side L1 power':'Grid',
'Grid side L2 power':'Grid',
'Total power of grid side L1-L2':'Grid',
'Grid external Limter1 power':'Grid',
'Grid external Limter2 power':'Grid',
'Grid external Total Power':'Grid',
'Inverter outputs L1 power':'Inverter',
'Inverter outputs L2 power':'Inverter',
'Inverter output Total power':'Inverter',
'Load side L1 power':'Load',
'Load side L2 power':'Load',
'Load side Total power':'Load',
'Load current L1':'Load',
'Load current L2':'Load',
'Gen Port Voltage':'Generator',
'Battery temperature':'Battery',
'Battery voltage':'Battery',
'Battery capacity SOC':'Battery',
'Empty Register':'',
'PV1 input power':'PV',
'PV2 input power':'PV',
'Empty Register':'',
'Empty Register':'',
'Battery output power':'Battery',
'Battery output current':'Battery',
'Load frequency':'Load',
'Inverter output frequency':'Inverter',
'Grid side relay status':'Grid',
'Generator side relay status':'Generator',
'Generator relay Frequency':'Generator',
'Empty Register':'',
'Empty Register':'',
'Empty Register':'',
'Control Mode':'Configuration',
'Equalization V':'Configuration',
'Absorption V':'Configuration',
'Float V':'Configuration',
'Batt Capacity':'Configuration',
'Batt Empty':'Configuration',
'Zero Export Power':'Configuration',
'Equalization day cycle':'Configuration',
'Equalization time':'Configuration',
'TEMPCO':'Configuration',
'Max A Charge from PV or Grid':'Configuration',
'Max A discharge from Batt':'Configuration',
'Empty Register':'',
'Battery operates according to voltage or SOC':'Configuration',
'Lithium battery wake up sign bit Activate Batt':'Configuration',
'Battery resistance value':'Configuration',
'Battery charging efficiency':'Configuration',
'Battery capacity Shut Down':'Configuration',
'Battery capacity Restart':'Configuration',
'Battery capacity Low Batt':'Configuration',
'Battery voltage Shut Down':'Configuration',
'Battery voltage Restart':'Configuration',
'Battery voltage Low Batt':'Configuration',
'Maximum operating time of generator':'Configuration',
'Generator cooling time':'Configuration',
'Generator charging Starting voltage point':'Configuration',
'Generator charging starting capacity point':'Configuration',
'Generator battery charging current':'Configuration',
'Grid charging Start voltage point':'Configuration',
'Grid charging start capacity point':'Configuration',
'Grid battery charging current':'Configuration',
'Generator charging enable':'Configuration',
'Grid charging enable':'Configuration',
'Solar Input as PSU':'Configuration',
'Force Smart load ON':'Configuration',
'Generator input is enabled as Smart load output':'Configuration',
'Smart Load OFF batt Voltage':'Configuration',
'Smart Load OFF batt':'Configuration',
'Smart Load ON batt Voltage':'Configuration',
'Smart Load ON batt':'Configuration',
'Empty Register':'',
'Minimum solar power required to start Smart load when connected to Grid':'Configuration',
'Gen Grid Signal On':'Configuration',
'Energy management model':'Configuration',
'Empty Register':'',
'Limit the maximum power output of the grid connection':'Configuration',
'Empty Register':'',
'Grid sell':'Configuration',
'Time of Use Selling enabled':'Configuration',
'Empty Register':'',
'Sell mode time point 1':'Configuration',
'Sell mode time point 2':'Configuration',
'Sell mode time point 3':'Configuration',
'Sell mode time point 4':'Configuration',
'Sell mode time point5':'Configuration',
'Sell mode time point6':'Configuration',
'Sell mode time point 1 power':'Configuration',
'Sell mode time point 2 power':'Configuration',
'Sell mode time point 3 power':'Configuration',
'Sell mode time point 4 power':'Configuration',
'Sell mode time point 5 power':'Configuration',
'Sell mode time point 6 power':'Configuration',
'Sell mode time point 1 voltage':'Configuration',
'Sell mode time point 2 voltage':'Configuration',
'Sell mode time point 3 voltage':'Configuration',
'Sell mode time point 4 voltage':'Configuration',
'Sell mode time point 5 voltage':'Configuration',
'Sell mode time point 6 voltage':'Configuration',
'Point 1 capacity':'Configuration',
'Point 2 capacity':'Configuration',
'Point 3 capacity':'Configuration',
'Point 4 capacity':'Configuration',
'Point 5 capacity':'Configuration',
'Point 6 capacity':'Configuration',
'Time point 1 charge enable':'Configuration',
'Time point 2 charge enable':'Configuration',
'Time point 3 charge enable':'Configuration',
'Time point 4 charge enable':'Configuration',
'Time point 5 charge enable':'Configuration',
'Time point 6 charge enable':'Configuration',
'AC Coupled export to grid cutoff':'Configuration',
'External CT sensor directional detection':'Configuration',
'Restore connection time':'Configuration',
'Solar Arc Fault Mode turned on':'Configuration',
'Grid Mode':'Configuration',
'Grid Frequency Setting':'Configuration',
'Grid Type':'Configuration',
'Grid Vol High':'Configuration',
'Grid Vol Low':'Configuration',
'Grid Hz High':'Configuration',
'Grid Hz Low':'Configuration',
'Generator connected to GRID input':'Configuration',
'GEN peak shaving Power':'Configuration',
'Grid Connect/Disconnect':'Configuration',
'Parallel register 1':'Configuration'
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
    listAddress=[]
    dicc={}
    for i in pr['data']:
        dicc[i['name']]=i['register'] 
    for i in pr['data']:
        listAddress.append(i['register'])
    listAddress.sort()
    listOut=[]
    listOut1=[]
    i=0
    a=1
    while True:
        if listAddress[i]==a:
            listOut.append(listAddress[i])
            i+=1
            a+=1
        else:
            listOut1.append(listOut.copy())
            listOut.clear()
            a=listAddress[i]    
        if i==len(listAddress):
            listOut1.append(listOut.copy())
            break
    regs={}
    a=0
    if c.open():
        for i in listOut1:
            modbusList=c.read_holding_registers(i[0],len(i))
            for e in modbusList:
                regs[listAddress[a]]=e
                a+=1
        c.close()
    else:
        pr['data'] = ''
    try:
        for i in pr['data']:
            i['value'] = regs[i['register']]
            i['category'] = i['name']
    except:
            i['value'] = None
    return pr['data']

@web.get('/', response_class=HTMLResponse)
async def main(request: Request):
    #dataRegisters=updateRegisters()
    with open('settings_clinet.yml', 'r') as file:
        pr = safe_load(file)
    context = {'request': request, 'data': pr['data']}
    return templates.TemplateResponse('index.html', context=context)

@web.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await manager.broadcast(updateRegisters())
    except WebSocketDisconnect:
        manager.disconnect(websocket)