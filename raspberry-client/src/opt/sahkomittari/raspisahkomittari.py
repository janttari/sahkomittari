#!/usr/bin/env python3
#sudo pip3 install websocket-client
import time, os, sys, socket, threading, websocket, configparser
from multiprocessing import Process, Pipe
import RPi.GPIO as GPIO
#----------------------------------------------------------------
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(skriptinHakemisto+'/sahkomittari.ini')
PALVELIN=config['yleiset']['palvelin']
PULSSIPINNI=int(config['yleiset']['pulssipinni'])
imp=int(config['yleiset']['imp'])
maxLahetysTiheys=float(config['yleiset']['maxtiheys'])
maxAliveTiheys=float(config['yleiset']['alive'])
pulssiPysyva=config['yleiset']['pulssipysyva']
tallennaPulssiSek=float(config['yleiset']['tallennapulssisek'])
yks=1000/imp #yksi pulssi on näin monta wattia
pulssiLaskuri=0 #lasketaan tähän muuttujaan pulssit
edLahetysAika=0 #Edellisen kerran lähetetty palvelimelle dataa aikaleima
edPulssi=0 #Edellisen kerran saadun pulssin aikaleima
tallennettuPulssi=0 #Viimeisin tiedostoon tallennettu pulssilukema, ettei turhaan kirjoitella jos se ei ole muuttunut
viimLahetysaika=0 #websocketille on viimeksi lähetetty-aikaleima
viimLahetettyPulssi=-1 #viimeksi websocketille lähetetty pulssimäärä
kwh="" #kokonaiskulutus kwh
reaaliaikainen="" #reaaliaikainen kulutus tällä hetkellä
aja=True #liipaise tämä Falseksi niin lopetetaan

