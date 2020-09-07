#!/usr/bin/env python3
#!!! lisää python-serial riippuvuuksiin ja poista adafruit RPi.GPIO
#
import time, os, sys, socket, threading, websocket, configparser, serial, json, adafruit_dht
#import board
#----------------------------------------------------------------
DEBUG=False
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(skriptinHakemisto+'/sahkomittari.ini')

class Mittaaja(): # TÄMÄ LUOKKA HOITAA VARSINAISEN PINNIN LUKEMISEN JA KULUTUKSEEN LIITTYVÄN LASKENNAN --------------------------
    def __init__(self, callback):
        '''self, pulssipinni, viestikanava, pulssiValue, maxLahetysTiheys, maxAliveTiheys, imp_per_kwh'''
        self.callback=callback
        self.lampo=-123.0
        self.kosteus=-124.0
        self.edArduinonPulssiMaara=0 #edellinen arduinon ilmoittama pulssilukema jotta voidaan laskea lisäys
        self.sarjaportti=config['yleiset']['sarjaportti']
        self.pulssilaskuri = -1 #lasketaan tähän pulssit
        self.maxLahetysTiheys=float(config['yleiset']['maxtiheys'])
        self.maxAliveTiheys=float(config['yleiset']['alive'])
        self.imp=int(config['yleiset']['imp'])
        self.viimWsLahetys = 0 #unix aika, milloin on viimeksi lähetetty lukemat
        self.viimWsPulssiMaara = 0 #viimeisen lähetyksen pulssimäärä
        self.viimWsLahetysAika = 0  #viimeisimmän pulssin aikaleima
        self.sarjaporttiLukija = threading.Thread(target=self.lueSarjaportti) #Lukee pinnin tilan prosessi
        self.sarjaporttiLukija.start()
        if "lampopinni" in config['yleiset']:
            self.dhtDevice = adafruit_dht.DHT22(config['yleiset']['lampopinni'])
        else:
            self.dhtDevice=None
        self.lammonMittaaja = threading.Thread(target=self.lueLampoanturi)
        self.lammonMittaaja.start()

    def lahetaSarjaporttiin(self, luku): #kirjoittaa tavun sarjaporttiin daadaan luku 0..255
        Sending = bytearray([int(luku)])
        self.sp.write(Sending)

    def lueLampoanturi(self):
        time.sleep(5)
        lampo=-123.0
        kosteus=-65.4
        while True:
            if self.dhtDevice is not None:
                try:
                    lampo = self.dhtDevice.temperature
                    kosteus = self.dhtDevice.humidity
                except RuntimeError as error:
                    print("DHT lukuvirhe",error.args[0])
                    time.sleep(2.0)
                    continue
            rivi='{"lampo": "'+str(lampo)+'", "kosteus": "'+str(kosteus)+'"}'
            self.callback(rivi)
            time.sleep(60)


    def lueSarjaportti(self): #Varsinainen sarjaporttia lukeva osa
        self.sp=serial.Serial(port=self.sarjaportti, baudrate=57600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=10)
        time.sleep(1) #jotta konffi tallennettu pulssimäärä on ehditty lukemaan muistikortilta
        while True:
            sdata=self.sp.readline().decode().rstrip()
            if len(sdata)>=3:
                try:
                    if sdata[0] == "a" or "r":
                        palat=sdata.split(";")
                        pulssit=int(palat[1])
                        vali=float(palat[2])/1000
                        if self.edArduinonPulssiMaara != 0:
                            lisays=pulssit-self.edArduinonPulssiMaara
                            self.edArduinonPulssiMaara+=lisays
                            self.pulssilaskuri+=lisays
                        else:
                            self.edArduinonPulssiMaara= pulssit
                            lisays=0
                        if time.time()-self.viimWsLahetysAika >= self.maxAliveTiheys or self.viimWsLahetysAika==0: #ALIVE
                            self.viimWsLahetysAika=time.time()
                            self.viimWsPulssiMaara=self.pulssilaskuri
                            self.lahetaWs("alive", self.pulssilaskuri, vali)
                        elif time.time()-self.viimWsLahetysAika >= self.maxLahetysTiheys and self.viimWsPulssiMaara != self.pulssilaskuri: #PULSSIT MUUTTUNEET
                            self.lahetaWs("kulutus", self.pulssilaskuri, vali)
                            self.viimWsLahetysAika=time.time()
                            self.viimWsPulssiMaara=self.pulssilaskuri
                    time.sleep(0.05)
                except:
                    print("sarjaportista tuli paskaa, ohitettu!")

    def lahetaWs(self, tyyppi, pulssienMaara,pulssienVali): #lähetetään ws palvelimelle    
        tmpKwh="{:.5f}".format(pulssienMaara*1000/self.imp/1000) #kokonaiskulutus kwh
        tmpReaaliaikainen="{:.5f}".format(((1000/self.imp*3600)/pulssienVali)/1000) #kulutusta on tällä hetkellä kW
        #pääohjelman callback 'lahetaWsServerille' hoitaa varsinaisen lähetyksen websocketilla:
        rivi='{"kwh": "'+tmpKwh+'", "pulssit": "'+str(pulssienMaara)+'", "reaaliaikainen": "'+tmpReaaliaikainen+'", "info": "'+tyyppi+'"}'
        self.callback(rivi)

    def setPulssilukema(self, lukema): #Voidaan asettaa pulssien määrä
        self.pulssilaskuri=lukema

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

    def on_message(self, message):
        jmessage=json.loads(message)
        if "komento" in jmessage:
            tavu=jmessage["komento"]["tavu"]
            mittari.lahetaSarjaporttiin(tavu)

    def on_error(self, error):
        pass

    def on_close(self, ws):
        pass

    def on_open(self):
        pass

    def lahetaWs(self, sanoma):
        try:
            self.ws.send(sanoma)
        except: #jos lähetys ei onnistu
            self.reconnect() #Pyydetään avaamaan ws uudelleen

    def reconnect(self): #avaa ws uudelleen
        self.t.join()
        time.sleep(1)
        self.t=threading.Thread(target=self.wsYhteys)
        self.t.start()
#------------------------------------------------------------------------------------------------------------------------------------

def lahetaWsServerille(data): #Tämä kutsutaan kun pulssien saatu
    wsAsiakas.lahetaWs('{"raspilta": '+data+'}')

def tallennaPulssi(): # Tallentaa pulssilukeman pysyväksi
    #lokita("tallenapulssi pysyvään tiedostoon. lukema on nyt:"+str(mittari.getPulssilukema()))
    with open(config['yleiset']['pulssipysyva'], "w") as fpulssiTallenna: #tallennetaan pulssien määrä pysyväksi
        fpulssiTallenna.write(str(mittari.getPulssilukema()))

if __name__ == "__main__": #----------------------------------------------------------------------------------------------------------
    wsAsiakas=WsAsiakas()
    viimtallennettuPulssiAika=time.time() #aika jolloin pulssi on viimeksi tallennettu tiedostoon
    mittari=Mittaaja(lahetaWsServerille)
    time.sleep(0.5)
    if os.path.isfile(config['yleiset']['pulssipysyva']): #Jos on olemassa tallennettu pulssilukema
        with open(config['yleiset']['pulssipysyva'], "r") as pulssiTiedosto: #Luetaan pulssilukema tiedostosta
            mittari.setPulssilukema(int(pulssiTiedosto.read()))
    while True:
        if time.time() - viimtallennettuPulssiAika >= float(config['yleiset']['tallennapulssisek']):
            tallennaPulssi()
            viimtallennettuPulssiAika=time.time()
        time.sleep(3)
