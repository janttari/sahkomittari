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
/opt/sahkomittari/raspisahkomittari.py #esim pulssipinni, pulssia/kwh jne
/opt/sahkomittari/flaskpalvelin/__init__.py #esim portti-numero
```

Oletuksena palvelu vastaa selaimella: http://<raspi_ip>:5555/  
Raakatekstinä kWh-lukema: http://<raspi_ip>:5555/txt
