#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
import datetime
import subprocess
import time
import os
import datetime as dt
from datetime import datetime, timedelta
from timeit import default_timer as timer
import math
import numpy as np

import paramiko

host = "114.29.154.250"
#host = "bit2farm.iptime.org"

port = 29979

ids = "pheno"
pwd = "kist1966!!!"

# 로컬경로
localPath = "/home/pi/"
#localPath = ""

# 서버경로
serverPath = "/var/www/cams/static/ircam/"
#serverPath = ""

# 파일명
fileName1 = "rgb_ir.jpg"
fileName2 = "B2F_CAMs_1000000000001.jpg"

paramiko.util.log_to_file(localPath + '/sftp.log')

import serial

PORT ='/dev/ttyACM0'
BaudRate = 115200
time_delay1 = 0.2 # 1sec
test = serial.Serial(PORT, BaudRate, bytesize=8, parity='N', stopbits=1, timeout=None, xonxoff=0, rtscts=0)

TIME_INTERVAL = 30          # time interval between data transmission
loop_max = 3

LAI = 2.5             # Leaf Area Index
h_level = 52    # Elevation above sea level : h_level [m], west sea area 0.1m, KIST SmartFarm 52m, suwon 38m

##################################################################################
def Evp_func(Tleaf, Tair, RH, Is, CO2_ppm):
    # Leaf_temperature : Tleaf, Air_temperature : Tair, Rative Humidity : RH, Solar Irradiation : Is, CO2(ppm) : CO2_ppm, LAI
    Tleaf = Tleaf
    Tair = Tair    
    RH = RH
    Is = Is
    CO2_ppm = CO2_ppm
    
    # Kelvin Air temperature : TairK, CO2(vpm) : CO2_vpm
    # Latent heat of vaporization of water : Laheat
    # Roh a * Cp : RoaCp
    # Atmospheric Pressure : Patm
    # Slope of the saturation vapor pressure : Slope_vapor
    # Psychometric constant : PsyConst
    # Saturation vapor pressure : VPD  [Pa]
    # Linearization factor of radiation heat flux equation : rR
    # DelTemp = Tair - Tleaf : DelTemp
    # External resistance : ResiExt (l = 15cm, u = 30cm)
    TairK = float(Tair) + 273.16
    CO2_vpm = float(CO2_ppm)*100000/(586.26*float(TairK))
    Laheat = 2502535.259 - 2385.76 * float(Tair)
    RoaCp = 3.5296e5/ float(TairK)
    Patm = 101325*(1 - 0.0065*float(h_level)/ 293)**5.26
    Slope_vapor = 4.415*math.exp(6.088e-3 * float(Tair))
    PsyConst = 1.6297e3*float(Patm)/float(Laheat)
    VPD = 610.78*math.exp(17.269*float(Tair)/(237.3+float(Tair)))*(1-float(RH)/100)
    rR = float(RoaCp)/(2.2676e-7*(float(TairK))**3)
    DelTemp = float(Tair) - float(Tleaf)
    ResiExt = 1174*0.15**0.5/(0.15*abs(float(DelTemp))+207*0.3**2)**0.25

    # Internal resistance : ResiInt = ResiInt_Is*ResiInt_CO2*ResiInt_VPD
    ## ResiInt_Is
    ResiInt_Is = 82.0*(float(Is)+4.30)*(1+2.3e-2*(float(Tleaf)-24.5)**2)/(float(Is)+0.54)
    ## ResiInt_CO2
    if float(Is) < 30:
        ResiInt_CO2 = 1
    elif float(CO2_vpm) < 1100:
        ResiInt_CO2 = 1+6.1e-7*(float(CO2_vpm) - 200)**2
    else:
        ResiInt_CO2 = 1.5
    ## ResiInt_VPD
    if float(VPD) < 800:
        ResiInt_VPD = 1 + 4.3*(float(VPD)/1000)**2
    else:
        ResiInt_VPD = 3.8

    ResiInt = float(ResiInt_Is)*float(ResiInt_CO2)*float(ResiInt_VPD)

    # Resistance star: ResiStar, Coeff, Rns term, Rnl term, VPD term
    ResiStar = (1+float(ResiInt)/float(ResiExt))
    Coef = 2*float(RoaCp)*float(LAI)/(float(Laheat)*(float(PsyConst)*float(ResiStar)+float(Slope_vapor)))
    RsTerm = 0.07*float(Slope_vapor)*float(Is)/float(RoaCp)
    RlTerm = 0.16*float(Slope_vapor)*float(DelTemp)/float(rR)
    VPDTerm = float(VPD)/float(ResiExt)

    # Evaportranspiration rate: ETc_rate kg/m2/s]
    ETc_rate = float(Coef)*(float(RsTerm) + float(RlTerm) + float(VPDTerm))

    # Evaportranspiration amount : ETc_amount, 1kg -> ml : 1000, crop growing density, 2.5 [ml/corp/s]
    ETc_amount = 400*float(ETc_rate)
    cETc_rate = "%.4e" %ETc_rate #print "Evaportranspiration rate : %s kg/m2/s" %str(cETc_rate)
    cETc_amount = "%.4e" %ETc_amount #print "Evaportranspiration amount : %s ml/crop/s" %str(cETc_amount)
    cVPD = "%.2f" %VPD #print "VPD : %s Pa" %str(cVPD)

    ##############################################################################
    # Potential water vapor : PWV
    aux1=8.07131-1730.63/(233.426+float(Tair))
    PWV = 10**float(aux1)

    # Humidity deficit (HD, g/m3)
    HD = float(PWV)-float(RH)*float(PWV)/100
    cHD = "%2.2f" %HD    
    
    return ETc_amount, VPD, HD



