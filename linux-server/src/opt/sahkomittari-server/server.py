#!/usr/bin/env python3
# sudo pip3 uninstall websocket_server
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
#
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
# vaiko git clone ja setup??

SHMHAKEMISTO="/dev/shm/sahkomittari" # tänne tallentuu reaaliaikainen kulutustieto www-pavelinta ja muuta käyttöä varten. Ei säily rebootin jälkeen
TALLENNAPYSYVA="/opt/sahkomittari-server/data" #Tänne kirjoitetaan pysyvät tiedot, jotka säilyy rebootin jälkeenkin.

from websocket_server import WebsocketServer
from datetime import datetime
import time, threading, logging, sys, os, json, logging

viimTallennusaika="" #Tähän kirjoitetaan milloin pysyvät tiedostot on viimeksi tallennettu HH
kwhMuisti={} # {'192.168.4.222': '0.45250'}
pulssiMuisti={}

logger = logging.getLogger('websocket_server.WebsocketServer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    global luelukkotiedosto
    print("Uusi asiakas liittynyt tunnuksella %d" % client['id'])

def client_left(client, server):    #AINA KUN SELAIN KATKAISSUT YHTEYDEN
    pass    # Ei tehdä nyt mitään
    print("lähti %d" % client['id'])

def message_received(client, server, message):    # SELAIMELTA SAAPUVA VIESTI
    asiakasIP, asiakasPortti=(client["address"])
    print(asiakasIP)
    jsmessage=json.loads(message)
    #if not ("info" in jsmessage.keys() and "alive" in jsmessage.get("info")): #jos ei ole pelkkä alive tieto:
    kwh=jsmessage.get("kwh")
    pulssit=jsmessage.get("pulssit")
    reaaliaikainen=jsmessage.get("reaaliaikainen")
    info=jsmessage.get("info","-")
    kwhMuisti[asiakasIP]=kwh
    pulssiMuisti[asiakasIP]=pulssit
    with open(SHMHAKEMISTO+"/"+asiakasIP, "w") as fReaaliaikainen:
        fReaaliaikainen.write(kwh+";"+reaaliaikainen+";"+pulssit) #/dev/shm/sahkomittari/192.168.4.222 --> 0.44625;0.54517;357 //kwh,reaaliaik kulutus, pulssien määrä
    print("arvo",asiakasIP,kwh,pulssit,reaaliaikainen,info)
    print(kwhMuisti)
    print(pulssiMuisti)

def laheta(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)

def kuuntelija(): # TÄSSÄ KÄYNNISTETÄÄN VARSINAINEN WEBSOCKET
    global server

    server = WebsocketServer(8888, host='0.0.0.0', loglevel=logging.ERROR )
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

def tallennaPysyvat():
    aika=aika=datetime.now().strftime("%Y%m%d-%H%M%S") #20200614-120002
    for asiakasIP in kwhMuisti: #käydään kaikki asiakkaa läpi yksi kerrallaan
        with open (TALLENNAPYSYVA+"/"+asiakasIP, "a") as fTallennaPysyva: #/opt/sahkomittari-server/data/192.168.4.222
            fTallennaPysyva.write(aika+";"+kwhMuisti[asiakasIP]+";"+pulssiMuisti[asiakasIP]+"\n") #20200614-120002;357
    
    print("**TALLENNA")

if __name__ == "__main__":    # PÄÄOHJELMA ALKAA
    os.makedirs( SHMHAKEMISTO, mode=0o777, exist_ok=True)
    os.makedirs( TALLENNAPYSYVA, mode=0o777, exist_ok=True )
    t=threading.Thread(target=kuuntelija)
    t.start()

    kierros=0
    while True: # PÄÄLOOPPI
        time.sleep(1)
        kello=time.strftime("%H")
        if kello != viimTallennusaika and kierros!=0: #Jos tunti on vaihtunut:
            tallennaPysyvat()
            viimTallennusaika=kello
        else:
            if kierros==0:               #jos on ohjelman ensimmäinen suorituskierros, mitään tallennettavaa ei vielä voi olla
                viimTallennusaika=kello
                print("eka kierros")
        if kierros%10==0:
            aika=datetime.now().strftime("%H:%M:%S")
            laheta("server lähettää "+aika)
            print(kierros)
            #tallennaPysyvat() #qqq testi
        kierros+=1
