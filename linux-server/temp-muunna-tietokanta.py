#!/usr/bin/env python3
import time, datetime, pytz, os, sqlite3
#muuttaa tietokannan unix-time --> YYYY-MM-DD HH:MM:SS (paikallisaika)
tietokanta="/opt/sahkomittari-server/data/kulutus.db"
tmptietokanta="tmp.db"

if os.path.isfile(tmptietokanta):
    print("rm temp")
    os.remove(tmptietokanta)

conn = sqlite3.connect(tietokanta)
connu = sqlite3.connect(tmptietokanta)
c = conn.cursor()
cu = connu.cursor()
cu.execute('CREATE TABLE IF NOT EXISTS kulutus (aikaleima DATE, ip TEXT , kwh REAL, pulssit INTEGER, tuntikohtainen REAL, lampo REAL, kosteus REAL, ulkolampo REAL, ulkokosteus REAL)')
kys=c.execute('SELECT * FROM kulutus')
for i in kys:
    aikaleima, ip, kwh, pulssit, tuntikohtainen, lampo, kosteus, ulkolampo, ulkokosteus = i
    unix_timestamp = int(aikaleima)
    paikaika = time.strftime("%Y-%m-%d %H:%M:%S",(time.localtime(unix_timestamp)))
    #    print(paikaika,type(paikaika))
    cu.execute('INSERT into kulutus(aikaleima, ip, kwh, pulssit, tuntikohtainen, lampo, kosteus, ulkolampo, ulkokosteus) VALUES("'+str(paikaika)+'", "'+str(ip)+'", "'+str(kwh)+'", "'+str(pulssit)+'", "'+str(tuntikohtainen)+'", "'+str(lampo)+'", "'+str(kosteus)+'", "'+str(ulkolampo)+'", "'+str(ulkokosteus)+'")')
connu.commit()
conn.close()
connu.close()
os.rename(tmptietokanta, tietokanta)