##### data structure
def merge_dic(x, y):
    z = x
    z.update(y)
    return z




##### MAIN LOOP

while True:
    time.sleep(time_delay1)
    now = time.localtime()
    
    if ((now.tm_sec) % TIME_INTERVAL == 0):
        tmp_str = datetime.now().strftime('%Y%m%d')
        tmp_str2 = datetime.now().strftime('%H:%M:%S')
        print("%02d:%02d:%02d" %(now.tm_hour, now.tm_min, now.tm_sec))
        loop_num = 0;
        T = 0
        H = 0
        D = 0
        C = 0
        L = 0
        
        while loop_num < loop_max:
            time.sleep(time_delay1)
            test.write(b'AT\r\n')
            time.sleep(time_delay1)

            result = test.readline()
            T = T + float(result[2:8].decode())
            
            time.sleep(time_delay1)
            result = test.readline()
            H = H + float(result[2:8].decode())
            
            time.sleep(time_delay1)
            result = test.readline()
            D = D + float(result[2:8].decode())
            
            time.sleep(time_delay1)
            result = test.readline()
            C = C + float(result[2:6].decode())
 
            time.sleep(time_delay1)
            result = test.readline()
            L = L + float(result[2:8].decode())
            loop_num = loop_num + 1

        T = T/loop_num
        H = H/loop_num
        D = D/loop_num
        C = C/loop_num
        L = L/loop_num

        # Leaf_temperature : Tleaf, Solar Irradiation : Is, Air_temperature : Tair, Kelvin Air temperature : TairK, Rative Humidity : RH, CO2(ppm) : CO2_ppm
        # Temperature, Humidity, Dew Point, CO2 concentration

        Tair = T
        RH = H
        Dp = D
        CO2_ppm = C
                
        # Intensity of Lighting
        Is = L
        
        # Leaf Temperature
        file_name = "/home/pi/data/Thermal.txt"
        
        if os.path.isfile(file_name):
            output = subprocess.check_output(['tail', '-n 1', file_name], universal_newlines=True)
            Leaf = output.strip().split(',')
            Tleaf = float(Leaf[0])
                
        else :
            print("No Thermal file !!")
            Tleaf = T
        
        transpiration, vpd, hd = Evp_func(Tleaf, Tair, RH, Is, CO2_ppm)
        print("Tleaf:%.1f,Is:%.1f,Tair:%.1f,RH:%.1f,Dp:%.1f,CO2_ppm:%.1f,Transpiration:%.1f,hd:%.1f,vpd:%.1f\n" %(Tleaf,Is,Tair,RH,Dp,CO2_ppm,transpiration,hd,vpd))
        f = open("/home/pi/data/%04d%02d%02d_data.txt" % (now.tm_year, now.tm_mon, now.tm_mday), 'a+')
        f.write("%02d:%02d:%02d,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n" %(now.tm_hour, now.tm_min, now.tm_sec, Tleaf,Is,Tair,RH,Dp,CO2_ppm,transpiration,hd,vpd))
        f.close()        
        
        try :
                ##### DB Server connection ############################################################################
                myclient =  pymongo.MongoClient('bit2farm.iptime.org',27111,username='CAMs',password='best', authSource='DB_CAMs')
                #######################################################################################################

                ##### Sub collection list in DB_CAMs #######################################################
                mydb = myclient["DB_CAMs"]
                ############################################################################################

                ##### Data Column ##########################################################################
                mycol = mydb["sensors"]
                ############################################################################################

                ###### Data DB Feeding Part ################################################################
                base_val = {'FarmName':'B2F', 'SN':'B2F_CAMs_1000000000001', 'Date':tmp_str, 'Time':tmp_str2}
                gen_val={'Leaf_Temp':str(Tleaf), 'Light':str(Is), 'Air_Temp':str(Tair), 'Humidity':str(RH), 'Dewpoint':str(Dp), 'CO2':str(CO2_ppm), 'EvapoTranspiration':str(transpiration), 'HD':str(hd), 'VPD':str(vpd) }
                input_val = merge_dic(base_val, gen_val)
                x = mycol.insert_one(input_val) #DB inserting
                ################################################################################################
                # 접속
                transport = paramiko.Transport((host, port))
                print(transport.getpeername())
                
                transport.connect(username = ids, password = pwd)
                sftp = paramiko.SFTPClient.from_transport(transport)
                sftp.put(localPath + fileName1, serverPath + fileName2)
                print("Transfer Success")
        except:
                print("fail to send")

        finally:
                sftp.close()
                transport.close()

test.close()
