#!/usr/bin/env python3
#!!! lisää python-serial riippuvuuksiin ja poista adafruit RPi.GPIO
#
import time, os, sys, socket, threading, websocket, configparser, serial

#----------------------------------------------------------------
DEBUG=False
skriptinHakemisto=os.path.dirname(os.path.realpath(__file__)) #Tämän skriptin fyysinen sijainti configia varten
config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
config.read(skriptinHakemisto+'/sahkomittari.ini')

def lokita(rivi):
    if DEBUG:
        kello=time.strftime("%y%m%d-%H%M%S")
        tamaskripti=os.path.basename(__file__)
        with open ("/var/log/sahkomittarilokit.txt", "a") as lkirj:
            lkirj.write(kello+" "+tamaskripti+": "+rivi+"\n")

class Mittaaja(): # TÄMÄ LUOKKA HOITAA VARSINAISEN PINNIN LUKEMISEN JA KULUTUKSEEN LIITTYVÄN LASKENNAN --------------------------
    def __init__(self, callback):
        '''self, pulssipinni, viestikanava, pulssiValue, maxLahetysTiheys, maxAliveTiheys, imp_per_kwh'''
        self.callback=callback
        #self.lampo=-123.0
        #self.kosteus=-124.0
        self.edArduinonPulssiMaara=0 #edellinen arduinon ilmoittama pulssilukema jotta voidaan laskea lisäys
        self.sarjaportti=config['yleiset']['sarjaportti']
        self.lampoMitattu=0 # aikaleima viimeisestä lämpömittauksesta
        self.pulssilaskuri = -1 #lasketaan tähän pulssit
        self.maxLahetysTiheys=float(config['yleiset']['maxtiheys'])
        self.maxAliveTiheys=float(config['yleiset']['alive'])
        self.imp=int(config['yleiset']['imp'])
        self.viimWsLahetys = 0 #unix aika, milloin on viimeksi lähetetty lukemat
        self.viimWsPulssiMaara = 0 #viimeisen lähetyksen pulssimäärä
        self.viimWsLahetysAika = 0  #viimeisimmän pulssin aikaleima
        self.sarjaporttiLukija = threading.Thread(target=self.lueSarjaportti) #Lukee pinnin tilan prosessi
        self.sarjaporttiLukija.start()

    def lueSarjaportti(self): #Varsinainen sarjaporttia lukeva osa
        sp=serial.Serial(port=self.sarjaportti, baudrate=57600,parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=10)
        time.sleep(1) #jotta konffi tallennettu pulssimäärä on ehditty lukemaan muistikortilta
        while True:
            sdata=sp.readline().decode().rstrip()
            if len(sdata)>=-5:
                try:
                    if sdata[0] == "a" or "r":
                        palat=sdata.split(";")
                        pulssit=int(palat[1])
                        vali=float(palat[2])/1000
                        lampo=float(palat[4])
                        kosteus=float(palat[5])
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
                            self.lahetaWs("alive", self.pulssilaskuri, vali, lampo, kosteus)
                        elif time.time()-self.viimWsLahetysAika >= self.maxLahetysTiheys and self.viimWsPulssiMaara != self.pulssilaskuri: #PULSSIT MUUTTUNEET
                            self.lahetaWs("kulutus", self.pulssilaskuri, vali, lampo, kosteus)
                            self.viimWsLahetysAika=time.time()
                            self.viimWsPulssiMaara=self.pulssilaskuri
                    time.sleep(0.05)
                except:
                    print("sarjaportista tuli paskaa, ohitettu!")

    def lahetaWs(self, tyyppi, pulssienMaara,pulssienVali, lampo, kosteus): #lähetetään ws palvelimelle    
        tmpKwh="{:.5f}".format(pulssienMaara*1000/self.imp/1000) #kokonaiskulutus kwh
        tmpReaaliaikainen="{:.5f}".format(((1000/self.imp*3600)/pulssienVali)/1000) #kulutusta on tällä hetkellä kW
        tmpLampo="{:.2f}".format(lampo)
        tmpKosteus="{:.2f}".format(kosteus)
        #pääohjelman callback 'lahetaWsServerille' hoitaa varsinaisen lähetyksen websocketilla:
        self.callback((pulssienMaara, tmpKwh, tmpReaaliaikainen, tyyppi, lampo, kosteus)) #tuple (int pulssimäärä, str kokonaiskulutus, str reaaliaik, str info)

    def setPulssilukema(self, lukema): #Voidaan asettaa pulssien määrä
        self.pulssilaskuri=lukema
        lokita("asetetaan mittarilukema: "+str(self.pulssilaskuri))

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

def lahetaWsServerille(data): #Tämä kutsutaan kun pulssien saatu
    pulssimaara, kwh, reaaliaik, info, lampo, kosteus = data
    rivi='{"kwh": "'+kwh+'", "pulssit": "'+str(pulssimaara)+'", "reaaliaikainen": "'+reaaliaik+'", "info": "'+info+'", "lampo": "'+str(lampo)+'", "kosteus": "'+str(kosteus)+'"}'
    wsAsiakas.lahetaWs(rivi)

def tallennaPulssi(): # Tallentaa pulssilukeman pysyväksi
    lokita("tallenapulssi pysyvään tiedostoon. lukema on nyt:"+str(mittari.getPulssilukema()))
    with open(config['yleiset']['pulssipysyva'], "w") as fpulssiTallenna: #tallennetaan pulssien määrä pysyväksi
        fpulssiTallenna.write(str(mittari.getPulssilukema()))

if __name__ == "__main__": #----------------------------------------------------------------------------------------------------------
    wsAsiakas=WsAsiakas()
    viimtallennettuPulssiAika=time.time() #aika jolloin pulssi on viimeksi tallennettu tiedostoon
    mittari=Mittaaja(lahetaWsServerille)
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
