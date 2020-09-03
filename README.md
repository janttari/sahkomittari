# sahkomittari
asennus **RASPBERRY CLIENT**:
Tämä versio ottaa vastaan sarjaportin kautta Arduinon lähettämän datan

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
/opt/sahkomittari/sahkomittari.ini #esim sarjaportti, pulssia/kwh jne LAITA TÄNNE PALVELIMEN OSOITE!
```


Luo systemd-palvelun sahkomittari.service (--> /opt/sahkomittari/raspisahkomittari.py)    
raspisahkomittari.py ottaa yhteyden palvelimeen ja lähettää sille sähkömittarin lukeman pulssin saatuaan ja ilman pulssejakin säännöllisin välein alive-viestillä.  

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
mene internet-selaimella http://raspi_server_ip  
  
 sahkomittari-server.service (--> /opt/sahkomittari-server/sahkomittari-server.py) #vastaanottaa datan raspberryltä  
 reaaliaikainen lukema tallentuu heti /dev/shm/sahkomittari-server/xxx.xxx.xxx.xxx  
 kokonaikulutus;reaaliaikainen;pulssit;info;lämpötila;kosteus  
  
 
sahkomittari-ws-selaimille.service (--> /opt/sahkomittari-server/sahkomittari-ws-selaimille.py) #lähettää dataa selaimille, kun /dev/shm/sahkomittari -hakemiston data muuttuu  
  
  
tietokanta asiakkaille:  
/opt/sahkomittari-server/data/asiakkaat.db #muokataan selaimella  
  
tietokanta kulutuslukemille:  
/opt/sahkomittari-server/data/kulutus.db #tänne tallennetaan pysyvät lukemat tasatunnein  
  
  
TODO:  
  
-sivu josta näkee tallennetut lukemat plus csv-vienti  
-tietokantojen varmuuskopiointi-lataus selaimella  

-------
LOKITUS (SEKÄ CLIENT, ETTÄ SERVER)
Aseta tiedostoissa:
```
/opt/sahkomittari/raspisahkomittari.py
/opt/sahkomittari-server/sahkomittari-server.py
/opt/sahkomittari-server/sahkomittari-ws-selaimille.py
```
DEBUG = True  
tai  
DEBUG = False  
lokit tallennetaan tiedostoon **/var/log/sahkomittarilokit.txt**  

