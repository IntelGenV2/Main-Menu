#ifndef BASIC_MESSAGES_H
#define BASIC_MESSAGES_H

#include <avr/pgmspace.h>

/*******************************************************************************
 * Interpreter messages (PROGMEM).
 ******************************************************************************/
static const unsigned char okmsg[] PROGMEM = "OK";
static const unsigned char syntaxmsg[] PROGMEM = "SYNTAX ERROR";
static const unsigned char cmdmsg[] PROGMEM = "CMD ERROR";
static const unsigned char expressionerrmsg[] PROGMEM = "EXPRESSION ERROR";
static const unsigned char badlinemsg[] PROGMEM = "LINE NUMBER ERROR";
static const unsigned char tickerrmsg[] PROGMEM = "COLOR TICK ERROR";
static const unsigned char divzeromsg[] PROGMEM = "DIVIDE BY 0 ERROR";
static const unsigned char stackoverflowmsg[] PROGMEM = "STACK OVERFLOW";
static const unsigned char outofmemorymsg[] PROGMEM = "OUT OF MEMORY";
static const unsigned char linelengthmsg[] PROGMEM = "LINE TOO LONG";
static const unsigned char returnmsg[] PROGMEM = "GOSUB ERROR";
static const unsigned char looperrmsg[] PROGMEM = "LOOP ERROR";
static const unsigned char outofdatamsg[] PROGMEM = "OUT OF DATA";
static const unsigned char breakmsg[] PROGMEM = "BREAK";
static const unsigned char inmsg[] PROGMEM = " IN ";
static const unsigned char backspacemsg[] PROGMEM = "\b \b";

#endif
