#!/usr/bin/env python3
# sudo pip3 uninstall websocket_server
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
#
SHMHAKEMISTO="/dev/shm/sahkomittari" # tänne tallentuu reaaliaikainen kulutustieto www-pavelinta ja muuta käyttöä varten. Ei säily rebootin jälkeen
TALLENNAPYSYVA="/opt/sahkomittari-server/data" #Tänne kirjoitetaan pysyvät tiedot, jotka säilyy rebootin jälkeenkin.

from websocket_server import WebsocketServer
from datetime import datetime
import time, threading, logging, sys, os, json, logging, urllib.parse, sqlite3
tietokanta=os.getcwd()+"/raspisahkomittari.db" #Tietokanta on samassa hakemistossa kuin tämä skriptikin
viimTallennusaika="" #Tähän kirjoitetaan milloin pysyvät tiedostot on viimeksi tallennettu HH
kwhMuisti={} # {'192.168.4.222': '0.45250'}
pulssiMuisti={} #ip:pulssit
mittariRaspit={} #Tässä liittyneenä olevat mittari-raspit ip:ws_client
selaimet=[] #Tässä liittyneenä olevat www-selaimet  ws_client:ip
logger = logging.getLogger('websocket_server.WebsocketServer')
logger.setLevel(logging.CRITICAL)
logger.addHandler(logging.StreamHandler())

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    global mittariRaspit
    ip, portti=client['address'] #asiakkaan ip ja portti
    conn = sqlite3.connect(tietokanta) #Tarkistetaan onko kyseinen laite mittari-raspberry...
    cursor=conn.execute('SELECT EXISTS(SELECT * from asiakkaat where ip="'+ip+'")')
    if cursor.fetchone()[0]>0: #Laite on mittari-raspberry
        mittariRaspit[ip]=client
    else: #Laite on jokin muu, eli www-selain
        selaimet.append(client)
    conn.close()

def client_left(client, server):    #kun mittariraspi tai selain on katkaisssut yhteyden
    asiakasIP, asiakasPortti=(client["address"])
    if client in selaimet: #tämä asiakas oli selain
        #selaimet.pop(str(client)) #poistetaan se selaimista
        for a in range(0, len(selaimet)):
            if selaimet[a] == client:
                selaimet.pop(a)
    elif asiakasIP in mittariRaspit: #tämä asiakas oli raspi
        mittariRaspit.pop(client)

def message_received(client, server, message):    # SELAIMELTA SAAPUVA VIESTI
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
            fReaaliaikainen.write(kwh+";"+reaaliaikainen+";"+pulssit) #/dev/shm/sahkomittari/192.168.4.222 --> 0.44625;0.54517;357 //kwh,reaaliaik kulutus, pulssien määrä
        #print("arvo",asiakasIP,kwh,pulssit,reaaliaikainen,info)
        #print(kwhMuisti)
        #print(pulssiMuisti)
        aika=datetime.now().strftime("%H:%M:%S")
        #aika="<font color='red'>"+aika+"</font>"
        lahetaSelaimille('{"elementit": [{"elementti": "'+asiakasIP+'_kwh", "arvo": "'+kwh+'"},{"elementti": "'+asiakasIP+'_nahty", "arvo": "'+aika+'"}]}') #kulutustiedot heti selaimen näytettäväksi

def lahetaBroadCast(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)

def lahetaSelaimille(viesti): #Lähetetään kaikille www-selaimille
    for selain in selaimet:
        server.send_message(selain, viesti)

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
            #lahetaSelaimille('{"elementit": [{"elementti": "192.168.4.222_kwh", "arvo": "'+aika+'"},{"elementti": "192.168.4.150_kwh", "arvo": "12.3"}]}')
            print(kierros)
            #tallennaPysyvat() #qqq testi
        kierros+=1
