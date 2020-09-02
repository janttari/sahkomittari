/*
    Laskee sähkömittarin S0 pulsseja ja tulostaa dataa sarjaporttiin.
    
    AJASTETTU SANOMA JOS EI PULSSEJA OLE HETKEEN SAATU:
    a;32;333;6745
    jossa a on sanoman tyyppi (ajastin), 32 on pulssien määrä, 333 aika edellisestä pulssista ms ja 6745 Arduinon sisäinen millis().

    REAALIAIKAINEN TIETO KUN PULSSI SAADAAN:
    r;32;333;6745
    jossa r on sanoman tyyppi (reaaliaikainen), 32 on pulssien määrä, 333 kahden viim mitatun pulssin väli ms ja 6745 Arduinon sisäinen millis().

    INFO KUN OHJELMA ARDUINO KÄYNNISTETÄÄN:
    i;start;versio=2020-09-02
    
*/

#define VERSIO "2020-09-02"
#define LAHETYSVALI 1000 //Lähetetään sarjaporttiin nn millisekunnin välein

#include <avr/wdt.h> //Watchdog
const byte minPulssiPituus = 70;  //Pulssin pitää olla vähintään nn millisekuntia.
volatile byte pulssiLaskuri = 0; //Pulssien määrä lasketaan tähän
unsigned long alkuaika = 0; //Keskeytyksen alkuaika
unsigned long  viimPulssiAika = millis(); //Aika jolloin viimeksi on mitattu pulssi
//unsigned long pulssiVali=0; //Viimeksi mitatun kahden pulssin väli
unsigned long viimLahetys = millis(); //Aika jolloin viimeksi lähetetty sarjaporttiin dataa
const byte mittariPinni = 2; //S0 tulee tähän pinniin. Pitää olla keskeyttävä pinni (esim Nanossa 2 tai 3)
boolean viimTila = LOW; //Pulssin viimeinen tunnettu tila

void setup() {
  wdt_enable(WDTO_8S); //Watchdog
  Serial.begin(57600);
  Serial.println("i;start;versio=" + String(VERSIO)); //Sanoma **i** info
  pinMode(mittariPinni, INPUT);
  attachInterrupt(digitalPinToInterrupt(mittariPinni), onPulssi, CHANGE); //Suoritetaan keskeytys tapahtui mikä muutos tahansa
}

void loop() {
  if (millis() - viimLahetys > LAHETYSVALI) { //Jos mittarilta ei ole tullut pulsseja, lähetetään silti säännöllisin väliajoin lukema, jotta reaaliaikaisen kulutuksen laskusuunta nähdään.
    viimLahetys = millis();
    Serial.println("a;" + String(pulssiLaskuri) + ";" + String(millis() - viimPulssiAika) + ";" + String(millis())); //Sanoma **a** ajastettu (kertoo ajan viimeisestä pulssista)
  }
  wdt_reset(); //Watchdogille elossaolosta ilmoitus
  delay(50);
}

void onPulssi() {
  bool tila = digitalRead(mittariPinni); //Luetaan onko pulssi tullut HIGH vai mennyt LOW
  if (tila != viimTila) { //Varmistetaan että on todella tapahtunut muutos tilassa
    viimTila = tila;
    if (tila == HIGH) {
      alkuaika = millis();
    }
    else {
      if (millis() - alkuaika >= minPulssiPituus) {
        pulssiLaskuri++;
        Serial.println("r;" + String(pulssiLaskuri) + ";" + String(millis() - viimPulssiAika) + ";"  + String(millis())); //Sanoma **r** reaaliaikanen (kertoo ajan tämän ja edellisen pulssin välillä)
        viimPulssiAika = millis();
        viimLahetys = millis();
      }
    }
  }
}
