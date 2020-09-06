#!/usr/bin/env python3
#
# Websocket-server callbackillä
#

from websocket_server import WebsocketServer #Käytetään muutettua luokkaa, jossa clients on objekti-kohtainen
from datetime import datetime
import time, threading, logging

class PalveluWs: #------------------------------------------------------------------------------------------------------------
    def __init__(self, portti, callback_on_message):
        self.portti=portti
        self.callback_on_message=callback_on_message
        self.t=threading.Thread(target=self.serveri)
        self.t.start()

    def lahetaKaikille(self,sanoma): #Lähetetään sanoma kaikille websocketin asiakkaille
        self.server.send_message_to_all(sanoma)

    def lahetaYksityinen(self, kohde, sanoma): #Lähetetään sanoma vain yhdelle ip:lle
        for l in self.server.clients:
            if kohde in l["address"][0]:
                self.server.send_message(l, sanoma)

    def serveri(self):
        self.server = WebsocketServer(self.portti, host='0.0.0.0', loglevel=logging.ERROR )
        #self.server.set_fn_new_client(self.new_client)
        #self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.callback_on_message)
        self.server.run_forever()    
