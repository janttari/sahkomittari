#!/usr/bin/env python3
import time, os, sys, socket, threading, websocket, configparser
import RPi.GPIO as GPIO
from multiprocessing import Process, Value, Pipe
from datetime import datetime as dt
#----------------------------------------------------------------
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(skriptinHakemisto+'/sahkomittari.ini')

def lokita(rivi):
    kello=time.strftime("%y%m%d-%H%M%S")
    print(kello, rivi)
    sys.stdout.flush()

class Mittaaja(): # TÄMÄ LUOKKA HOITAA VARSINAISEN PINNIN LUKEMISEN JA KULUTUKSEEN LIITTYVÄN LASKENNAN --------------------------
    def __init__(self, viestikanava):
        '''self, pulssipinni, viestikanava, pulssiValue, maxLahetysTiheys, maxAliveTiheys, imp_per_kwh'''
        self.viestikanava=viestikanava
        self.pulssipinni=int(config['yleiset']['pulssipinni'])
        self.pulssilaskuri = Value("i", 0)#lasketaan tähän pulssit
        self.maxLahetysTiheys=float(config['yleiset']['maxtiheys'])
        self.maxAliveTiheys=float(config['yleiset']['alive'])
        self.imp=int(config['yleiset']['imp'])
        self.viimLahetys = 0 #unix aika, milloin on viimeksi lähetetty lukemat
        self.viimPulssimaara = 0 #viimeisen lähetyksen pulssimäärä
        self.viimPulssiAika = Value("d", 0)  #viimeisimmän pulssin aikaleima
        self.aikaaEdPulssista = Value("d", 1)
        self.pinninLukija = Process(target=self.luePinni, args=(self.pulssilaskuri , self.viimPulssiAika, self.aikaaEdPulssista, )) #Lukee pinnin tilan prosessi
        self.pinninLukija.start()
        self.valvoja=threading.Thread(target=self.valvoPulsseja)
        self.valvoja.start()

    def luePinni(self, pulssilaskuriPipe, viimPulssiAikaPipe, aikaaEdPulssistaPipe): #Varsinainen pinniä lukeva osa
        GPIO.setmode(GPIO.BCM) #https://www.raspberrypi-spy.co.uk/2012/06/simple-guide-to-the-rpi-gpio-header-and-pins/
        GPIO.setup(self.pulssipinni, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #käytetään sisäistä alasvetoa
        while True:
            GPIO.wait_for_edge(self.pulssipinni, GPIO.RISING) #odotetaan nouseva reunaa
            pulssilaskuriPipe.value+=1
            aikaaEdPulssistaPipe.value=float(time.time()-viimPulssiAikaPipe.value)
            viimPulssiAikaPipe.value=float(time.time())
            GPIO.wait_for_edge(self.pulssipinni, GPIO.FALLING) #odotetaan laskeva reuna
    
    def valvoPulsseja(self): #Tämä seuraa saapuvia pulsseja ja milloin pitää lähettää alive
        time.sleep(3) #Odotetaan hetki kunnes tallennetut lukemat on saatu varmasti
        while True:
            if (time.time()-self.viimLahetys>self.maxLahetysTiheys and self.viimPulssimaara != self.pulssilaskuri.value) or (time.time()-self.viimLahetys>self.maxAliveTiheys):
                self.viimLahetys=time.time()
                if self.viimPulssimaara != self.pulssilaskuri.value: #jos pulsseja on tullut
                    self.viimPulssimaara = self.pulssilaskuri.value
                    tmpInfo="kulutus"
                else:
                    tmpInfo="alive"
                    self.aikaaEdPulssista.value=float(time.time()-self.viimPulssiAika.value)
                tmpPulssit=int(self.pulssilaskuri.value)
                tmpKwh="{:.5f}".format(tmpPulssit*1000/self.imp/1000) #kokonaiskulutus kwh
                tmpReaaliaikainen="{:.5f}".format(((1000/self.imp*3600)/self.aikaaEdPulssista.value)/1000) #kulutusta on tällä hetkellä kW
                self.viestikanava.send((tmpPulssit, tmpKwh, tmpReaaliaikainen, tmpInfo)) #tuple (int pulssimäärä, str kokonaiskulutus, str reaaliaik, str info)            
            time.sleep(0.05)
            
    def setPulssilukema(self, lukema): #Voidaan asettaa pulssien määrä
        self.pulssilaskuri.value=lukema
        lokita("asetetaan mittarilukema: "+str(self.pulssilaskuri.value))
        
    def getPulssilukema(self):
        return self.pulssilaskuri

class WsAsiakas(): #-----------------------------------------------------------------------------------------------------
    def __init__(self):
        self.palvelin=config['yleiset']['palvelin']
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()

    def wsYhteys(self):
        websocket.enableTrace(False)
        self.ws = websocket.WebSocketApp(self.palvelin,
                                  on_message = self.on_message,
                                  on_error = self.on_error,
                                  on_close = self.on_close,
                                  on_open = self.on_open)
        self.ws.run_forever()
        
    def on_message(self, ws, message):
        pass

    def on_error(self, error):
        lokita("WS error: "+str(error))

    def on_close(self, ws):
        lokita("WS close")

    def on_open(self, ws):
        lokita("WS open")

    def lahetaWs(self, sanoma):
        try:
            self.ws.send(sanoma)
        except: #jos lähetys ei onnistu
            lokita("ws Virhe viestin lähetyksessä!")
            self.reconnect() #Pyydetään avaamaan ws uudelleen

    def reconnect(self): #avaa ws uudelleen
        self.t.join()
        time.sleep(1)
        lokita("***reconnect ws")
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
#------------------------------------------------------------------------------------------------------------------------------------

def vastaanotaImpulssi(parent): #Tämä kutsutaan kun pulssien saatu
    while True:
        pulssimaara, kwh, reaaliaik, info=parent.recv()
        rivi='{"kwh": "'+kwh+'", "pulssit": "'+str(pulssimaara)+'", "reaaliaikainen": "'+reaaliaik+'", "info": "'+info+'"}'
        wsAsiakas.lahetaWs(rivi)

def tallennaPulssi(): # Tallentaa pulssilukeman pysyväksi
    lokita("tallenapulssi pysyvään tiedostoon")
    with open(config['yleiset']['pulssipysyva'], "w") as fpulssiTallenna: #tallennetaan pulssien määrä pysyväksi
        fpulssiTallenna.write(str(mittari.getPulssilukema()))
                
if __name__ == "__main__": #----------------------------------------------------------------------------------------------------------
    childPipe, parentPipe = Pipe()
    wsAsiakas=WsAsiakas()
    viimtallennettuPulssiAika=time.time() #aika jolloin pulssi on viimeksi tallennettu tiedostoon
    mittari=Mittaaja(childPipe)
    vastottaja=threading.Thread(target=vastaanotaImpulssi, args=(parentPipe,))
    vastottaja.start()
    time.sleep(0.5)
    if os.path.isfile(config['yleiset']['pulssipysyva']): #Jos on olemassa tallennettu pulssilukema
        lokita("lue kulutus tiedostosta")
        with open(config['yleiset']['pulssipysyva'], "r") as pulssiTiedosto: #Luetaan pulssilukema tiedostosta
            mittari.setPulssilukema(int(pulssiTiedosto.read()))
    while True:
        if time.time() - viimtallennettuPulssiAika >= float(config['yleiset']['tallennapulssisek']):
            tallennaPulssi()
            viimtallennettuPulssiAika=time.time()
        time.sleep(3)
