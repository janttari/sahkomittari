# sahkomittari
asennus:

    cd ~
    git clone https://github.com/janttari/sahkomittari.git
    cd sahkomittari
    sudo ./asenna

päivitys:

    cd ~/sahkomittari
    ./paivita

asentuu hakemistoon /opt/sahkomittari/

Asetukset tiedostoissa:
```
/opt/sahkomittari/raspisahkomittari.py #esim pulssipinni, pulssia/kwh jne LAITA TÄNNE PALVELIMEN OSOITE!
```

Luo systemd-palvelun.
raspisahkomittari.py ottaa yhteyden palvelimeen ja lähettää sille sähkömittarin lukeman pulssin saatuaan. 
Vastaanottoa voi kokeilla: server-testi

