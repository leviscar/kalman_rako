# -*- coding: utf-8 -*-
# TOA experiment
import UWB_Kalman
import numpy as np

def readdata(TS,accel):
    fd=open('experiment_data\\TOAdata1.txt','r')
    try: 
        while True:
            Tstmp=np.zeros(4)    
            for i in range(4):
                s=fd.readline()
                Tstmp[i]=int(s.split()[3])
            TS.append(Tstmp)    
            acceltmp=np.zeros((100,2))    
            for i in range(100):
                s=fd.readline().split()
                acceltmp[i,0]=float(s[0])
                acceltmp[i,1]=float(s[1])
            accel.append(acceltmp)
    except (EOFError,IndexError):
        pass
    fd.close()
    
def checkmpudata(accel):
    accelx=accel[:,0]
    accely=accel[:,1]
    accelx=accelx.ravel()
    accely=accely.ravel()
    zerocountx=list(accelx).count(0)
    zerocounty=list(accely).count(0)
    
    if zerocountx>30 or zerocounty>30:
        return False
    else:
        if accelx[0]==0:
            for idx,ac in enumerate(accelx):
                if ac!=0:
                    break
            accelx[0:idx+1]=accelx[idx+1]
            
        if accelx[-1]==0:
            tmp=list(accelx)
            tmp.reverse()
            tmp=np.array(tmp)
            for idx,ac in enumerate(tmp):
                if ac!=0:
                    break
            tmp[0:idx+1]=tmp[idx+1]    
            tmp=list(accelx)
            tmp.reverse()
            accelx=np.array(tmp)
        
        iszero=0
        startidx=0
        
        while True:
            for idx1,ac in enumerate(accelx[startidx:]):
                if ac==0:
                    iszero=1
                    break   
            if iszero:    
                for idx2,ac in enumerate(accelx[idx1:]):
                    if ac!=0:
                        break         
                accelx[idx1:idx2+1]=(accelx[idx1-1]+accelx[idx2+1])/2
            else:
                break
            startidx=idx2+1    

        if accely[0]==0:
            for idx,ac in enumerate(accely):
                if ac!=0:
                    break
            accely[0:idx+1]=accely[idx+1]
            
        if accely[-1]==0:
            tmp=list(accely)
            tmp.reverse()
            tmp=np.array(tmp)
            for idx,ac in enumerate(tmp):
                if ac!=0:
                    break
            tmp[0:idx+1]=tmp[idx+1]    
            tmp=list(accely)
            tmp.reverse()
            accely=np.array(tmp)
        
        iszero=0
        startidx=0
        
        while True:
            for idx1,ac in enumerate(accely[startidx:]):
                if ac==0:
                    iszero=1
                    break   
            if iszero:    
                for idx2,ac in enumerate(accely[idx1:]):
                    if ac!=0:
                        break         
                accely[idx1:idx2+1]=(accely[idx1-1]+accely[idx2+1])/2
            else:
                break
            startidx=idx2+1              
        
        accel[:,0]=accelx
        accel[:,1]=accely
        return True

def checkuwbdata(dis):
    cnt=0
    for i in dis:
        if i>0.001:
            cnt+=1
    if cnt>=3:
        return True
    else:
        return False
    
DIS=[]
ACCEL=[]
readdata(DIS,ACCEL)
datacnt=len(DIS)

dt_IMU=0.01
dt_UBW=1
Anchor_num=4
Anchor_pos=np.array([[0,0],
                 [10,0],
                 [0,10],
                 [10,10]])
std_a=0.02
std_r=0.1
sigma_a=std_a**2
sigma_r=std_r**2

ekf=UWB_Kalman.EKF.RAKOEKF(sigma_a,sigma_r,Anchor_pos,Anchor_num,dt_IMU,dt_UBW)


for i in range(datacnt):
    Dis=DIS[i]
    Accel=ACCEL[i]
    mpuvalid=checkmpudata(Accel)
    uwbvalid=checkuwbdata(Dis)
    plot_x=[]
    plot_y=[]
    if mpuvalid and uwbvalid:
        postmp=ekf.ekffilter(Accel,Dis)
        plot_x.append(postmp[0])
        plot_y.append(postmp[1])
    elif not mpuvalid and uwbvalid:
        postmp=ekf.LSQ_TOA(Dis)
        ekf.StatusLast[0,0]=postmp[0]
        ekf.StatusLast[1,0]=postmp[1]
        plot_x.append(postmp[0])
        plot_y.append(postmp[1])        
        
    elif not mpuvalid and not uwbvalid:
        pass
    elif mpuvalid and not uwbvalid:
        pass
        
    
    