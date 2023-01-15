# from pyModbusTCP.client import ModbusClient
from datetime import datetime

class WilAPI:
    def __init__(self):
        self.init_p1 = 0
        self.init_p2 = 0
        self.listSeparate=[]

    def __separate(self,data:list):
        for i in data:
            res=bin(i).replace("0b","").zfill(16)
            self.listSeparate.append([int(res[1:8], 2),int(res[9:16], 2)])
        return self.listSeparate

    def calculate(self,result:list):
        re=self.__separate(result)
        year='20'+str(re[0][0])
        temp = datetime(int(year),re[0][1],re[1][0],re[1][1]) 
        if (self.init_p1 == 0 and temp.hour == 0 and (temp.weekday()==5 or temp.weekday()==0) ) or self.init_p2 == 0:
            self.init_p1 = 1
            self.init_p2 = 1
            OnPeak_Init=1600
            Onpeak_End=2100
            Super_Off_Peak_Init_1=0000
            Super_Off_Peak_Init_3=1000
            Super_Off_Peak_End_1=600
            Super_Off_Peak_End_2=1400
            Super_Off_Peak_End_3=1400
            Power_Descarga=2000
            Lim_Min_Batt=30
            PCurrent=50
            if temp.weekday()==5 or temp.weekday()==6:
                P2soc=100
                P2Charge=0
                P2Power=2000
                P2Time=Super_Off_Peak_End_2
                P3soc=100
                P3Charge=0
                P3Power=2000
                P3Time=Super_Off_Peak_End_2
                P4soc=100
                P4Charge=0
                P4Power=2000
                P4Time=Super_Off_Peak_End_2
            else:
                P2soc=100
                P2Charge=0
                P2Power=2000
                P2Time=Super_Off_Peak_End_1
                if temp.month == 3 or temp.month == 4:
                    P3soc=100
                    P3Charge=0
                    P3Power=2000
                    P3Time=Super_Off_Peak_Init_3
                    P4soc=100
                    P4Charge=0
                    P4Power=2000
                    P4Time=Super_Off_Peak_End_3
                else:
                    P3soc=100
                    P3Charge=0
                    P3Power=2000
                    P3Time=Super_Off_Peak_End_1
                    P4soc=100
                    P4Charge=0
                    P4Power=2000
                    P4Time=Super_Off_Peak_End_1
            P1soc=100
            P1Charge=1
            P1Power=2000
            P1Time=Super_Off_Peak_Init_1
            P5soc=Lim_Min_Batt
            P5Charge=1
            P5Power=Power_Descarga
            P5Time=OnPeak_Init
            P6soc=100
            P6Charge=0
            P6Power=2000
            P6Time=Onpeak_End
            values_to_write = [P1Time, P2Time, P3Time, P4Time, P5Time, P6Time, P1Power, P2Power, P3Power, P4Power, P5Power, P6Power]
            values_to_write1 = [P1soc, P2soc, P3soc, P4soc, P5soc, P6soc, P1Charge, P2Charge, P3Charge, P4Charge, P5Charge, P6Charge]
            return [{'register':250,'value':values_to_write},{'register':268,'value':values_to_write1},{'register':230,'value':PCurrent}]
        else:
            return []
peakShaving=WilAPI()