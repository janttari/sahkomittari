# sahkomittari
asennus **RASPBERRY CLIENT**:

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

Luo systemd-palvelun sahkomittari.service
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

sahkomittari-server.service #vastaanottaa datan raspberryltä
sahkomittari-ws-selaimille.service #lähettää dataa selaimille, kun /dev/shm/sahkomittari -hakemiston data muuttuu


tietokanta asiakkaille: 
/opt/sahkomittari-server/data/asiakkaat.db #muokataan selaimella 
 
tietokanta kulutuslukemille: 
/opt/sahkomittari-server/data/kulutus.db #tänne tallennetaan pysyvät lukemat tasatunnein 
 
 
TODO: 
-selaimelle tallennetut kulutuslukemat heti kun sivu ladataan. nyt näyttää vain kun mittari-raspilta tulee dataa 
 
