#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('raspisahkomittari.db')
print( "Opened database successfully")

cursor = conn.execute('SELECT * from asiakkaat WHERE nimi="koiralohi"')
for row in cursor:
    print ("ID = ", row[0])
    print ("NAME = ", row[2])
#   print "ADDRESS = ", row[2]
#   print "SALARY = ", row[3], "\n"
print(cursor)
print ("Operation done successfully")
conn.close()

conn = sqlite3.connect('raspisahkomittari.db')
cursor=conn.execute('SELECT EXISTS(SELECT * from asiakkaat where ip="19d2.168.4.222")')
if cursor.fetchone()[0]>0:
    print("löytyi")
else:
    print("ei!")
conn.close()
