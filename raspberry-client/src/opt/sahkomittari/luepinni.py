#!/usr/bin/env python3
PULSSIPINNI=24
import multiprocessing
import RPi.GPIO as GPIO

def monitorChannel(channel):
    while True:
        GPIO.wait_for_edge(channel, GPIO.RISING)
        print(str(channel) + "ylös")
        GPIO.wait_for_edge(channel, GPIO.FALLING)
        print(str(channel) + "alas")



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PULSSIPINNI, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 
monitorChannel(PULSSIPINNI)