GPIO.setmode(GPIO.BCM) #https://www.raspberrypi-spy.co.uk/2012/06/simple-guide-to-the-rpi-gpio-header-and-pins/
GPIO.setup(PULSSIPINNI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #käytetään sisäistä alasvetoa

def luePinni(child_conn): #Lukee GPIO-pinniltä pulsseja. Tämä käynnistetään itsenäisenä prosessina
    global PULSSIPINNI
    while True:
        GPIO.wait_for_edge(PULSSIPINNI, GPIO.RISING) #odotetaan nouseva reuna
        child_conn.send(1) #Lähetetään että on saatu pulssi
        GPIO.wait_for_edge(PULSSIPINNI, GPIO.FALLING) #odotetaan laskeva reuna

def vastaanotaImpulssi(parent_conn): #Tämä säie vastaanottaa aina luvun 1 kun luePinni on lukenut pulssin
    global pulssiLaskuri, aja
    while aja:
        data=parent_conn.recv()
        if data != "stop": #Ohjelman alasajoon liityvä snoma
            pulssiLaskuri+=1
            laskeKulutus()

def laskeKulutus():
    global kwh, reaaliaikainen, edPulssi
    ero=time.time()-edPulssi #edellisen pulssin ja nykyisen pulssin välillä on kulunut n sekuntia
    edPulssi=time.time()
    kwh="{:.5f}".format(pulssiLaskuri*yks/1000) #Yhteensä kulutusta kertynyt kW
    reaaliaikainen="{:.5f}".format(1000/yks/ero/1000) #kulutusta on tällä hetkellä kW

def reconnect(): #Uudelleenyhdistää katkenneen yhteyden sulkemalla wsasiakas-threadin ja avaamalla sen uudelleen
    global threadWsAsiakas
    threadWsAsiakas.join()
    time.sleep(1)
    print("***reconnect")
    threadWsAsiakas=threading.Thread(target=wsasiakas)
    threadWsAsiakas.start()

def on_open(ws): #Tämä suoritetaan kun ws-yhteyn on avattu
    pass #Ei tehdä nyt mitään

def on_message(ws, message): #Tämä suoritetaan kun serveri lähettää meillepäin ws dataa
    pass

def on_error(ws, error): #ws virhe
    print("!!!",error)

def on_close(ws): #Tämä tapahtuu kun ws yhteys on katkennut
    print("*** closed")
    reconnect() #Yritetään avata yhteys uudelleen

def lahetaLukema(): #Tämä säie lähettää websocketille tiedot
    global aja, pulssiLaskuri, viimLahetettyPulssi, maxLahetysTiheys, maxAliveTiheys, viimLahetysaika, kwh, reaaliaikainen
    while aja:
        if pulssiLaskuri!= viimLahetettyPulssi and  time.time()-viimLahetysaika > maxLahetysTiheys: #pulssien määrä on muuttunut
            info = "-"
            viimLahetettyPulssi=pulssiLaskuri
            viimLahetysaika=time.time()
        elif time.time()-viimLahetysaika > maxAliveTiheys: #pulssit ei muuttuneet, alive-viesti
            info = "alive"
            viimLahetysaika=time.time()
        if info != "": #Jos on jotain lähetettävää...
            rivi='{"kwh": "'+kwh+'", "pulssit": "'+str(pulssiLaskuri)+'", "reaaliaikainen": "'+reaaliaikainen+'", "info": "'+info+'"}'
            lahetaWs(rivi)
            info=""
        time.sleep(0.05)

def lahetaWs(sanoma): #Lähetä sanoma serverille päin
    if kwh != "": #jos ei ole ohjelman esimmäinen suoritukierros, jolla ei vilä lähetettävää ole
        #print(sanoma)
        try:
            ws.send(sanoma)
        except: #Jos lähetys ei onnistu...
            print("!!! Virhe viestin lähetyksessä!")
            reconnect()#Pyydetään avaamaan ws uudelleen

def wsasiakas(): #Varsinainen ws-client. Suorita tähä threadina!
    global ws, PALVELIN
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(PALVELIN,
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close,
                              on_open = on_open)
    ws.run_forever()

def tallennaPulssi(): # Tallentaa pulssilukeman pysyväksi
    print("* tallenapulssi")
    tallennettuPulssi=pulssiLaskuri
    with open(pulssiPysyva, "w") as fpulssiTallenna: #tallennetaan pulssien määrä pysyväksi
        fpulssiTallenna.write(str(pulssiLaskuri))

if __name__ == "__main__":
    parent_conn, child_conn = Pipe() #Pinniä lukeva prosessi kommunikoi tän kautta
    threadWsAsiakas=threading.Thread(target=wsasiakas) #WS thread
    threadWsAsiakas.start()
    kasit=threading.Thread(target=vastaanotaImpulssi, args=(child_conn,)) #Vastaanottaa pulssit thread
    kasit.start()
    lahettelija=threading.Thread(target=lahetaLukema) #Lähettää pulssit palvelimelle thread
    lahettelija.start()
    process = Process(target=luePinni, args=(parent_conn,)) #Lukee pinnin tilan prosessi
    process.start()
    kierros=0
    if os.path.isfile(pulssiPysyva): #Jos on olemassa tallennettu pulssilukema
        with open(pulssiPysyva, "r") as pulssiTiedosto: #Luetaan pulssilukema tiedostosta
            pulssiLaskuri=int(pulssiTiedosto.read())
            laskeKulutus()
    try:
        while aja: #Suoritetaan tätä looppia ja tehdään täällä säännöllisesti tarvittavat toiminnot
            if kierros % tallennaPulssiSek == 0 and tallennettuPulssi != pulssiLaskuri and kierros !=0:
                tallennaPulssi()
            time.sleep(1)
            kierros+=1
    except KeyboardInterrupt: #Testikäytössä ohjelma on hankala sammuttaa, joudutaan vähän kikkailemaan
        print("LOPETETAAN")
        tallennaPulssi()
        aja=False
        ws.close()
        threadWsAsiakas.join()
        parent_conn.send("stop")
        kasit.join()
        lahettelija.join()
        process.terminate()
        GPIO.cleanup()
        print("LOPETETTU")



