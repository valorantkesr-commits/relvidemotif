#include <WiFi.h>
#include <HTTPClient.h>
#include <TFT_eSPI.h>
#include <SPI.h>
#include <ArduinoJson.h>

const char* ssid = "WIFI_ADI";
const char* password = "WIFI_SIFRESI";

const char* apiKey = "get api here";
const char* serverUrl = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent";

TFT_eSPI tft = TFT_eSPI();

#define BUTTON_1 0    
#define BUTTON_2 14   

void setup() {
    Serial.begin(115200);

    tft.init();
    tft.setRotation(1);
    tft.fillScreen(TFT_BLACK);
    
    pinMode(TFT_BL, OUTPUT);
    digitalWrite(TFT_BL, HIGH);

    pinMode(BUTTON_1, INPUT_PULLUP);
    pinMode(BUTTON_2, INPUT_PULLUP);

    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.setTextSize(2);
    tft.setCursor(10, 10);
    tft.print("Ametist T-Display");

    tft.setTextSize(1);
    tft.setCursor(10, 45);
    tft.print("Wi-Fi baglaniyor...");

    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    tft.setCursor(10, 70);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.print("Baglanti Basarili!");
    delay(1000);
    
    gosterAnaEkran();
}

void loop() {
    if (digitalRead(BUTTON_1) == LOW) {
        tft.fillScreen(0x1A1B);
        tft.setCursor(10, 10);
        tft.setTextColor(TFT_YELLOW, 0x1A1B);
        tft.setTextSize(1);
        tft.print("Analiz ediliyor...");
        
        geminiIstegiGonder();
        delay(300);
    }

    if (digitalRead(BUTTON_2) == LOW) {
        gosterAnaEkran();
        delay(300);
    }
}

void gosterAnaEkran() {
    tft.fillScreen(0x1A1B); 
    tft.setTextColor(TFT_WHITE, 0x1A1B);
    tft.setTextSize(2);
    tft.setCursor(10, 15);
    tft.print("Ametist Motifi");
    
    tft.setTextSize(1);
    tft.setTextColor(TFT_LIGHTGREY, 0x1A1B);
    tft.setCursor(10, 55);
    tft.print("[Buton 1]: Analizi Baslat");
    tft.setCursor(10, 75);
    tft.print("[Buton 2]: Ekrani Temizle");
}

void geminiIstegiGonder() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        String tamUrl = String(serverUrl) + "?key=" + apiKey;
        
        http.begin(tamUrl);
        http.addHeader("Content-Type", "application/json");

        JsonDocument docOut;
        docOut["contents"][0]["parts"][0]["text"] = "Hali motifi hakkinda kisa ve net 2 cumlelik bilgi ver.";
        
        String payload;
        serializeJson(docOut, payload);

        int httpKod = http.POST(payload);

        tft.fillScreen(0x1A1B);
        tft.setCursor(10, 10);
        tft.setTextSize(1);

        if (httpKod > 0) {
            String cevap = http.getString();
            Serial.println(cevap);

            JsonDocument docIn;
            DeserializationError hata = deserializeJson(docIn, cevap);

            if (!hata) {
                const char* metin = docIn["candidates"][0]["content"]["parts"][0]["text"];
                
                if (metin != nullptr) {
                    tft.setTextColor(TFT_CYAN, 0x1A1B);
                    tft.println("Sonuc:\n");
                    tft.setTextColor(TFT_WHITE, 0x1A1B);
                    tft.println(metin);
                } else {
                    tft.setTextColor(TFT_RED, 0x1A1B);
                    tft.print("JSON icinde metin bulunamadi.");
                }
            } else {
                tft.setTextColor(TFT_RED, 0x1A1B);
                tft.print("Parse Hatasi: ");
                tft.print(hata.c_str());
            }
        } else {
            tft.setTextColor(TFT_RED, 0x1A1B);
            tft.print("HTTP Hata Kodu: ");
            tft.print(httpKod);
        }
        http.end();
    } else {
        tft.fillScreen(0x1A1B);
        tft.setCursor(10, 10);
        tft.setTextColor(TFT_RED, 0x1A1B);
        tft.print("Wi-Fi Kopuk!");
    }
}
