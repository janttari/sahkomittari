#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("/opt/sahkomittari-server/data/kulutus.db")
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS kulutus (aikaleima INTEGER, ip STRING , kwh REAL, pulssit INTEGER)')
c.execute('INSERT into kulutus(aikaleima, ip, kwh, pulssit) VALUES(555, "127.0.0.1", 556.0, 88)')
conn.commit()
conn.close()
