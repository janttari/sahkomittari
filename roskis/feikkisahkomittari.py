#!/usr/bin/env python3
# sudo pip3 install RPi.GPIO
# Tää antaa feikkidataa pinnille emuloiden sähkömittarin pulssia. yhdistä pinni gpio21 ja gpio24
pinni=21
import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(pinni, GPIO.OUT)

laskuri=0
while True:
    GPIO.output(pinni, GPIO.HIGH)
    laskuri+=1
    print(laskuri)
    time.sleep(0.09)
    GPIO.output(pinni, GPIO.LOW)
    time.sleep(1)


