#!/usr/bin/env python3
# sudo pip3 install websocket-client
import RPi.GPIO as GPIO
import time, os, sys, socket, threading, websocket

#----------------------------------------------------------------
ASIAKAS="testiraspi" #Tämän laitteen asiakastunnus. Tää voi olla vähän turha, koska websocket_server client kertoo lähettäjän "address"
PALVELIN='ws://192.168.4.150:8888/' #Palvelin johon otetaan yhteys
PULSSIPINNI=24 #luetaan tästä GPIO-pinnistä pulssi
imp=800 #pulssien määrä per kwh
BOUNCETIME=300 #painonapilla tapahtuvaan testailuun 300 sopiva, mittarille sopiva ???
MAXTIHEYS=1.5 #Lähetä korkeintaan näin tiheästi (sekuntia)
ALIVE=10.0 #Lähetetään alive-sanoma jos muuta lähetystä ei ole näin pitkään aikaan ollut (sekuntia)
pulssiPysyva="/opt/sahkomittari/pulssi" #Tähän tallennetaan säännöllisin väliajoin pulssilukema
tallennaPulssiSek=3 #Tallenna pulssi tiedostoon joka n sekunti
#----------------------------------------------------------------

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
    logprint(message)

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
        rivi='{"asiakas": "'+ASIAKAS+'", "kwh": "'+kwh+'", "pulssit": "'+str(pulssiLaskuri)+'", "reaaliaikainen": "'+reaaliaikainen+'", "info": "'+info+'"}'
        laheta(rivi)
        edLahetysAika=time.time()

def onPulssi(channel): #tää suoritetaan aina kun pulssi tulee
    global pulssiLaskuri, edPulssi
    pulssiLaskuri+=1 #kasvatetaan laskurin määrää yhdellä
    lahetaKulutus()

if __name__ == "__main__":
    GPIO.add_event_detect(PULSSIPINNI, GPIO.RISING, callback=onPulssi, bouncetime=BOUNCETIME) #määritellään että kun GPIO24 saa pulssin, suoritetaan funktio my_Pulssi
    threadWsAsiakas=threading.Thread(target=wsasiakas)
    threadWsAsiakas.start()
    kierros=0
    if os.path.isfile(pulssiPysyva): #Jos on olemassa tallennettu pulssilukema
        with open(pulssiPysyva, "r") as pulssiTiedosto: #Luetaan pulssilukema tiedostosta
            pulssiLaskuri=int(pulssiTiedosto.read())
    while True:
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



