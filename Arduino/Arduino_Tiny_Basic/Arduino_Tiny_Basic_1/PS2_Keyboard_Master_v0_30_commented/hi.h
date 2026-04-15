#ifndef HI_H
#define HI_H

#include <avr/pgmspace.h>

/*
 * HI command — grumpy one-liners (flash only). Edit strings or HI_MSG_COUNT.
 */
#define HI_MSG_COUNT 10

static const unsigned char hi_m0[] PROGMEM = "What.";
static const unsigned char hi_m1[] PROGMEM = "No!";
static const unsigned char hi_m2[] PROGMEM = "Bye.";
static const unsigned char hi_m3[] PROGMEM = "Shoo.";
static const unsigned char hi_m4[] PROGMEM = "Later.";
static const unsigned char hi_m5[] PROGMEM = "Go away.";
static const unsigned char hi_m6[] PROGMEM = "Oh no...";
static const unsigned char hi_m7[] PROGMEM = "What now?";
static const unsigned char hi_m8[] PROGMEM = "Not now. Busy.";
static const unsigned char hi_m9[] PROGMEM = "bruh...";

static const unsigned char *const hi_tab[HI_MSG_COUNT] PROGMEM = {
    hi_m0, hi_m1, hi_m2, hi_m3, hi_m4,
    hi_m5, hi_m6, hi_m7, hi_m8, hi_m9,
};

static inline void hi_print_random(void)
{
    extern void printmsgNoNL(const unsigned char *msg);
    unsigned char i = (unsigned char)random((long)HI_MSG_COUNT);
    const unsigned char *p =
        (const unsigned char *)pgm_read_word(&hi_tab[i]);
    printmsgNoNL(p);
}

#endif
