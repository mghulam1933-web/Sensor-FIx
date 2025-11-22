#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pin sensor
const int sensor1Pin = 2;
const int sensor2Pin = 3;

// Ukuran objek (meter)
float objectWidth = 0.05; // 5 cm

// Sensor 1
unsigned long s1_start = 0;
unsigned long s1_end   = 0;
bool s1_block = false;

// Sensor 2
unsigned long s2_start = 0;
unsigned long s2_end   = 0;
bool s2_block = false;

// Nilai kecepatan
float v1 = 0;
float v2 = 0;

// Waktu blok
float t1_block = 0;
float t2_block = 0;

// Total waktu antar sensor
float T_total = 0;

void setup() {
  pinMode(sensor1Pin, INPUT_PULLUP);
  pinMode(sensor2Pin, INPUT_PULLUP);

  lcd.begin(16, 2);
  lcd.backlight();
  lcd.clear();
  lcd.print("v1 v2 + T_total");
  delay(1000);

  lcd.clear();
  lcd.print("Siap ukur...");
}

void loop() {

  bool s1 = (digitalRead(sensor1Pin) == LOW);
  bool s2 = (digitalRead(sensor2Pin) == LOW);

  // ============================
  // SENSOR 1
  // ============================
  if (s1 && !s1_block) {
    s1_start = micros();   // mulai tutup sensor 1
    s1_block = true;
  }

  if (!s1 && s1_block) {
    s1_end = micros();     // selesai tutup sensor 1
    s1_block = false;

    t1_block = (s1_end - s1_start) / 1e6;  
    v1 = objectWidth / t1_block;

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("v1:");
    lcd.print(v1, 2);
    lcd.print(" t1:");
    lcd.print(t1_block, 3);
  }

  // ============================
  // SENSOR 2
  // ============================
  if (s2 && !s2_block) {
    s2_start = micros();   // mulai tutup sensor 2
    s2_block = true;
  }

  if (!s2 && s2_block) {
    s2_end = micros();     // selesai tutup sensor 2
    s2_block = false;

    t2_block = (s2_end - s2_start) / 1e6;  
    v2 = objectWidth / t2_block;

    // ============================
    // HITUNG TOTAL WAKTU T
    // ============================

    T_total = (s2_end - s1_start) / 1e6;   // detik

    lcd.setCursor(0, 1);
    lcd.print("v2:");
    lcd.print(v2, 2);
    lcd.print(" T:");
    lcd.print(T_total, 3);
  }
}
