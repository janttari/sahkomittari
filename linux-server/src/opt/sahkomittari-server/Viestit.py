import socket, threading, time, struct

# Luokka joka lähettää lähiverkossa multicast-viestejä eri koneiden välillä.
# Voidaan käyttää ohjelmien väliseen tiedonsiirtoon eri ohjelmien ja koneiden välillä.
# Sanoma on pelkkä str, jonka käsittely jää vastaanottajan tehtäväksi.
# 
# Anna parametrina vähintään callback, jonne kirjoitetaan vastaanotettu viesti.
# Valinnaisina parametreinä PORTTI ja IS_BROADCAST=False
#
#
# Esimerkkikoodi testi.py **************************************************************
##!/usr/bin/env python3
#from Viestit import Viestit
#import time
#
#def on_sanoma(rivi): #Tämä suoritetaan kun viesti on vastaanotettu.
#    print("saatu",rivi)
#
##v=Viestit(on_sanoma,5555) #Käytä haluttua porttia
#v=Viestit(on_sanoma) #Käytä oletusporttia 5007
#while True:
#    time.sleep(1)
#    v.laheta("pöytäkone lähettää")
#
# ***************************************************************************************
class Viestit():
    def __init__(self, callback, PORTTI=5007, IS_BROADCAST=True):
        self.callback=callback
        self.MCAST_GRP = '224.1.1.1'
        self.MCAST_PORT = PORTTI
        self.IS_BROADCAST = IS_BROADCAST
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.MCAST_PORT))
        mreq = struct.pack("4sl", socket.inet_aton(self.MCAST_GRP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        kuuntelija=threading.Thread(target=self.kuuntelija)
        kuuntelija.start()

    def kuuntelija(self):
        while True:
            data=self.sock.recv(10240)
            self.callback(data.decode())


    def laheta(self, sanoma):
        if self.IS_BROADCAST:
            self.sock.sendto(sanoma.encode(), (self.MCAST_GRP, self.MCAST_PORT))
        else:
            self.sock.sendto(sanoma.encode(), ('', self.MCAST_PORT))
