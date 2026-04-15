#ifndef BOOT_SCREEN_H
#define BOOT_SCREEN_H

#include <Arduino.h>
#include <avr/pgmspace.h>
#include "gpu_protocol.h"

/* Boot timing (ms) */
#define BOOT_DELAY_START_MS 750
#define BOOT_DELAY_AFTER_CLS_MS 80
#define BOOT_DELAY_LOGO_MS 5000
#define BOOT_DELAY_POST_MEM_MS 5000
#define BOOT_DELAY_AFTER_WELCOME_CLS_MS 100
#define BOOT_DELAY_WELCOME_LINE_MS 1000
#define BOOT_DELAY_WRONG_PASS_MS 1500

#define BOOT_PASSWORD_LEN 4

static const char boot_password[] PROGMEM = "Tron";

static inline int boot_password_ok(const char *buf, unsigned char len)
{
    unsigned char j;
    if (len != BOOT_PASSWORD_LEN)
        return 0;
    for (j = 0; j < BOOT_PASSWORD_LEN; j++) {
        if (buf[j] != (char)pgm_read_byte(&boot_password[j]))
            return 0;
    }
    return 1;
}

/* TRON-style logo over Serial; '`' / '~' in F() strings must match GPU_COLOR_TICK / GPU_BLOCK. */
#define BOOT_PRINT_GRID()                       \
    do {                                        \
        Serial.println(F("`~~~~~~~~~~~~~~~~~~~~~~~~")); \
        Serial.println(F("~`~~~~~~~~~~~~~~~~~~~~~~``~")); \
        Serial.println(F("~`~                    ~``~")); \
        Serial.println(F("~`~                    ~``~")); \
        Serial.println(F("~`~`   Tiny Basic 1.6   ``~``~")); \
        Serial.println(F("~`~                    ~``~")); \
        Serial.println(F("~`~                    ~``~")); \
        Serial.println(F("~`~~~~~~~~~~~~~~~~~~~~~~``~")); \
        Serial.println(F("~~~~~~~~~~~~~~~~~~~~~~~~")); \
    } while (0)

#endif
