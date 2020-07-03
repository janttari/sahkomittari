#!/usr/bin/env python3
# sudo pip3 uninstall websocket_server
# sudo pip3 install git+https://github.com/Pithikos/python-websocket-server
# sudo pip3 install watchdog
#
# Valvoo /dev/shm/sahkomittari -hakemiston muutoksia. Kun tiedosto muuttuu, lähetetään sen sisältö selaimille websocketilla
#


import time, threading, os, logging, sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from websocket_server import WebsocketServer
from datetime import datetime

SHMHAKEMISTO="/dev/shm/sahkomittari-server"

def lokita(rivi):
    kello=time.strftime("%y%m%d-%H%M%S")
    print(kello, rivi)
    sys.stdout.flush()

def new_client(client, server):    #Uusi asiakas avannut yhteyden.
    print("liittyi " + str(client))

def client_left(client, server):    #selain katkaissut yhteyden.
    print("lahti " + str(client))

def message_received(client, server, message):    # SELAIMELTA SAAPUVA VIESTI
    print("msg_selaimelta " + str(client)+" "+str(message))

def lahetaBroadCast(viesti):    # LÄHETETÄÄN BROADCAST-VIESTI KAIKILLE
    server.send_message_to_all(viesti)

def wsSelaimille(): # TÄSSÄ KÄYNNISTETÄÄN VARSINAINEN WEBSOCKET
    global server
    server = WebsocketServer(8889, host='0.0.0.0', loglevel=logging.ERROR )
    server.set_fn_new_client(new_client)
    server.set_fn_client_left(client_left)
    server.set_fn_message_received(message_received)
    server.run_forever()


class Watcher: #Luokka valvoo muuttuneita tiedostoja
    DIRECTORY_TO_WATCH = SHMHAKEMISTO

    def __init__(self):
        self.observer = Observer()
        self.run()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")
        self.observer.join()

class Handler(FileSystemEventHandler): #Kun tiedostot SHM-hakemistossa muuttuneet
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None
        elif event.event_type == 'modified':
            lokita("Received modified event - %s." % event.src_path)
            aika=datetime.now().strftime("%H:%M:%S")
            ip=os.path.basename(event.src_path) 
            with open (event.src_path, "r") as fReaali:
                kulutus, reaaliaikainen, pulssit, info=fReaali.read().split(";")
                #print(ip,kulutus,reaaliaikainen,pulssit)
            lahetaBroadCast('{"elementit": [{"elementti": "nahty_'+ip+'", "arvo": "'+aika+'"}, {"elementti": "kwh_'+ip+'", "arvo": "'+kulutus+'"}, {"elementti": "reaali_'+ip+'", "arvo": "'+reaaliaikainen+'"}, {"elementti": "pulssit_'+ip+'", "arvo": "'+pulssit+'"}, {"elementti": "info_'+ip+'", "arvo" : "'+info+'"} ]}')

if __name__ == '__main__':
    os.makedirs( SHMHAKEMISTO, mode=0o777, exist_ok=True)
    threadWatchdogfiles = threading.Thread(target=Watcher)
    threadWatchdogfiles.start()
    threadWsSelaimille=threading.Thread(target=wsSelaimille)
    threadWsSelaimille.start()

    while True:
        #aika=datetime.now().strftime("%H:%M:%S")
        #demo1pulssit+=1
        #lahetaBroadCast('{"elementit": [{"elementti": "nahty_192.168.4.222", "arvo": "'+aika+'"},{"elementti": "kwh_192.168.4.222", "arvo": "'+str(demo1pulssit*1.25/1000)+'"}, {"elementti": "pulssit_192.168.4.222", "arvo": "'+str(demo1pulssit)+'"}]}')
        time.sleep(3)
