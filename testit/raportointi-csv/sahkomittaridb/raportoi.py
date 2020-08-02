#!/usr/bin/env python3
import sqlite3, time 

#käydään ensin olemassaolevat asiakkaat läpi
asiakkaat=[]
conn = sqlite3.connect('asiakkaat.db')
c = conn.cursor()
c.execute("SELECT * FROM asiakkaat")
for row in c:
    asiakkaat.append(row)
conn.close()

#nyt käydään kulutustietokanta läpi ja etsitään jokaisen kuukauden viimeisin lukema
kulutus=[]
conn = sqlite3.connect('kulutus.db')
c = conn.cursor()
for asi in asiakkaat:
    ip,nimi,numero=asi
    c.execute('SELECT * FROM kulutus where ip="'+ip+'"')
    kk="00"
    for row in c:
        unixaika, ip, kwh, pulssit, ajantasainen, lampo, kosteus, pihalampo, pihakosteus= row
        local_time = time.localtime(unixaika)
        paivays=time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        #print(kk)
        kulutus.append((paivays, ip, kwh, pulssit, ajantasainen, lampo, kosteus, pihalampo, pihakosteus))
        viimitem=len(kulutus)
        if viimitem > 1 and kulutus[viimitem-1][0][5:7] != kk:
            kk=paivays[5:7]
            rpaivays, rip, rkwh, rpulssit, rajantasainen, rlampo, rkosteus, rpihalampo, rpihakosteus = kulutus[viimitem-1]
            print(str(rpaivays)+";"+str(rip)+";"+str(rkwh)+";"+str(rpulssit)+";"+str(rajantasainen)+";"+str(rlampo)+";"+str(rkosteus)+";"+str(rpihalampo)+";"+str(rpihakosteus))
        #print("RR",paivays)