#include <Wire.h>
#include <Adafruit_PN532.h>
#include <WiFi.h>
#include <HTTPClient.h>

#define SDA_PIN 4
#define SCL_PIN 5

#define WIFI_SSID "Rayhan"  // Ganti dengan SSID jaringan WiFi Anda
#define WIFI_PASSWORD "kamciper1"  // Ganti dengan kata sandi jaringan WiFi Anda

const char *serverAddress = "http://192.168.18.11/rfid/process.php";  // Ganti dengan URL skrip PHP Anda

Adafruit_PN532 nfc(SDA_PIN, SCL_PIN);

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
  Serial.println("Menunggu kartu NFC ...");

  // Koneksi ke jaringan WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi network");
}

void loop() {
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success) {
    Serial.println("Kartu NFC ditemukan!");

    Serial.print("UID: ");
    for (int i = 0; i < uidLength; i++) {
      Serial.print("0x");
      Serial.print(uid[i], HEX);
      Serial.print(" ");
    }
    Serial.println();

    // Convert UID bytes to a string representation
    String uidString = "";
    for (int i = 0; i < uidLength; i++) {
      if (uid[i] < 0x10) uidString += "0";
      uidString += String(uid[i], HEX);
    }
    
    sendToServer(uidString);
    delay(1000); // Jeda sejenak sebelum membaca kartu berikutnya
  }
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
