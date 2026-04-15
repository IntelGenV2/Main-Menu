#ifndef BASIC_KEYWORDS_H
#define BASIC_KEYWORDS_H

#include <avr/pgmspace.h>

/*******************************************************************************
 * BASIC keyword table + enum (must stay in lockstep; last char of each +0x80).
 * Also: func_tab, to_tab, step_tab, relop_tab, highlow_tab for scantable().
 ******************************************************************************/
const static unsigned char keywords[] PROGMEM = {
    'L', 'I', 'S', 'T' + 0x80,
    'N', 'E', 'W' + 0x80,
    'R', 'U', 'N' + 0x80,
    'N', 'E', 'X', 'T' + 0x80,
    'I', 'F' + 0x80,
    'T', 'H', 'E', 'N' + 0x80,
    'G', 'O', 'T', 'O' + 0x80,
    'G', 'O', 'S', 'U', 'B' + 0x80,
    'R', 'E', 'T', 'U', 'R', 'N' + 0x80,
    'R', 'E', 'M' + 0x80,
    'D', 'A', 'T', 'A' + 0x80,
    'R', 'E', 'A', 'D' + 0x80,
    'R', 'E', 'S', 'T', 'O', 'R', 'E' + 0x80,
    'F', 'O', 'R' + 0x80,
    'I', 'N', 'P', 'U', 'T' + 0x80,
    '?' + 0x80,
    'P', 'R', 'I', 'N', 'T' + 0x80,
    'B', 'Y', 'E' + 0x80,
    'C', 'L', 'S' + 0x80,
    'M', 'E', 'M' + 0x80,
    '.' + 0x80,
    'A', 'W', 'R', 'I', 'T', 'E' + 0x80,
    'D', 'W', 'R', 'I', 'T', 'E' + 0x80,
    'D', 'E', 'L', 'A', 'Y' + 0x80,
    'E', 'N', 'D' + 0x80,
    'R', 'S', 'E', 'E', 'D' + 0x80,
    'T', 'O', 'N', 'E', 'W' + 0x80,
    '!' + 0x80,
    'T', 'O', 'N', 'E' + 0x80,
    'N', 'O', 'T', 'O', 'N', 'E' + 0x80,
    'E', 'C', 'H', 'A', 'I', 'N' + 0x80,
    'E', 'L', 'I', 'S', 'T' + 0x80,
    'E', 'L', 'O', 'A', 'D' + 0x80,
    'E', 'F', 'O', 'R', 'M', 'A', 'T' + 0x80,
    'E', 'S', 'A', 'V', 'E' + 0x80,
    'H', 'I' + 0x80,
    0};

enum {
    KW_LIST = 0,
    KW_NEW,
    KW_RUN,
    KW_NEXT,
    KW_IF,
    KW_THEN,
    KW_GOTO,
    KW_GOSUB,
    KW_RETURN,
    KW_REM,
    KW_DATA,
    KW_READ,
    KW_RESTORE,
    KW_FOR,
    KW_INPUT,
    KW_INPUT_QMARK,
    KW_PRINT,
    KW_BYE,
    KW_CLS,
    KW_MEM,
    KW_DOT_PRINT,
    KW_AWRITE,
    KW_DWRITE,
    KW_DELAY,
    KW_END,
    KW_RSEED,
    KW_TONEW,
    KW_TONEW_BANG,
    KW_TONE,
    KW_NOTONE,
    KW_ECHAIN,
    KW_ELIST,
    KW_ELOAD,
    KW_EFORMAT,
    KW_ESAVE,
    KW_HI,
    KW_DEFAULT
};

const static unsigned char func_tab[] PROGMEM = {
    'A', 'B', 'S' + 0x80,
    'A', 'R', 'E', 'A', 'D' + 0x80,
    'D', 'R', 'E', 'A', 'D' + 0x80,
    'R', 'N', 'D' + 0x80,
    0};
#define FUNC_ABS 0
#define FUNC_AREAD 1
#define FUNC_DREAD 2
#define FUNC_RND 3
#define FUNC_UNKNOWN 4

const static unsigned char to_tab[] PROGMEM = {
    'T', 'O' + 0x80,
    0};

const static unsigned char step_tab[] PROGMEM = {
    'S', 'T', 'E', 'P' + 0x80,
    0};

const static unsigned char relop_tab[] PROGMEM = {
    '>', '=' + 0x80,
    '<', '>' + 0x80,
    '>' + 0x80,
    '=' + 0x80,
    '<', '=' + 0x80,
    '<' + 0x80,
    '!', '=' + 0x80,
    0};
#define RELOP_GE 0
#define RELOP_NE 1
#define RELOP_GT 2
#define RELOP_EQ 3
#define RELOP_LE 4
#define RELOP_LT 5
#define RELOP_NE_BANG 6
#define RELOP_UNKNOWN 7

const static unsigned char highlow_tab[] PROGMEM = {
    'H', 'I', 'G', 'H' + 0x80,
    'H', 'I' + 0x80,
    'L', 'O', 'W' + 0x80,
    'L', 'O' + 0x80,
    0};
#define HIGHLOW_HIGH 1
#define HIGHLOW_UNKNOWN 4

#endif
