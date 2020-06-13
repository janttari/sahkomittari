#!/usr/bin/env python3
# sudo pip3 install websocket-client
import RPi.GPIO as GPIO
import time, os, sys, socket, threading, websocket, configparser, urllib.parse

#----------------------------------------------------------------
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(skriptinHakemisto+'/sahkomittari.ini')
PALVELIN=config['yleiset']['palvelin']
PULSSIPINNI=int(config['yleiset']['pulssipinni'])
imp=int(config['yleiset']['imp'])
BOUNCETIME=int(config['yleiset']['bouncetime'])
MAXTIHEYS=float(config['yleiset']['maxtiheys'])
ALIVE=float(config['yleiset']['alive'])
pulssiPysyva=config['yleiset']['pulssipysyva']
tallennaPulssiSek=float(config['yleiset']['tallennapulssisek'])
yks=1000/imp #yksi pulssi on näin monta wattia
GPIO.setmode(GPIO.BCM) #pinnien numerointi https://www.raspberrypi-spy.co.uk/2012/06/simple-guide-to-the-rpi-gpio-header-and-pins/
GPIO.setup(PULSSIPINNI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #käytetään sisäistä alasvetoa
pulssiLaskuri=0 #lasketaan tähän muuttujaan pulssit
edLahetysAika=0 #Edellisen kerran lähetetty palvelimelle dataa aikaleima
edPulssi=0 #Edellisen kerran saadun pulssin aikaleima
tallennettuPulssi=0 #Viimeisin tiedostoon tallennettu pulssilukema, ettei turhaan kirjoitella jos se ei ole muuttunut

def logprint(asia):
    print(asia)
    pass

def reconnect(): #Uudelleenyhdistää katkenneen yhteyden sulkemalla wsasiakas-threadin ja avaamalla sen uudelleen
    global threadWsAsiakas
    threadWsAsiakas.join()
    time.sleep(1)
    logprint("reconnect")
    threadWsAsiakas=threading.Thread(target=wsasiakas)
    threadWsAsiakas.start()

def on_open(ws): #Tämä suoritetaan kun ws-yhteyn on avattu
    pass #Ei tehdä nyt mitään

def on_message(ws, message): #Tämä suoritetaan kun serveri lähettää meillepäin dataa
    #if message=="getKonffi":
    #    getKonffi()
    pass

def on_error(ws, error):
    logprint(error)

def on_close(ws): #Tämä tapahtuu kun yhteys on katkennut
    logprint("### closed ##base64#")
    reconnect() #Yritetään avata yhteys uudelleen

def laheta(sanoma): #Lähetä sanoma serverille päin
    try:
        ws.send(sanoma)
    except: #Jos lähetys ei onnistu...
        logprint("Virhe viestin lähetyksessä!")
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

def lahetaKulutus(info=""): #Lähetetään selaimille kwh-lukema ja nykyinen kulutus
    global edLahetysAika, pulssiLaskuri, edPulssi
    kwh="{:.5f}".format(pulssiLaskuri*yks/1000) #Yhteensä kulutusta kertynyt kW
    ero=time.time()-edPulssi #edellisen pulssin ja nykyisen pulssin välillä on kulunut n sekuntia
    if info == "": #Mieti tää fiksummin, ihan paskaa purkkaa. Tarkoitus kuitenkin on että edellisen pulssin aikaa ei nollata alive-viestien kohdalla
        edPulssi=time.time()
    reaaliaikainen="{:.5f}".format(1000/yks/ero/1000) #kulutusta on tällä hetkellä kW
    if info != "" or edLahetysAika == 0 or time.time()-edLahetysAika>MAXTIHEYS: #Lähetetään vain sallitulla tiheydellä
        rivi='{"kwh": "'+kwh+'", "pulssit": "'+str(pulssiLaskuri)+'", "reaaliaikainen": "'+reaaliaikainen+'"'
        if info !="": #jos on ylimääräistä infoa lähetettäväksi, esim että tämä on vain alive viesti (alivessakin silti kannattaa lähettää lukemat, koska reaaliaikainen kulutushan mitataan edellisestä pulssista aikana
            rivi+=', "info": "'+info+'"'
        rivi+='}'
        laheta(rivi)
        edLahetysAika=time.time()

def onPulssi(channel): #tää suoritetaan aina kun pulssi tulee
    global pulssiLaskuri, edPulssi
    pulssiLaskuri+=1 #kasvatetaan laskurin määrää yhdellä
    lahetaKulutus()


#def getKonffi(): #Lähetetään palvelimelle config-tiedoston sisältö kun palvelin sitä pyytää
#    global skriptinHakemisto
#    print("GKK")
#    with open (skriptinHakemisto+'/sahkomittari.ini', "r") as fKonffi:
#        konffi=urllib.parse.quote(fKonffi.read())
#    rivi='{"asiakas": "'+ASIAKAS+'", "konffi": "'+konffi+'"}'
#    laheta(rivi)


if __name__ == "__main__":
    GPIO.add_event_detect(PULSSIPINNI, GPIO.RISING, callback=onPulssi, bouncetime=BOUNCETIME) #määritellään että kun GPIO-pinni saa pulssin, suoritetaan funktio my_Pulssi
    threadWsAsiakas=threading.Thread(target=wsasiakas)
    threadWsAsiakas.start()
    kierros=0
    if os.path.isfile(pulssiPysyva): #Jos on olemassa tallennettu pulssilukema
        with open(pulssiPysyva, "r") as pulssiTiedosto: #Luetaan pulssilukema tiedostosta
            pulssiLaskuri=int(pulssiTiedosto.read())
    while True: #Suoritetaan tätä looppia ja tehdään täällä säännöllisesti tarvittavat toiminnot
        if kierros % tallennaPulssiSek == 0 and tallennettuPulssi != pulssiLaskuri:
            print("tallenapulssi")
            #ws.close()
            #quit()
            tallennettuPulssi=pulssiLaskuri
            with open(pulssiPysyva, "w") as fpulssiTallenna: #tallennetaan pulssien määrä pysyväksi
                fpulssiTallenna.write(str(pulssiLaskuri))
        if time.time()-edLahetysAika >ALIVE and kierros !=0: #ei lähetetä heti ekalla kerralla kun socket tuskin on vielä auki...
            edLahetysAika=time.time()
            lahetaKulutus("alive") #lähetetään alive viesti
        time.sleep(1)
        kierros+=1



