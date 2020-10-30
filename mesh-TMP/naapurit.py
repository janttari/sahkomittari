#!/usr/bin/env python3
import subprocess, time

def tamaLaite():
    omaIP = subprocess.getoutput('ifconfig |grep bat0 -a1|tail -n1 |cut -d " " -f10')
    omaMAC = subprocess.getoutput('sudo batctl n|head -n1|cut -d " " -f5|cut -d "/" -f2')
    return(omaMAC,omaIP)

def naapurit():
    #print("OMA IP: "+omaIP, omaMAC)

    naapuritraaka = subprocess.getoutput('sudo batctl n -H').split("\n")
    tmpnaapurit=[]
    for n in naapuritraaka:
        nmac = n[0:17]
        naika = n[20:26]
        nteho = n[36:40]
        #print(nmac,naika,nteho)
        tmpnaapurit.append((nmac,naika,nteho))
    return tmpnaapurit # [('00:c0:ca:98:8f:9f', ' 0.500', ' 7.8'), ('00:c0:ca:98:8e:ed', ' 0.190', '35.6')]


tama=tamaLaite()
print("TÄMÄ LAITE MAC:",tama[0],"IP:",tama[1])
n=naapurit()
for i in n:
    print("MAC:",i[0],"AIKA:",i[1],"TEHO:",i[2])

