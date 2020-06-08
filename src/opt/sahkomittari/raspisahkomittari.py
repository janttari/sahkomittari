#!/usr/bin/env python3
import RPi.GPIO as GPIO
import flaskpalvelin
import time, os, sys

#----------------------------------------------------------------
PULSSIPINNI=24 #luetaan tästä GPIO-pinnistä pulssi
imp=800 #pulssien määrä per kwh
BOUNCETIME=300 #painonapilla tapahtuvaan testailuun 300 sopiva, mittarille sopiva ???
#----------------------------------------------------------------

yks=1000/imp #yksi pulssi on näin monta wattia
GPIO.setmode(GPIO.BCM) #pinnien numerointi https://www.raspberrypi-spy.co.uk/2012/06/simple-guide-to-the-rpi-gpio-header-and-pins/
GPIO.setup(PULSSIPINNI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #käytetään sisäistä alasvetoa
laskuri=0 #lasketaan tähän muuttujaan pulssit


def on_liittyi(data): #flask-asiakas liittyi
    lahetaKwhJson() #Lähetetään heti asiakkaalle nykyinen kulutuslukema

def on_poistui(data): #flask-asiakas poistui
    pass

def on_selaimelta(data): #selain lähetti meille dataa
    pass

def lahetaKwhJson(): #Lähetetään selaimille kwh-lukema
    global laskuri
    kwh="{:.5f}".format(laskuri*yks/1000)
    lahetettava='[{"elementti": "kwh", "arvo": "'+kwh+'", "vari": "white"}]'
    flask.elemArvot(lahetettava)

def onPulssi(channel): #tää suoritetaan aina kun pulssi tulee
    global laskuri
    laskuri+=1 #kasvatetaan laskurin määrää yhdellä
    lahetaKwhJson()


GPIO.add_event_detect(PULSSIPINNI, GPIO.RISING, callback=onPulssi, bouncetime=BOUNCETIME) #määritellään että kun GPIO24 saa pulssin, suoritetaan funktio my_Pulssi

if __name__ == "__main__":
    flask=flaskpalvelin.FlaskPalvelin()
    while True:
        time.sleep(1)

