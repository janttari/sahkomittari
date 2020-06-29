#!/usr/bin/env python3 
# sudo pip3 uninstall websocket_server sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
#
# Tässä ei ole ws-palvelua selaimelle. tehdään siitä kokonaan oma ohjelma tietoturvan vuoksi! se skripti voi käyttää /dev/shm ja inotify
#

from websocket_server import WebsocketServer
from datetime import datetime
import time, threading, logging, sys, os, json, logging, urllib.parse, sqlite3


SHMHAKEMISTO="/dev/shm/sahkomittari-server" # tänne tallentuu reaaliaikainen kulutustieto www-pavelinta ja muuta käyttöä varten. Ei säily rebootin jälkeen
kulutusTietokanta=os.getcwd()+"/opt/sahkomittari-server/data/kulutus.db"

viimTallennusaika="" #Tähän kirjoitetaan milloin pysyvät tiedostot on viimeksi tallennettu HH
kwhMuisti={} # {'192.168.4.222': '0.45250'}
pulssiMuisti={} #ip:pulssit
mittariRaspit={} #Tässä liittyneenä olevat mittari-raspit ip:ws_client
logger = logging.getLogger('websocket_server.WebsocketServer')
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.StreamHandler())

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    pass
    #print(client)

def client_left(client, server):    #kun mittariraspi tai selain on katkaisssut yhteyden
    pass
    #asiakasIP, asiakasPortti=(client["address"])
    #if asiakasIP in mittariRaspit: #tämä asiakas oli raspi
    #    mittariRaspit.pop(client)

def message_received(client, server, message):    # RASPILTA SAAPUVA VIESTI
    #print(message)
    asiakasIP, asiakasPortti=(client["address"])
    jsmessage=json.loads(message)
    if "konffi" in jsmessage: # asiakas lähettää konffitiedostonsa tänne qEI-KÄYTÖSSÄ
        konffi=urllib.parse.unquote(jsmessage["konffi"])   # qEI-KÄYTÖSSÄ
        print(asiakasIP, "-->", konffi)    #  qEI-KÄYTÖSSÄ
    else: #kulutuslukemia tai alive tulee
        kwh=jsmessage.get("kwh")
        pulssit=jsmessage.get("pulssit")
        reaaliaikainen=jsmessage.get("reaaliaikainen")
        info=jsmessage.get("info","-")
        kwhMuisti[asiakasIP]=kwh
        pulssiMuisti[asiakasIP]=pulssit
        with open(SHMHAKEMISTO+"/"+asiakasIP, "w") as fReaaliaikainen:
            fReaaliaikainen.write(kwh+";"+reaaliaikainen+";"+pulssit+";"+info) #/dev/shm/sahkomittari/192.168.4.222 --> 0.44625;0.54517;357 //kwh,reaaliaik kulutus, pulssien määrä

def lahetaBroadCast(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)

def lahetaRaspeille(viesti): #Lähetetään kaikille raspeille
    pass

def lahetaYksityinen(laite, viesti): #lähetetään yksittäiselle laitteelle viesti
    server.send_message(laite, viesti)

def kuuntelija(): # TÄSSÄ KÄYNNISTETÄÄN VARSINAINEN WEBSOCKET
    global server
    server = WebsocketServer(8888, host='0.0.0.0', loglevel=logging.ERROR )
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

def tallennaPysyvat(): # muuta tää sqllitelle!
    #aika=aika=datetime.now().strftime("%Y%m%d-%H%M%S") #20200614-120002
    aika=str(int(time.time())) #unix-aikaleima
    conn = sqlite3.connect("/opt/sahkomittari-server/data/kulutus.db")
    c = conn.cursor()
    for asiakasIP in kwhMuisti: #käydään kaikki asiakkaa läpi yksi kerrallaan
        c.execute('INSERT into kulutus(aikaleima, ip, kwh, pulssit) VALUES('+aika+', "'+asiakasIP+'", '+kwhMuisti[asiakasIP]+', '+pulssiMuisti[asiakasIP]+')')
        #with open (TALLENNAPYSYVA+"/"+asiakasIP, "a") as fTallennaPysyva: #/opt/sahkomittari-server/data/192.168.4.222
        #    fTallennaPysyva.write(aika+";"+kwhMuisti[asiakasIP]+";"+pulssiMuisti[asiakasIP]+"\n") #20200614-120002;357
    conn.commit()
    conn.close()
    #print("**TALLENNA")

if __name__ == "__main__":    # PÄÄOHJELMA ALKAA
    conn = sqlite3.connect("/opt/sahkomittari-server/data/kulutus.db")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS kulutus (aikaleima INTEGER, ip TEXT , kwh REAL, pulssit INTEGER)')
    conn.commit()
    conn.close()
    #os.makedirs( SHMHAKEMISTO, mode=0o777, exist_ok=True)
    #os.makedirs( TALLENNAPYSYVA, mode=0o777, exist_ok=True )
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
                #print("eka kierros")
        #if kierros%10==0:
        #    aika=datetime.now().strftime("%H:%M:%S")
        #    #lahetaSelaimille('{"elementit": [{"elementti": "192.168.4.222_kwh", "arvo": "'+aika+'"},{"elementti": "192.168.4.150_kwh", "arvo": "12.3"}]}')
        #    print(kierros)
        #    #tallennaPysyvat() #qqq testi
        kierros+=1
