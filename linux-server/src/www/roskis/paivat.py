#!/usr/bin/env python3
#tulostetaan joka päivän viimeisin lukema ja sen lisäksi tämän päivän viimeisin mittaus
#
import os, subprocess
def tulostaLukema(raakaRivi):
    paivays, kwh,pulssit=raakaRivi.split(";")
    yy=paivays[2:4]
    mm=paivays[4:6]
    dd=paivays[6:8]
    hh=paivays[9:11]
    mm=paivays[11:13]
    print("%s-%s-%s %s:%s %s <br>"%(yy,mm,dd,hh,mm,kwh))

print ("Content-type:text/html\r\n\r\n")
print ('<html>')
print ('<head>')
print ('<title>Päiväkohtainen</title>')
print ('</head>')
print ('<body>')
IPos=os.environ.get("QUERY_STRING")
process=subprocess.Popen(["./ip_to_numeronimiip", IPos], stdout=subprocess.PIPE)
laite, err= process.communicate()
laite=laite.decode().rstrip()
print("<h1>"+laite+"</h1><br>")
with open("/opt/sahkomittari-server/data/"+IPos, "r") as fLukemat:
    lukemat=fLukemat.readlines()

viimpv=""
for l in range(1,len(lukemat)):
    lukema=lukemat[l]
    pv=lukema[:8] #20200611
    if pv !=viimpv:
        if viimpv!="":
            tulostaLukema(lukemat[l-1])
    viimpv=pv
tulostaLukema(lukemat[l]) #tulostetaan vielä tämän päivän viimeisin saatu luku
print ('</body>')
print ('</html>')
