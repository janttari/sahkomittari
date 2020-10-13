/*
    HUOM! KYTKE A0 HYPPYLANGALLA GND JOS PALOHÄLYTINTÄ EI OLE KYTKETTY SIIHEN!

    Laskee sähkömittarin S0 pulsseja ja tulostaa dataa sarjaporttiin.

    AJASTETTU SANOMA JOS EI PULSSEJA OLE HETKEEN SAATU:
    a;32;333;6745;
    jossa a on sanoman tyyppi (ajastin), 32 on pulssien määrä, 333 aika edellisestä pulssista ms ja 6745 Arduinon sisäinen millis().

    REAALIAIKAINEN TIETO KUN PULSSI SAADAAN:
    r;32;333;6745
    jossa r on sanoman tyyppi (reaaliaikainen), 32 on pulssien määrä, 333 kahden viim mitatun pulssin väli ms ja 6745 Arduinon sisäinen millis().

    KUN INPUTIN TILA MUUTTUU:
    h;2;1
    jossa h on sanoman tyyppi hälytys, 2 on pinnin indeksi-numero ja 1 on tila hälyttää

    INFO KUN OHJELMA ARDUINO KÄYNNISTETÄÄN:
    i;start;versio=2020-09-02

    Arduinole voi lähettää yhden tavun sarjaportista, joka laittaa 8 lähtöä haluttuun tilaan.

*/

#define VERSIO "2020-10-13"
const byte relePinnit[] = {4, 5, 6, 7, 8, 9, 10, 11}; // näissä pinneissä voi olla rele HUOMAA LÄHETTÄESSÄ BITTIJÄRJESTYS!
#define LAHETYSVALI 1000 //Lähetetään sarjaporttiin nn millisekunnin välein silloinkin kun reaaliaikaista mittaustietoa ei tule

typedef struct inputPinnit { //pinni sekä sallittu alue jonka sisällä tulon arvon pitää olla jottei se hälytä
  int pinni;
  int minimi;
  int maksimi;
} inputPinnit_t;
//inputPinnit_t inputit[] = {{A0, 2, 222}, {A1, 3, 333}, {A2, 3, 333}};
inputPinnit_t inputit[] = {{A0, 0, 500}};
bool inputPinniTila[sizeof(inputit) / sizeof(int) / 3]; //luetaan analogisten pinnien  tila tähän true=hälyttää, false=ei hälytä
bool edInputPinniTila[sizeof(inputit) / sizeof(int) / 3]; //pinnien viimeinen tunnettu tila

#include <avr/wdt.h> //Watchdog
const byte minPulssiPituus = 20;  //Pulssin pitää olla vähintään nn millisekuntia.
volatile byte pulssiLaskuri = 0; //Pulssien määrä lasketaan tähän
unsigned long alkuaika = 0; //Keskeytyksen alkuaika
unsigned long  viimPulssiAika = millis(); //Aika jolloin viimeksi on mitattu pulssi
//unsigned long pulssiVali=0; //Viimeksi mitatun kahden pulssin väli
unsigned long viimLahetys = millis(); //Aika jolloin viimeksi lähetetty sarjaporttiin dataa
const byte mittariPinni = 2; //S0 tulee tähän pinniin. Pitää olla keskeyttävä pinni (esim Nanossa 2 tai 3)
boolean viimTila = LOW; //Pulssin viimeinen tunnettu tila

void setup() {
  Serial.begin(57600);
  int pinniMaara = sizeof(inputit) / sizeof(int) / 3; //inputpinnien määrä
  for (int i = 0; i < pinniMaara; i++) { //alustetaan kaikki tulot ei-hälyttäviksi
    inputPinniTila[i] = false;
    edInputPinniTila[i] = false;
  }

  for ( byte a = 0; a < sizeof (relePinnit) ; a++) { //alustetaan releet
    pinMode(relePinnit[a], OUTPUT);
    digitalWrite(relePinnit[a], LOW);
  }

  wdt_enable(WDTO_8S); //Watchdog
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

  if (Serial.available() > 0) { //jos sarjaportista on arduinon suuntaan tulevaa dataa
    byte komento = Serial.read();
    for ( int a = 0; a < sizeof (relePinnit) ; a++) {
      if (bitRead(komento, a )) {
        digitalWrite(relePinnit[a], HIGH);
        //Serial.println("i;"+String(relePinnit[a])+" HIGH");
      }
      else {
        digitalWrite(relePinnit[a], LOW);
        //Serial.println("i;"+String(relePinnit[a])+" LOW");
      }
    }
  }
  lueInput();
  delay(50);
}

void lueInput() {
  int pinniMaara = sizeof(inputit) / sizeof(int) / 3; //inputpinnien määrä
  for (int i = 0; i < pinniMaara; i++) {
    int arvo = analogRead(inputit[i].pinni);
    //Serial.println("Luetaan pinni " + String(inputit[i].pinni) + ":" + String(arvo));
    if (arvo < inputit[i].minimi || arvo > inputit[i].maksimi) { //hälyttää
      inputPinniTila[i] = true;
    }
    else {
      inputPinniTila[i] = false;
    }
    if (inputPinniTila[i] != edInputPinniTila[i]) { //jos pinnin hälytystila on muuttunut
      Serial.println("h;" + String(i) + ";" + String(inputPinniTila[i]));
      edInputPinniTila[i] = inputPinniTila[i];
    }

  }
}
void onPulssi() { //tämä suoritetaan aina kun mittari-pinnin tila muuttuu joko LOW-->HIGH tai HIGH-->LOW
  bool tila = digitalRead(mittariPinni); //Luetaan onko pulssi tullut HIGH vai mennyt LOW
  if (tila != viimTila) { //Varmistetaan että on todella tapahtunut muutos tilassa
    viimTila = tila;
    if (tila == HIGH) { //mittarin lähettämä pulssitapahtuma alkaa
      alkuaika = millis();
    }
    else {
      if (millis() - alkuaika >= minPulssiPituus) { // jos HIGH tila on ollut riittävän pitkä että se voidaan tulkita impulssiksi
        pulssiLaskuri++;
        Serial.println("r;" + String(pulssiLaskuri) + ";" + String(millis() - viimPulssiAika) + ";"  + String(millis())); //Sanoma **r** reaaliaikanen (kertoo ajan tämän ja edellisen pulssin välillä)
        viimPulssiAika = millis();
        viimLahetys = millis();
      }
    }
  }
}
