#!/usr/bin/env python3
#!!! lisää python-serial riippuvuuksiin ja poista adafruit RPi.GPIO
#
import time, os, sys, socket, threading, websocket, configparser, serial, json


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
        self.lammonMittaaja = threading.Thread(target=self.lueLampoanturi)
        self.lammonMittaaja.start()

    def lahetaSarjaporttiin(self, luku): #kirjoittaa tavun sarjaporttiin daadaan luku 0..255
        Sending = bytearray([int(luku)])
        self.sp.write(Sending)

    def lueLampoanturi(self):
        time.sleep(5)
        while True:
            rivi='{"lampo": "-111.1", "kosteus": "-222.2"}'
            self.callback(rivi)
            time.sleep(60)

class WsAsiakas(): #-----------------------------------------------------------------------------------------------------
    def __init__(self):
        self.palvelin='ws://192.168.4.222:8888'
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

    def on_message(client, server, message):
        print("DATAA tuli", message)
        #jmessage=json.loads(message)
        #if "komento" in jmessage:
        #    tavu=jmessage["komento"]["tavu"]
        #    mittari.lahetaSarjaporttiin(tavu)

    def on_error(self, error):
        print("WS error: "+str(error))

    def on_close(self, ws):
        print("WS close")

    def on_open(self):
        print("WS open")

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
    wsAsiakas.lahetaWs('{"raspilta": '+data+'}')


if __name__ == "__main__": #----------------------------------------------------------------------------------------------------------
    wsAsiakas=WsAsiakas()

    while True:
        time.sleep(3)
