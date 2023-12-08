#include <Wire.h>
#include <Adafruit_PN532.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <LiquidCrystal_I2C.h>

#define SDA_PIN 4
#define SCL_PIN 5

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

#define WIFI_SSID "Rayhan"  // Ganti dengan SSID jaringan WiFi Anda
#define WIFI_PASSWORD "kamciper1"  // Ganti dengan kata sandi jaringan WiFi Anda
const char *serverAddress = "http://192.168.18.11/rfid/process.php";  // Ganti dengan URL skrip PHP Anda

uint8_t allowedUID[] = {4, 107, 67, 178, 224, 75, 128};

int relayPin = 18;
int buzzerPin = 19;
int redLedPin = 22;
int yellowLedPin = 23;

LiquidCrystal_I2C lcd(0x27, 16, 2); // Alamat I2C LCD dan dimensi

void setup(void) {
  Serial.begin(115200);
  Serial.println("Hello!");

  Wire.begin(SDA_PIN, SCL_PIN);

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.print("Tidak dapat menemukan board PN53x");
    while (1);
  }

  nfc.SAMConfig();

  // Koneksi ke jaringan WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi network");
  Serial.println("Menunggu kartu NFC ...");

  pinMode(relayPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(redLedPin, OUTPUT);
  pinMode(yellowLedPin, OUTPUT);
  
  digitalWrite(relayPin, LOW);
  digitalWrite(buzzerPin, LOW);
  digitalWrite(redLedPin, LOW);
  digitalWrite(yellowLedPin, LOW);

  lcd.init(); // Inisialisasi LCD
  lcd.backlight(); // Aktifkan backlight LCD
  lcd.setCursor(0, 0);
  lcd.print("Waiting for card");
}

void loop() {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    lcd.clear(); // Bersihkan layar LCD
    lcd.setCursor(0, 0);
    lcd.print("Found an NFC card!");
    
    Serial.println("Found an NFC card!");
    Serial.print("UID: ");
    for (int i = 0; i < uidLength; i++) {
      Serial.print(uid[i]);
      Serial.print(" ");
    }
    Serial.println();
    
    bool accessGranted = true;
    if (uidLength == sizeof(allowedUID)) {
      for (int i = 0; i < uidLength; i++) {
        if (uid[i] != allowedUID[i]) {
          accessGranted = false;
          break;
        }
      }
    } else {
      accessGranted = false;
    }

    String uidString = convertUIDToString(uid, uidLength);
    if (uidString.equalsIgnoreCase("046b43b2e04b80")) {
      digitalWrite(relayPin, LOW);
      digitalWrite(yellowLedPin, HIGH);
      lcd.setCursor(0, 1);
      lcd.print("Access granted");
      delay(2000);
      digitalWrite(relayPin, HIGH);
      digitalWrite(yellowLedPin, LOW);

      String uidString = convertUIDToString(uid, uidLength);
      sendToServer(uidString);
    } else {
      digitalWrite(redLedPin, HIGH);
      digitalWrite(buzzerPin, HIGH);
      lcd.setCursor(0, 1);
      lcd.print("Access denied");
      delay(2000);
      digitalWrite(redLedPin, LOW);
      digitalWrite(buzzerPin, LOW);

      String uidString = convertUIDToString(uid, uidLength);
      sendToServer(uidString);
    }
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Waiting for card");
  }
}

String convertUIDToString(uint8_t *uid, uint8_t uidLength) {
  String uidString = "";
  for (int i = 0; i < uidLength; i++) {
    if (uid[i] < 0x10) uidString += "0";
    uidString += String(uid[i], HEX);
  }
  return uidString;
}

void sendToServer(String uidString) {
  HTTPClient http;

  if (http.begin(serverAddress)) {
    Serial.println("Connected to server");

    // Menyiapkan data POST
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    int httpResponseCode = http.POST("uid=" + uidString);

    if (httpResponseCode == 200) {
      Serial.println("Data sent successfully");
      String payload = http.getString();
      Serial.print("RESPONSE = ");
      Serial.println(payload);
    } else {
      Serial.print("Error on sending POST request: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("Connection to server failed");
  }
}