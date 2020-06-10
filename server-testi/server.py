#!/usr/bin/env python3
# sudo pip3 uninstall websocket_server
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
#
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
# vaiko git clone ja setup??

from websocket_server import WebsocketServer
from datetime import datetime
import time, threading, logging, sys, os
import logging
logger = logging.getLogger('websocket_server.WebsocketServer')
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    global luelukkotiedosto
    print("Uusi asiakas liittynyt tunnuksella %d" % client['id'])

def client_left(client, server):    #AINA KUN SELAIN KATKAISSUT YHTEYDEN
    pass    # Ei tehdä nyt mitään
    print("lähti %d" % client['id'])

def message_received(client, server, message):    # SELAIMELTA SAAPUVA VIESTI
    #smessage=base64.b64decode(message).decode()
    #smessage=message.encode("iso-8859-1").decode("utf-8")
    print("saatiin>>>"+message+"<<<")
    #laheta("Palvelin vastaanotti viestin:"+message)

def laheta(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)

def kuuntelija(): # TÄSSÄ KÄYNNISTETÄÄN VARSINAINEN WEBSOCKET
    global server

    server = WebsocketServer(8888, host='0.0.0.0', loglevel=logging.ERROR )
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()

if __name__ == "__main__":    # PÄÄOHJELMA ALKAA
    t=threading.Thread(target=kuuntelija)
    t.start()

    kierros=0
    while True: # PÄÄLOOPPI
        time.sleep(1)
        if kierros%10==0:
            aika=datetime.now().strftime("%H:%M:%S")
            laheta("server lähettää "+aika)
            print(kierros)
        kierros+=1
