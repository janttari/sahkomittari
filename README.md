# sahkomittari
asennus **CLIENT RASPBERRY**:

    cd ~
    git clone https://github.com/janttari/sahkomittari.git
    cd sahkomittari/raspberry-client
    sudo ./asenna

päivitys:

    cd ~/sahkomittari/raspberry-client
    ./paivita

asentuu hakemistoon /opt/sahkomittari/

Asetukset tiedostoissa:
```
/opt/sahkomittari/raspisahkomittari.py #esim pulssipinni, pulssia/kwh jne LAITA TÄNNE PALVELIMEN OSOITE!
```

Luo systemd-palvelun.
raspisahkomittari.py ottaa yhteyden palvelimeen ja lähettää sille sähkömittarin lukeman pulssin saatuaan. 
Vastaanottoa voi kokeilla: server-testi

-------
asennus **LINUX SERVER**:

    cd ~
    git clone https://github.com/janttari/sahkomittari.git
    cd sahkomittari/linux-server
    sudo ./asenna 

päivitys: 

    cd ~/sahkomittari/linux-server 
    ./paivita 


asentuu /opt/sahkomittari-server/ 
ja luo systemd servicen joka käynnistyy itsestään
