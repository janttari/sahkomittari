#!/usr/bin/env python3
# sudo pip3 uninstall websocket_server
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
#
# Vastaanottaa portissa 5007 ohjelmien sisäiseltä socketilta dataa ja lähettää sen edelleen ulospäin näkyvälle websocketille (selaimien käyttöön)
#



import time, threading, os, logging, sys, json
from datetime import datetime
from Viestit import Viestit
from websocket_server import WebsocketServer

DEBUG=False

def lokita(rivi):
    if DEBUG:
        kello=time.strftime("%y%m%d-%H%M%S")
        tamaskripti=os.path.basename(__file__)
        with open ("/var/log/sahkomittarilokit.txt", "a") as lkirj:
            lkirj.write(kello+" "+tamaskripti+": "+rivi+"\n")

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    pass
    #print("liittyi " + str(client))

def client_left(client, server):    #selain katkaissut yhteyden.
    pass
    #print("lahti " + str(client))

def message_received(client, server, message):    # SELAIMELTA SAAPUVA VIESTI
    #print("msg_selaimelta " + str(client)+"!!! "+str(message))
    jdata=json.loads(message)
    if "komento" in jdata:
        sisalto=str(jdata["komento"])
        v.laheta(message) #Lähetetään komento edelleen raspberryjä palvelevalle serverille, joka ohjaa datan sitten mittaraspille

def lahetaBroadCast(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)
    lokita( "lähetetään selaimille "+ viesti) #qqq

def wsSelaimille(): # TÄSSÄ KÄYNNISTETÄÄN VARSINAINEN WEBSOCKET
    global server
    server = WebsocketServer(8889, host='0.0.0.0', loglevel=logging.ERROR )
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

def on_sanoma(data): #sahkomittari-server lähettää tähän dataa
    aika=datetime.now().strftime("%H:%M:%S")
    jdata=json.loads(data)
    if "wsdataselaimille" in jdata:
        ip=list(jdata["wsdataselaimille"])[0]
        sisalto=jdata["wsdataselaimille"][ip]
        riviselaimille='{"elementit": ['
        riviselaimille+='{"elementti": "nahty_'+ip+'", "arvo": "'+aika+'"}, '
        if "kwh" in sisalto:
            kwh=sisalto["kwh"]
            riviselaimille+='{"elementti": "kwh_'+ip+'", "arvo": "'+kwh+'"}, '
        if "reaaliaikainen" in sisalto:
            reaali=sisalto["reaaliaikainen"]
            riviselaimille+='{"elementti": "reaali_'+ip+'", "arvo": "'+reaali+'"}, '
        if "pulssit" in sisalto:
            pulssit=sisalto["pulssit"]
            riviselaimille+='{"elementti": "pulssit_'+ip+'", "arvo": "'+pulssit+'"}, '
        if "info" in sisalto:
            info=sisalto["info"]
            riviselaimille+='{"elementti": "info_'+ip+'", "arvo": "'+info+'"}, '
        if "lampo" in sisalto:
            lampo=sisalto["lampo"]
            riviselaimille+='{"elementti": "lampo_'+ip+'", "arvo": "'+lampo+'"}, '
        if "kosteus" in sisalto:
            kosteus=sisalto["kosteus"]
            riviselaimille+='{"elementti": "kosteus_'+ip+'", "arvo": "'+kosteus+'"}, '
        riviselaimille=riviselaimille[:-2] #viimeinen pilkku ja välilyönti pois
        riviselaimille+=']}'
        lahetaBroadCast(riviselaimille)

if __name__ == '__main__':
    v=Viestit(on_sanoma) # Tää vastaanottaa varsinaisen sähkömittari serverin välittämää dataa selaimille edelleen
    threadWsSelaimille=threading.Thread(target=wsSelaimille)
    threadWsSelaimille.start()

    while True:
        #aika=datetime.now().strftime("%H:%M:%S")
        #demo1pulssit+=1
        #lahetaBroadCast('{"elementit": [{"elementti": "nahty_192.168.4.222", "arvo": "'+aika+'"},{"elementti": "kwh_192.168.4.222", "arvo": "'+str(demo1pulssit*1.25/1000)+'"}, {"elementti": "pulssit_192.168.4.222", "arvo": "'+str(demo1pulssit)+'"}]}')
        time.sleep(3)
