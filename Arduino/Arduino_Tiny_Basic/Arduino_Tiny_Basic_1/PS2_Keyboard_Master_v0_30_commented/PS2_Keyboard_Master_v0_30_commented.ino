/*******************************************************************************
 * PS2_Keyboard_Master_v0_30_commented – FULLY DOCUMENTED CPU SKETCH
 *******************************************************************************
 * PURPOSE - For humans and AIs who edit the inner workings of the TinyBasic
 * CPU. This file contains copious comments; no external documentation needed.
 *
 * ============================================================================
 * HARDWARE & ARCHITECTURE
 * ============================================================================
 * - CPU - Arduino Nano. Runs this sketch (TinyBasic interpreter + boot logic).
 * - GPU - Separate Arduino Nano with VGA_Graphics_Slave_v1_5.ino.
 * - Link: CPU Serial TX → GPU Serial RX. Baud = kConsoleBaud (4800). Must match.
 * - Keyboard: PS2Keyboard on kPs2DataPin=8, kPs2IrqPin=3. Scancodes → ASCII.
 * - All display output goes via Serial.write()/Serial.print(); GPU renders.
 *
 * ============================================================================
 * MEMORY LAYOUT (program buffer = program[kRamSize])
 * ============================================================================
 * [program_start ... program_end)  = BASIC lines (sorted by line number)
 * [program_end ... program+kRamSize) = free space for new/edited lines (tail of program[] buffer)
 * A..Z live in basic_variable[27]; FOR/GOSUB frames in interp_for_stack[STACK_SIZE] (separate RAM).
 * SRAM tuning: packed FOR/GOSUB stack structs; HISTORY_WIDTH; see #defines near globals.
 *
 * LINE FORMAT in program buffer:
 *   [LINENUM 2 bytes][LEN 1 byte][TEXT...][NL]
 *   LEN = length of whole line including header + text + NL (must be 1..255).
 *   Lines stored in ascending line-number order.
 *
 * ============================================================================
 * GPU serial protocol — see gpu_protocol.h (must match VGA_Graphics_Slave_v1_5).
 *
 * ============================================================================
 * EXECUTION FLOW (loop)
 * ============================================================================
 * 1. setup(): init Serial, PS2, program[], variables_begin, interp stack pointers.
 * 2. BOOT (first loop): TRON GRID, password ("Tron").
 * 3. On correct password: showMemoryScreen() — SRAM, BASIC, EEPROM (~ bars).
 * 4. Then WELCOME; warmstart path (never re-enters boot until reset).
 * 5. warmstart: reset sp; print OK unless skipped; goto prompt.
 * 6. prompt: getln('>'). User types line. Up-arrow/Down-arrow browse last 3
 *    non-empty lines. toUppercaseBuffer() normalizes A..Z outside quotes.
 * 7. LINE ENTRY - Parse line number. If 0 → direct command. Else merge into program.
 * 8. direct: txtpos at program_end+sizeof(LINENUM). goto interperateAtTxtpos.
 * 9. interperateAtTxtpos: breakcheck (ESC), scantable(keywords), switch on command.
 * 10. run_next_statement: skip ':', if NL → execnextline. Else → interperateAtTxtpos.
 * 11. execnextline: current_line += line_length, goto execline.
 * 12. execline: if program_end → warmstart. Else txtpos = current line, goto interperateAtTxtpos.
 *
 * ============================================================================
 * KEY DATA STRUCTURES
 * ============================================================================
 * - txtpos: Pointer into program buffer; current parse position.
 * - current_line: During RUN, points to line being executed.
 * - program_start, program_end: Bounds of stored lines.
 * - sp: FOR/GOSUB + printnum stack (grows down inside interp_for_stack).
 * - inStream, outStream: Serial or EEPROM only.
 * - inhibitOutput: true while reading a program from EEPROM (ELOAD path; suppress echo).
 * - runAfterLoad, triggerRun: After ECHAIN or autorun load, run on next prompt.
 * - lastLineBuf/lastLineLen/historyCount: 3-entry command history for prompt.
 *
 * ============================================================================
 * EDITING THIS FILE
 * ============================================================================
 * ADDING A NEW COMMAND -
 *   1. Add keyword string to basic_keywords.h keywords[] (last char +0x80). Order must match enum.
 *   2. Add KW_XXX to the enum there (same order as keywords[]). New funcs/relops: func_tab / relop_tab there.
 *   3. Add case KW_XXX: ... in switch(table_index) in interperateAtTxtpos.
 *   4. Use expression() for numeric args, scantable() for TO/STEP, etc.
 *   5. End with goto run_next_statement or goto execnextline.
 * 
 * CHANGING BOOT - boot_screen.h (delays, logo macro, password); loop() gpu_* for colors.
 *
 * ============================================================================
 * SOURCE LAYOUT (top-to-bottom)
 * ============================================================================
 * Configuration, includes, globals, gpu_protocol.h, basic_keywords.h / basic_messages.h / hi.h → parser helpers (scantable,
 * stack, printnum) → GPU pen + line I/O (getln, findline, expressions) →
 * errors and MEM/EEPROM helpers → loop() (boot, then warmstart / prompt /
 * merge / interpreter labels) → command implementations (LIST, PRINT, …) →
 * setup() → breakcheck, inchar, outchar.
 *
 * EXPRESSION GRAMMAR - expr4 (unary/atoms) → expr3 (mul/div) → expr2 (add/sub) → expression (relops).
 *
 * LINE MERGE - findline() finds insertion point; compact() removes old line;
 *   while(linelen) shuffle bytes from program_end toward start.
 ******************************************************************************/
/*******************************************************************************
 * CONFIGURATION – features, pins, baud
 * ----------------------------------------------------------------------------
 * EAUTORUN - Off by default: do not define ENABLE_EAUTORUN (no auto-load/run from EEPROM on boot).
 * Tones and EEPROM are built in (TONE/TONEW/NOTONE; ESAVE/ELOAD/…).
 * kErrorLedPin - Red error LED (active HIGH); on for errors, off after successful direct line,
 *   CLS, RUN, LIST completion, BYE, EEPROM→warmstart, or autorun start.
 * kConsoleBaud - Must match GPU Serial.begin(). 4800 is stable; 9600 faster but
 *   can cause PS2 keyboard shift-state glitches (numbers→symbols).
 ******************************************************************************/

/* Optional EEPROM autorun: uncomment the next line so EEPROM[0] '0'..'9' loads and runs on boot. */
/* #define ENABLE_EAUTORUN 1 */

#define kPiezoPin 5
#define kErrorLedPin 6

#define kConsoleBaud 4800

/*******************************************************************************
 * BUILD & INCLUDES – Arduino/AVR, RAM size, libraries
 * ----------------------------------------------------------------------------
 * program[kRamSize] is only lines + scratch. Vars/stack are separate static arrays. PROGMEM in flash.
 ******************************************************************************/
#include <avr/pgmspace.h>
#ifndef RAMEND
#define RAMEND (4096 - 1)
#endif

#include <EEPROM.h>
/* ELOAD pacing: per-byte delay stretches load time; start delay is one-shot at eload/echain. */
#define EEPROM_LOAD_CHAR_DELAY_MS 4
#define EEPROM_LOAD_START_DELAY_MS 150
int eepos = 0;  /* EEPROM read/write position during ELOAD/ESAVE */

#include <PS2Keyboard.h>
/* PS/2 pins as macros (no .bss); wire DATA/CLK per header comment. IRQ must be 2 or 3. */
#define kPs2DataPin 8
#define kPs2IrqPin  3
PS2Keyboard keyboard;
/* Program buffer = lines + scratch only. Must match BASIC_PROGRAM_LIMIT_BYTES in
 * Tools/Tiny Basic Sender/tiny_basic_syntax.py (change both if you resize the buffer). */
#define kRamSize 1024

/*******************************************************************************
 * TYPES & COMPATIBILITY – byte, PROGMEM (for non-Arduino builds)
 * ----------------------------------------------------------------------------
 * byte: Some compilers lack this. Fallback to unsigned char.
 * PROGMEM/pgm_read_byte: Arduino stores strings/tables in flash. Non-Arduino
 *   builds use empty PROGMEM and direct pointer read.
 ******************************************************************************/
#ifndef byte
typedef unsigned char byte;
#endif

#ifndef PROGMEM
#define PROGMEM
#endif
#ifndef pgm_read_byte
#define pgm_read_byte( A ) *(A)
#endif
#ifndef pgm_read_word
#define pgm_read_word( A ) (*(const unsigned int *)(A))
#endif

#include "gpu_protocol.h"
#include "basic_messages.h"
#include "basic_keywords.h"
#include "boot_screen.h"
#include "hi.h"

/*******************************************************************************
 * RUNTIME STATE – output control, load/save stream selection
 * ----------------------------------------------------------------------------
 * inhibitOutput - When true during EEPROM program load (ELOAD/ECHAIN/autorun), outchar() does
 *   nothing (no echo of raw bytes to the GPU).
 * runAfterLoad: After ECHAIN or autorun ELOAD path, set true; inchar() then sets
 *   triggerRun so RUN starts on next prompt.
 * inStream/outStream - kStreamSerial (keyboard/Serial), kStreamEEProm.
 ******************************************************************************/
boolean inhibitOutput = false;
static boolean runAfterLoad = false;
static boolean triggerRun = false;

enum {
  kStreamSerial = 0,
  kStreamEEProm
};
static unsigned char inStream = kStreamSerial;
static unsigned char outStream = kStreamSerial;

/*******************************************************************************
 * ASCII CONSTANTS – control chars, type alias
 * ----------------------------------------------------------------------------
 * CR/LF - Newline via CR. GPU newlines when x!=0; ignores LF (CRLF-safe).
 * CTRLH - Backspace (0x08). Also 127 (Delete). Used by getln and GPU.
 * BELL - '\b' alias. CTRLS/CTRLX - possible flow control. SQUOTE/DQUOTE - strings.
 ******************************************************************************/
#define CR	'\r'
#define NL	'\n'
#define LF      0x0a
#define TAB	'\t'
#define BELL	'\b'
#define SPACE   ' '
#define SQUOTE  '\''
#define DQUOTE  '\"'
#define CTRLC	0x03
#define CTRLH	0x08
#define CTRLS	0x13
#define CTRLX	0x18

typedef short unsigned LINENUM;
#define ECHO_CHARS 1

/*******************************************************************************
 * INTERPRETER GLOBALS – program buffer, text pointer, error flags
 * ----------------------------------------------------------------------------
 * program[]: stored BASIC lines. txtpos: parse cursor. list_line: LIST/ESAVE walk.
 * expression_error / expression_error_code: set by expression evaluation.
 ******************************************************************************/
static unsigned char program[kRamSize];
static short basic_variable[27];
static unsigned char *txtpos,*list_line, *tmptxtpos;
static unsigned char expression_error;
static unsigned char expression_error_code;
static unsigned char *tempsp;

// Command history (up to 3 last non-empty lines at prompt)
// Each entry stores up to 20 characters (one safe on-screen line).
#define HISTORY_DEPTH 3
#define HISTORY_WIDTH 20
static unsigned char lastLineBuf[HISTORY_DEPTH][HISTORY_WIDTH];
static unsigned char lastLineLen[HISTORY_DEPTH];
static unsigned char historyCount = 0;      // how many entries are valid (0..HISTORY_DEPTH)
static unsigned char historyIndex = 0;      // which entry we are viewing when browsing
static boolean historyBrowsing = false;     // true while user is stepping back with up-arrow

/*******************************************************************************
 * KEYWORDS & COMMAND ENUM – see basic_keywords.h (table + enum must match).
 ******************************************************************************/

/*******************************************************************************
 * PARSER TABLES & STACK STRUCTURES – FOR/NEXT, GOSUB, funcs, relops
 * ----------------------------------------------------------------------------
 * stack_for_frame: FOR A=1 TO 10 STEP 2. Stores var, terminal, step,
 *   current_line, txtpos. Stack grows DOWN (sp decreases on push).
 * stack_gosub_frame: GOSUB 100. Stores return current_line, txtpos.
 * func_tab / relop_tab / highlow_tab / to_tab / step_tab: see basic_keywords.h.
 ******************************************************************************/
struct stack_for_frame {
  char frame_type;
  char for_var;
  short int terminal;
  short int step;
  unsigned char *current_line;
  unsigned char *txtpos;
} __attribute__((packed));

struct stack_gosub_frame {
  char frame_type;
  unsigned char *current_line;
  unsigned char *txtpos;
} __attribute__((packed));

// STACK_SIZE - Max 5 FOR frames OR mix of FOR+GOSUB. Increase if nested deeper.
#define STACK_SIZE (sizeof(struct stack_for_frame)*5)
#define VAR_SIZE sizeof(short int)  /* Variables A..Z = short ints */

static unsigned char interp_for_stack[STACK_SIZE];

/*******************************************************************************
 * INTERPRETER STATE – program, stack, variables, current line
 * ----------------------------------------------------------------------------
 * stack_limit = interp_for_stack; sp grows down from interp_for_stack+STACK_SIZE.
 * variables_begin = (unsigned char *)basic_variable (27 shorts, A..Z).
 * current_line: During RUN, points to line being executed. NULL = direct mode.
 ******************************************************************************/
static unsigned char *stack_limit;
static unsigned char *program_start;
static unsigned char *program_end;
static unsigned char *variables_begin;
static unsigned char *current_line;
static unsigned char *sp;
#define STACK_GOSUB_FLAG 'G'
#define STACK_FOR_FLAG 'F'
static unsigned char table_index;
static LINENUM linenum;
/* DATA / READ: RESTORE anchor (NULL = program start). */
static unsigned char *data_read_start_line;
static unsigned char *data_cur_line;
static unsigned char *data_cur_pos;
/* Set after boot prints "System OK" - skip duplicate warmstart OK line. */
static unsigned char omit_next_warmstart_ok;

/*******************************************************************************
 * MESSAGE STRINGS (PROGMEM) – see basic_messages.h
 ******************************************************************************/

/*******************************************************************************
 * FORWARD DECLARATIONS
 ******************************************************************************/
static int inchar(void);
static void outchar(unsigned char c);
static void line_terminator(void);
static short int expression(void);
static unsigned char breakcheck(void);
static void printErrorWithPointer(const unsigned char *msg);
static void errorLedOn(void);
static void errorLedOff(void);
static void toneErrorEvent(void);
static void toneSystemReady(void);
static void toneNewEvent(void);
static unsigned char lineExists(LINENUM target);
static LINENUM currentLineNumber(void);
static void showMemoryScreen(void);
static int eepromUsedBytes(void);
static unsigned char *next_program_line(unsigned char *line);
static unsigned char *find_data_line_from(unsigned char *line_start);
static void data_reset_pointers(void);
static unsigned char data_parse_number(short int *out);

/*******************************************************************************
 * KEYBOARD HELPERS – backspace, printable check
 * ----------------------------------------------------------------------------
 * isBackspaceKey - 0x08 or 127. Used in getln and password prompt.
 * isPrintableInput - 32..126 (ASCII printable). Skip control chars.
 ******************************************************************************/
static inline boolean isBackspaceKey(char c)
{
  return (c == CTRLH) || ((unsigned char)c == 127);
}

static inline boolean isPrintableInput(char c)
{
  unsigned char uc = (unsigned char)c;
  return (uc >= 32 && uc <= 126);
}

/*******************************************************************************
 * PARSER HELPERS – ignore_blanks, scantable, stack (pushb/popb), printnum
 * ----------------------------------------------------------------------------
 * ignore_blanks: Advance txtpos past spaces, tabs, and CR (stray paste/Windows).
 * scantable: Linear scan of PROGMEM table. On match, txtpos advances past
 *   keyword, table_index = which entry. On mismatch, skip to next table entry.
 * pushb/popb: Software stack (sp). Used by printnum for digit reversal and
 *   by FOR/GOSUB. Stack grows down (high addr = bottom).
 * printnum: Convert int to decimal digits via pushb (reverse order), then popb.
 ******************************************************************************/
static void ignore_blanks(void)
{
  while(*txtpos == SPACE || *txtpos == TAB || *txtpos == '\r')
    txtpos++;
}

/* Expands in loop() only; goto qtickerr is in that function. */
#define IGNORE_AND_REJECT_CMD_TICK() do { ignore_blanks(); if (*txtpos == GPU_COLOR_TICK) goto qtickerr; } while(0)

/* Route statement/line failures using expression_error_code: 2 = divide by zero,
 * else non-zero = bad expression; these macros never fall through. */
#define GOTO_DIV0_OR_EXPRESSION_ERROR() \
  do { \
    if((expression_error_code) == 2) \
      goto qdivzero; \
    goto qexpression; \
  } while(0)

#define GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR() \
  do { \
    if((expression_error_code) == 2) \
      goto qdivzero; \
    if((expression_error_code) != 0) \
      goto qexpression; \
    goto qsyntax; \
  } while(0)

/* Clears expression parse/eval flags before each expression() call. */
#define CLEAR_EXPR_ERR() \
  do { \
    expression_error = 0; \
    expression_error_code = 0; \
  } while(0)

/*******************************************************************************
 * scantable – match next token against a PROGMEM keyword table
 * ----------------------------------------------------------------------------
 * Walk txtpos[i] vs table bytes. Terminator byte uses high bit (0x80); last char
 * of keyword matches txtpos[i]+0x80. On match: advance txtpos, ignore_blanks.
 * On mismatch: skip to next table entry, increment table_index, retry.
 ******************************************************************************/
static void scantable(const unsigned char *table)
{
  int i = 0;
  table_index = 0;
  while(1)
  {
    if(pgm_read_byte( table ) == 0)
      return;

    if(txtpos[i] == pgm_read_byte( table ))
    {
      i++;
      table++;
    }
    else
    {
      if(txtpos[i]+0x80 == pgm_read_byte( table ))
      {
        txtpos += i+1;  // Advance the pointer to following the keyword
        ignore_blanks();
        return;
      }

      while((pgm_read_byte( table ) & 0x80) == 0)
        table++;

      table++;
      table_index++;
      ignore_blanks();
      i = 0;
    }
  }
}

/*******************************************************************************
 * pushb / popb – byte stack on sp (grows down inside interp_for_stack tail)
 ******************************************************************************/
static void pushb(unsigned char b)
{
  sp--;
  *sp = b;
}

static unsigned char popb()
{
  unsigned char b;
  b = *sp;
  sp++;
  return b;
}

/*******************************************************************************
 * printnum – signed decimal via outchar (uses pushb/popb digit stack)
 * ----------------------------------------------------------------------------
 * Negative values use unsigned magnitude so -32768 prints correctly on 16-bit.
 ******************************************************************************/
void printnum(int num)
{
  int digits = 0;
  unsigned int mag;

  if(num < 0)
  {
    outchar('-');
    mag = 1U + (unsigned int)(-(num + 1));
  }
  else
    mag = (unsigned int)num;

  if(mag == 0)
  {
    outchar('0');
    return;
  }

  do {
    pushb((unsigned char)(mag % 10U + (unsigned int)'0'));
    mag /= 10U;
    digits++;
  } while(mag > 0);

  while(digits > 0)
  {
    outchar(popb());
    digits--;
  }
}

/* printUnum - Same as printnum but unsigned. Used for file sizes, etc. */
void printUnum(unsigned int num)
{
  int digits = 0;

  do {
    pushb(num%10+'0');
    num = num/10;
    digits++;
  }
  while (num > 0);

  while(digits > 0)
  {
    outchar(popb());
    digits--;
  }
}

/*******************************************************************************
 * GPU PEN HELPERS – default / yellow / red (Serial to VGA slave)
 * ----------------------------------------------------------------------------
 * SI resets to green; GPU_COLOR_TICK steps the pen (green→yellow→red). Only these
 * routines plus string bytes from PRINT/LIST should change line color.
 ******************************************************************************/
static void gpu_green(void)
{
  outchar(GPU_COLOR_RESET);
}

static void gpu_yellow(void)
{
  outchar(GPU_COLOR_RESET);
  outchar(GPU_COLOR_TICK);
}

static void gpu_red(void)
{
  outchar(GPU_COLOR_RESET);
  outchar(GPU_COLOR_TICK);
  outchar(GPU_COLOR_TICK);
}

/* testnum: Parse decimal line number at txtpos. Advances txtpos past digits.
 * Returns 0 if no digits (direct mode). Returns 0xFFFF on overflow → qbadline. */
static unsigned short testnum(void)
{
  unsigned short num = 0;
  ignore_blanks();

  while(*txtpos>= '0' && *txtpos <= '9' )
  {
    if(num >= 0xFFFF/10)
    {
      num = 0xFFFF;
      break;
    }

    num = num *10 + *txtpos - '0';
    txtpos++;
  }
  return	num;
}

/* print_quoted_string: If txtpos at " or ', print chars until matching delim.
 * Also accepts UTF-8 smart quotes (E2 80 9C/9D/98/99). Return 1 if printed, 0 else. */
static unsigned char print_quoted_string(void)
{
  int i=0;
  unsigned char delim = *txtpos;
  unsigned char delim_len = 1; /* 1 for ASCII " or ', 3 for UTF-8 */

  if(delim == '"' || delim == '\'')
  {
    txtpos++;
  }
  else if(delim == 0xE2 && txtpos[1] == 0x80 && (txtpos[2] == 0x9C || txtpos[2] == 0x9D || txtpos[2] == 0x98 || txtpos[2] == 0x99))
  {
    delim = txtpos[2]; /* use 3rd byte to match closing */
    delim_len = 3;
    txtpos += 3;
  }
  else
    return 0;

  /* Baseline pen for string body; ` inside string steps from here. */
  gpu_green();

  if(delim_len == 1)
  {
    while(txtpos[i] != delim)
    {
      if(txtpos[i] == NL)
        return 0;
      i++;
    }
    while(*txtpos != delim)
    {
      outchar(*txtpos);
      txtpos++;
    }
    txtpos++;
  }
  else
  {
    while(txtpos[i] != 0xE2 || txtpos[i+1] != 0x80 || txtpos[i+2] != delim)
    {
      if(txtpos[i] == NL)
        return 0;
      i++;
    }
    while(*txtpos != 0xE2 || txtpos[1] != 0x80 || txtpos[2] != delim)
    {
      outchar(*txtpos);
      txtpos++;
    }
    txtpos += 3;
  }

  return 1;
}

static void errorLedOn(void)
{
  digitalWrite(kErrorLedPin, HIGH);
}

static void errorLedOff(void)
{
  digitalWrite(kErrorLedPin, LOW);
}

static void toneErrorEvent(void)
{
  tone(kPiezoPin, 180, 70);
  delay(70);
  tone(kPiezoPin, 120, 90);
  delay(90);
  noTone(kPiezoPin);
}

/* Softer G-major arpeggio + resolution (distinct from setup chime). */
static void toneSystemReady(void)
{
  tone(kPiezoPin, 392, 65);
  delay(65);
  tone(kPiezoPin, 494, 65);
  delay(65);
  tone(kPiezoPin, 587, 65);
  delay(65);
  tone(kPiezoPin, 784, 100);
  delay(100);
  noTone(kPiezoPin);
}

/* Short downward fifth — program cleared. */
static void toneNewEvent(void)
{
  tone(kPiezoPin, 659, 55);
  delay(55);
  tone(kPiezoPin, 440, 75);
  delay(75);
  noTone(kPiezoPin);
}

static void errorLedToneOn(void)
{
  errorLedOn();
  toneErrorEvent();
}

/* printmsgNoNL: Print PROGMEM string to outStream. No newline at end. */
void printmsgNoNL(const unsigned char *msg)
{
  while( pgm_read_byte( msg ) != 0 ) {
    outchar( pgm_read_byte( msg++ ) );
  }
}

/* Single helper for one-line errors (DIV BY ZERO, etc.): red pen + message + CR. */
static void print_red_msg(const unsigned char *msg)
{
  gpu_red();
  printmsgNoNL(msg);
  line_terminator();
}

/* Runtime errors that are not printErrorWithPointer: LED/tone then red message. */
static void print_runtime_red_msg(const unsigned char *msg)
{
  errorLedToneOn();
  print_red_msg(msg);
}

/*******************************************************************************
 * LINE & PROGRAM MANAGEMENT – getln, findline, lineExists, printline
 * ----------------------------------------------------------------------------
 * getln: Print prompt, set txtpos=program_end+2 (skip line number slot). Read
 *   chars from inchar() into buffer. CR/NL terminates. Outside " or ', ` is sent to
 *   the GPU for color only (not stored) so it does not eat buffer or backspaces.
 *   Inside strings, ` is stored and echoed to GPU for color. Backspace toggles
 *   in_dq/in_sq when erasing " or '.
 * findline: Walk from program_start. Return first line with line number >= linenum.
 *   Line length = line[sizeof(LINENUM)]; next line = line + that.
 * lineExists - Set linenum, findline, check if exact match.
 * printline: list_line points at line. Print line number, space, text, NL.
 ******************************************************************************/
/* Echo for getln: outside ` handled in getln (outchar only, not stored). */
static void getln_echo_stored(unsigned char ch, unsigned char *in_dq, unsigned char *in_sq)
{
  if (ch == DQUOTE)
  {
    if (!*in_sq)
      *in_dq = (unsigned char)(!*in_dq);
    outchar(ch);
  }
  else if (ch == SQUOTE)
  {
    if (!*in_dq)
      *in_sq = (unsigned char)(!*in_sq);
    outchar(ch);
  }
  else
    outchar(ch);
}

/* getln(prompt): Print prompt ('>' or '?'), read line into program buffer.
 * prompt: Single char shown before input ('>' for main, '?' for INPUT). */
static void getln(char prompt)
{
  unsigned char in_dq = 0, in_sq = 0;
  outchar(prompt);
  txtpos = program_end+sizeof(LINENUM);

  // When starting a new input line, stop any history browsing
  historyBrowsing = false;

  while(1)
  {
    char c = inchar();
    switch(c)
    {
    case CR:
    {
      // Compute line length (chars typed after prompt); avoid unsigned char wrap on long lines.
      unsigned char *start = program_end + sizeof(LINENUM);
      unsigned int rawLen = (unsigned int)(txtpos - start);
      unsigned char len =
          (rawLen > HISTORY_WIDTH) ? HISTORY_WIDTH : (unsigned char)rawLen;

      // Only store non-empty lines in history (skip blank ENTER presses)
      if (rawLen > 0)
      {

        // Shift older entries back: 0→1, 1→2
        for (unsigned char h = HISTORY_DEPTH - 1; h > 0; h--)
        {
          lastLineLen[h] = lastLineLen[h - 1];
          for (unsigned char i = 0; i < lastLineLen[h]; i++)
            lastLineBuf[h][i] = lastLineBuf[h - 1][i];
        }

        // Store newest at index 0
        lastLineLen[0] = len;
        for (unsigned char i = 0; i < len; i++)
          lastLineBuf[0][i] = start[i];

        // Update count (max HISTORY_DEPTH)
        if (historyCount < HISTORY_DEPTH)
          historyCount++;
      }

      // Leaving line entry resets browsing state
      historyBrowsing = false;
      historyIndex = 0;

      line_terminator();
      txtpos[0] = NL;
      return;
    }
    case NL:
      /* On this system, the keyboard "down" key behaves like a newline.
       * Treat NL as "history down" while browsing, otherwise ignore it so
       * it doesn't act like a second ENTER. */
      if (historyBrowsing && historyCount > 0)
      {
        if (historyIndex > 0)
        {
          historyIndex--;

          unsigned char len = lastLineLen[historyIndex];

          // Erase current input back to the prompt
          while (txtpos > program_end + sizeof(LINENUM))
          {
            txtpos--;
            outchar(CTRLH);
          }

          // Re-type the newer history line
          in_dq = 0;
          in_sq = 0;
          for (unsigned char i = 0; i < len; i++)
          {
            unsigned char chh = lastLineBuf[historyIndex][i];
            if (chh == GPU_COLOR_TICK && !in_dq && !in_sq)
              continue;
            txtpos[0] = chh;
            txtpos++;
            getln_echo_stored(chh, &in_dq, &in_sq);
          }
        }
        else
        {
          // At newest entry and user pressed down: exit history browsing,
          // leaving a blank line ready for fresh input.
          historyBrowsing = false;

          while (txtpos > program_end + sizeof(LINENUM))
          {
            txtpos--;
            outchar(CTRLH);
          }
        }
      }
      break;
    default:
      // Up-arrow: step backwards through command history (up to HISTORY_DEPTH)
      if (c == PS2_UPARROW)
      {
        if (historyCount > 0)
        {
          // On first up-arrow, start at the newest (index 0).
          // Further up-arrows walk back until the oldest available.
          if (!historyBrowsing)
          {
            historyBrowsing = true;
            historyIndex = 0;
          }
          else if (historyIndex + 1 < historyCount)
          {
            historyIndex++;
          }

          unsigned char len = lastLineLen[historyIndex];

          // Erase current input back to the prompt
          while (txtpos > program_end + sizeof(LINENUM))
          {
            txtpos--;
            outchar(CTRLH);
          }

          // Re-type the last line into the buffer and on screen
          in_dq = 0;
          in_sq = 0;
          for (unsigned char i = 0; i < len; i++)
          {
            unsigned char chh = lastLineBuf[historyIndex][i];
            if (chh == GPU_COLOR_TICK && !in_dq && !in_sq)
              continue;
            txtpos[0] = chh;
            txtpos++;
            getln_echo_stored(chh, &in_dq, &in_sq);
          }
        }
      }
      // Down-arrow: step forwards toward newer history, or clear to blank
      else if (c == PS2_DOWNARROW)
      {
        if (historyBrowsing)
        {
          if (historyIndex > 0)
          {
            historyIndex--;

            unsigned char len = lastLineLen[historyIndex];

            // Erase current input back to the prompt
            while (txtpos > program_end + sizeof(LINENUM))
            {
              txtpos--;
              outchar(CTRLH);
            }

            // Re-type the newer history line
            in_dq = 0;
            in_sq = 0;
            for (unsigned char i = 0; i < len; i++)
            {
              unsigned char chh = lastLineBuf[historyIndex][i];
              if (chh == GPU_COLOR_TICK && !in_dq && !in_sq)
                continue;
              txtpos[0] = chh;
              txtpos++;
              getln_echo_stored(chh, &in_dq, &in_sq);
            }
          }
          else
          {
            // At newest entry and user pressed down: exit history browsing,
            // leaving a blank line ready for fresh input.
            historyBrowsing = false;

            while (txtpos > program_end + sizeof(LINENUM))
            {
              txtpos--;
              outchar(CTRLH);
            }
          }
        }
      }
      else if(isBackspaceKey(c))
      {
        if(txtpos == program_end+sizeof(LINENUM))
          break;
        txtpos--;
        /* Keep in_dq/in_sq in sync with buffer so ` echo matches real strings. */
        {
          unsigned char rm = *txtpos;
          if (rm == DQUOTE && !in_sq)
            in_dq = (unsigned char)!in_dq;
          else if (rm == SQUOTE && !in_dq)
            in_sq = (unsigned char)!in_sq;
        }
        outchar(CTRLH);
      }
      else if(!isPrintableInput(c))
      {
      }
      else if(txtpos >= program + kRamSize - (int)sizeof(LINENUM))
      {
        outchar(BELL);
      }
      else
      {
        unsigned char ch = (unsigned char)c;
        if (ch == GPU_COLOR_TICK && !in_dq && !in_sq)
        {
          /* GPU color step only; not stored (manual / header). History skips outside ` */
          outchar(GPU_COLOR_TICK);
          break;
        }
        txtpos[0] = ch;
        txtpos++;
        getln_echo_stored(ch, &in_dq, &in_sq);
      }
      break;
    }
  }
}

/*******************************************************************************
 * findline – first line with number >= global linenum
 * ----------------------------------------------------------------------------
 * Walk from program_start. Line stride = line[sizeof(LINENUM)] (full record len).
 ******************************************************************************/
static unsigned char *findline(void)
{
  unsigned char *line = program_start;
  while(1)
  {
    if(line == program_end)
      return line;

    if(((LINENUM *)line)[0] >= linenum)
      return line;

    line += line[sizeof(LINENUM)];
  }
}

/*******************************************************************************
 * lineExists – exact line number present
 * ----------------------------------------------------------------------------
 * Temporarily sets linenum, findline; true iff hit matches target. Restores
 * txtpos and linenum.
 ******************************************************************************/
static unsigned char lineExists(LINENUM target)
{
  unsigned char *saved_txtpos = txtpos;
  LINENUM saved_linenum = linenum;
  unsigned char result;

  linenum = target;
  txtpos = findline();
  result = (txtpos != program_end && ((LINENUM *)txtpos)[0] == target);

  txtpos = saved_txtpos;
  linenum = saved_linenum;
  return result;
}

/*******************************************************************************
 * next_program_line – advance to following program record
 * ----------------------------------------------------------------------------
 * Layout: [LINENUM][len byte][text through NL]. Returns program_end if past end.
 ******************************************************************************/
static unsigned char *next_program_line(unsigned char *line)
{
  if(line == NULL || line >= program_end)
    return program_end;
  return line + line[sizeof(LINENUM)];
}

/*******************************************************************************
 * find_data_line_from – locate next DATA line
 * ----------------------------------------------------------------------------
 * Walk physical lines from line_start (inclusive) toward program_end. If a
 * line’s text (after header) begins with DATA, return that line’s base pointer.
 * Otherwise advance by line[sizeof(LINENUM)] (full record length). Restores
 * txtpos for caller. Returns NULL if none. Used by READ to open/continue stream
 * and by RESTORE anchor + READ together (RESTORE n → findline → first search).
 ******************************************************************************/
static unsigned char *find_data_line_from(unsigned char *line_start)
{
  unsigned char *saved_txtpos = txtpos;

  while(line_start != program_end)
  {
    txtpos = line_start + sizeof(LINENUM) + 1;
    ignore_blanks();
    scantable(keywords);
    if(table_index == KW_DATA)
    {
      txtpos = saved_txtpos;
      return line_start;
    }
    line_start += line_start[sizeof(LINENUM)];
  }
  txtpos = saved_txtpos;
  return NULL;
}

/*******************************************************************************
 * data_reset_pointers – clear READ/RESTORE stream state
 ******************************************************************************/
static void data_reset_pointers(void)
{
  data_read_start_line = NULL;
  data_cur_line = NULL;
  data_cur_pos = NULL;
}

/*******************************************************************************
 * data_parse_number – integer literal inside DATA item list
 * ----------------------------------------------------------------------------
 * Optional leading '-', digits required. Skips trailing comma. 0 = parse fail.
 ******************************************************************************/
static unsigned char data_parse_number(short int *out)
{
  unsigned char neg = 0;

  ignore_blanks();
  if(*txtpos == '-')
  {
    neg = 1;
    txtpos++;
  }
  if(*txtpos < '0' || *txtpos > '9')
    return 0;

  short int v = 0;
  while(*txtpos >= '0' && *txtpos <= '9')
  {
    v = (short int)(v * 10 + (*txtpos - '0'));
    txtpos++;
  }
  if(neg)
    v = (short int)-v;
  *out = v;
  ignore_blanks();
  if(*txtpos == ',')
    txtpos++;
  ignore_blanks();
  return 1;
}

/*******************************************************************************
 * printErrorWithPointer – syntax-style error + optional " IN <line>"
 ******************************************************************************/
static void printErrorWithPointer(const unsigned char *msg)
{
  errorLedToneOn();
  gpu_red();
  // Print error message, optionally followed by " IN <line>" if we are
  // currently executing a program line (current_line != 0).
  printmsgNoNL(msg);
  {
    LINENUM ln = currentLineNumber();
    if (ln != 0)
    {
      printmsgNoNL(inmsg);
      printnum(ln);
    }
  }
  line_terminator();
}

/*******************************************************************************
 * currentLineNumber – 0 in direct mode; else LINENUM at current_line
 ******************************************************************************/
static LINENUM currentLineNumber(void)
{
  if(current_line == NULL || current_line == program_end)
    return 0;
  return *((LINENUM *)current_line);
}

/*******************************************************************************
 * MEM screen – SRAM / BASIC / EEPROM usage bars
 * ----------------------------------------------------------------------------
 * memPrintBar draws ~-filled row. Order: SRAM (yellow), BASIC (green), EEPROM
 * (red). Stats text: label left, "a/b free" right-padded in MEM_STATS_LINE_CHARS.
 * Ends with gpu_green for prompt.
 * SRAM (yellow): runtime bytes free between heap and stack (AVR classic &v − brk).
 *   Shown as xxx/kRamSize (1024) to pair with BASIC’s 1024-byte line buffer on a
 *   2 KiB part; value is capped at 1024 for display if headroom exceeds that.
 *   Snapshot when MEM runs (call depth affects the number slightly).
 ******************************************************************************/
#if defined(__AVR__)
/* Bytes currently available between end-of-heap and stack pointer (runtime). */
static int avrFreeRamBetweenHeapAndStack(void)
{
  extern int __heap_start;
  extern void *__brkval;
  int here;
  return (int)&here - (int)((__brkval == 0) ? (void *)&__heap_start : __brkval);
}
#endif

/* MEM text row: label flush left, value flush right within this width (~GPU row). */
#define MEM_STATS_LINE_CHARS 24

static unsigned char mem_str_len8(const char *s)
{
  unsigned char n = 0;
  while (s[n])
    n++;
  return n;
}

static unsigned char mem_u_dec_width8(unsigned n)
{
  if (n >= 1000)
    return 4;
  if (n >= 100)
    return 3;
  if (n >= 10)
    return 2;
  return 1;
}

static void mem_print_stats_line(const char *label, int a, int b)
{
  unsigned char lab = mem_str_len8(label);
  unsigned char tail = (unsigned char)(mem_u_dec_width8((unsigned)a) + 1U +
                                         mem_u_dec_width8((unsigned)b) + 5U); /* " free" */
  int pad = (int)MEM_STATS_LINE_CHARS - (int)lab - (int)tail;
  if (pad < 1)
    pad = 1;
  Serial.print(label);
  while (pad--)
    Serial.write(' ');
  Serial.print(a);
  Serial.print('/');
  Serial.print(b);
  Serial.println(F(" free"));
}

static void mem_print_stats_line_text(const char *label, const char *rhs)
{
  unsigned char lab = mem_str_len8(label);
  unsigned char r = mem_str_len8(rhs);
  int pad = (int)MEM_STATS_LINE_CHARS - (int)lab - (int)r;
  if (pad < 1)
    pad = 1;
  Serial.print(label);
  while (pad--)
    Serial.write(' ');
  Serial.println(rhs);
}

static void memPrintBar(int num, int den)
{
  int filled, k;
  if (den <= 0)
    den = 1;
  filled = (num * 22) / den;
  if (filled > 22)
    filled = 22;
  if (filled < 0)
    filled = 0;
  Serial.print("[");
  for (k = 0; k < filled; k++)
    Serial.write(GPU_BLOCK);
  for (; k < 22; k++)
    Serial.write(' ');
  Serial.println("]");
}

static void showMemoryScreen(void)
{
#if defined(__AVR__)
  int sramFree = avrFreeRamBetweenHeapAndStack();
  if (sramFree < 0)
    sramFree = 0;
  /* Same 1024 scale as BASIC row (half of 2 KiB on ATmega328p-class chips). */
  int sramFreeDisp = sramFree;
  if (sramFreeDisp > (int)kRamSize)
    sramFreeDisp = (int)kRamSize;

  gpu_yellow();
  mem_print_stats_line("SRAM ", sramFreeDisp, (int)kRamSize);
  delay(150);
  memPrintBar(sramFreeDisp, (int)kRamSize);
  delay(150);
#else
  gpu_yellow();
  mem_print_stats_line_text("SRAM ", "n/a");
  delay(150);
#endif

  {
    int basicFree = (int)((program + kRamSize) - program_end);
    if (basicFree < 0)
      basicFree = 0;
    if (basicFree > (int)kRamSize)
      basicFree = (int)kRamSize;
    gpu_green();
    mem_print_stats_line("BASIC ", basicFree, (int)kRamSize);
    delay(150);
    memPrintBar(basicFree, (int)kRamSize);
    delay(150);
  }

  {
    int eeTot = (int)(E2END) + 1;
    int eeFree = eeTot - eepromUsedBytes();
    if (eeFree < 0)
      eeFree = 0;
    if (eeFree > eeTot)
      eeFree = eeTot;
    gpu_red();
    mem_print_stats_line("EEPROM ", eeFree, eeTot);
    delay(150);
    memPrintBar(eeFree, eeTot);
    delay(150);
  }
  gpu_green();
}

/*******************************************************************************
 * eepromUsedBytes – count bytes until first zero (Arduino EEPROM image)
 ******************************************************************************/
static int eepromUsedBytes(void)
{
  int used = 0;
  for (int i = 0; i <= E2END; i++)
  {
    if (EEPROM.read(i) == 0)
      break;
    used++;
  }
  return used;
}

/*******************************************************************************
 * toUppercaseBuffer – normalize keywords on freshly entered line
 * ----------------------------------------------------------------------------
 * program_end+sizeof(LINENUM) .. NL: lowercase a-z → A-Z outside quotes.
 ******************************************************************************/
static void toUppercaseBuffer(void)
{
  unsigned char *c = program_end+sizeof(LINENUM);
  unsigned char quote = 0;

  while(*c != NL)
  {
    if(*c == quote)
      quote = 0;
    else if(*c == '"' || *c == '\'')
      quote = *c;
    else if(quote == 0 && *c >= 'a' && *c <= 'z')
      *c = *c + 'A' - 'a';
    c++;
  }
}

/*******************************************************************************
 * printline – emit one program line to outStream
 * ----------------------------------------------------------------------------
 * list_line points at line record; advances past line. Used by LIST, ESAVE.
 * Serial: gpu_green at line start; green before " and ' delimiters; ` in strings
 * steps VGA pen. EEPROM save path unchanged.
 ******************************************************************************/
void printline()
{
  LINENUM line_num;

  line_num = *((LINENUM *)(list_line));
  list_line += sizeof(LINENUM) + sizeof(char);

  if (outStream == kStreamSerial)
    gpu_green();
  printnum(line_num);
  outchar(' ');
  while(*list_line != NL)
  {
    unsigned char ch = *list_line;
    if (outStream == kStreamSerial && (ch == DQUOTE || ch == SQUOTE))
      gpu_green();
    outchar(ch);
    list_line++;
  }
  list_line++;
  line_terminator();
}

/*******************************************************************************
 * EXPRESSION EVALUATION – Pratt-style recursive descent
 * ----------------------------------------------------------------------------
 * expr4:
 *   Unary minus, literals, variables A..Z, funcs (ABS, AREAD, DREAD, RND),
 *   parenthesized expr.
 * expr3:
 *   *, / (left-assoc).
 * expr2:
 *   +, - (left-assoc); leading +/- as 0+expr / 0-expr.
 * expression:
 *   expr2, optional relop, expr2 (relops yield 0 or 1).
 * expression_error / expression_error_code:
 *   Div-by-zero and parse failures.
 ******************************************************************************/
static short int expr4(void)
{
  ignore_blanks();

  if( *txtpos == '-' ) {
    txtpos++;
    return -expr4();
  }

  if(*txtpos == '0')
  {
    txtpos++;
    return 0;
  }

  if(*txtpos >= '1' && *txtpos <= '9')
  {
    short int a = 0;
    do 	{
      a = a*10 + *txtpos - '0';
      txtpos++;
    } 
    while(*txtpos >= '0' && *txtpos <= '9');
    return a;
  }

  if(txtpos[0] >= 'A' && txtpos[0] <= 'Z')
  {
    short int a;
    if(txtpos[1] < 'A' || txtpos[1] > 'Z')
    {
      a = ((short int *)variables_begin)[*txtpos - 'A'];
      txtpos++;
      return a;
    }

    scantable(func_tab);
    if(table_index == FUNC_UNKNOWN)
      goto expr4_error;

    unsigned char f = table_index;

    if(*txtpos != '(')
      goto expr4_error;

    txtpos++;
    a = expression();
    if(*txtpos != ')')
      goto expr4_error;
    txtpos++;
    switch(f)
    {
    case FUNC_ABS:
      if(a < 0) 
        return -a;
      return a;

    case FUNC_AREAD:
      pinMode( a, INPUT );
      return analogRead( a );                        
    case FUNC_DREAD:
      pinMode( a, INPUT );
      return digitalRead( a );

    case FUNC_RND:
      return( random( a ));
    }
  }

  if(*txtpos == '(')
  {
    short int a;
    txtpos++;
    a = expression();
    if(*txtpos != ')')
      goto expr4_error;

    txtpos++;
    return a;
  }

expr4_error:
  expression_error = 1;
  if(expression_error_code == 0)
    expression_error_code = 1;
  return 0;

}

/*******************************************************************************
 * expr3 – multiplication and division (left-associative)
 ******************************************************************************/
static short int expr3(void)
{
  short int a,b;

  a = expr4();

  ignore_blanks(); // fix for eg:  100 a = a + 1

  while(1)
  {
    if(*txtpos == '*')
    {
      txtpos++;
      b = expr4();
      a *= b;
    }
    else if(*txtpos == '/')
    {
      txtpos++;
      b = expr4();
      if(b != 0)
        a /= b;
      else
      {
        expression_error = 1;
        expression_error_code = 2;
      }
    }
    else
      return a;
  }
}

/*******************************************************************************
 * expr2 – addition and subtraction (left-associative)
 ******************************************************************************/
static short int expr2(void)
{
  short int a,b;

  if(*txtpos == '-' || *txtpos == '+')
    a = 0;
  else
    a = expr3();

  while(1)
  {
    if(*txtpos == '-')
    {
      txtpos++;
      b = expr3();
      a -= b;
    }
    else if(*txtpos == '+')
    {
      txtpos++;
      b = expr3();
      a += b;
    }
    else
      return a;
  }
}

/*******************************************************************************
 * expression – expr2 plus optional relational tail
 ******************************************************************************/
static short int expression(void)
{
  short int a,b;

  a = expr2();

  if(expression_error)	return a;

  scantable(relop_tab);
  if(table_index == RELOP_UNKNOWN)
    return a;

  switch(table_index)
  {
  case RELOP_GE:
    b = expr2();
    if(a >= b) return 1;
    break;
  case RELOP_NE:
  case RELOP_NE_BANG:
    b = expr2();
    if(a != b) return 1;
    break;
  case RELOP_GT:
    b = expr2();
    if(a > b) return 1;
    break;
  case RELOP_EQ:
    b = expr2();
    if(a == b) return 1;
    break;
  case RELOP_LE:
    b = expr2();
    if(a <= b) return 1;
    break;
  case RELOP_LT:
    b = expr2();
    if(a < b) return 1;
    break;
  }
  return 0;
}

/*******************************************************************************
 * MAIN LOOP – boot, warmstart, prompt, command dispatch
 * ----------------------------------------------------------------------------
 * After boot (password correct), loop never re-enters boot. warmstart runs
 * once per "session". prompt→getln→merge/direct→interperateAtTxtpos. Commands
 * use goto (warmstart, prompt, execline, execnextline, etc.).
 ******************************************************************************/
void loop()
{
/*******************************************************************************
 * BOOT – border, password, loading sequence
 * ----------------------------------------------------------------------------
 * Border - ` steps color (green→yellow→red) in art; ~ = block. Start gpu_green()
 * so first ` is predictable. Password prompt green; wrong password red; WELCOME/System OK green.
 ******************************************************************************/
  delay(BOOT_DELAY_START_MS);
  outchar(GPU_CLEAR_SCREEN);
  delay(BOOT_DELAY_AFTER_CLS_MS);
  gpu_green();

  BOOT_PRINT_GRID();
  delay(BOOT_DELAY_LOGO_MS);

  {
    char buf[8], c;
    byte i, j;
    bool firstPrompt = true;
    for (;;) {
      i = 0;
      if (firstPrompt) {
        gpu_green();
        Serial.print(F("Password: "));
        firstPrompt = false;
      }

      while (true) {
        while (!keyboard.available());  // wait for a real key
        c = keyboard.read();
        if (c == 13) break;
        if (isBackspaceKey(c)) {
          if (i > 0) {
            i--;
            Serial.write(8);
            Serial.write(' ');
            Serial.write(8);
          }
          continue;
        }
        if (!isPrintableInput(c)) {
          continue;
        }
        if (i < 8) {
          buf[i++] = c;
          Serial.write('*');
        }
      }

      if (boot_password_ok(buf, i)) {
        outchar(GPU_CLEAR_SCREEN);
        outchar(GPU_CLEAR_SCREEN);
        showMemoryScreen();
        delay(BOOT_DELAY_POST_MEM_MS);

        outchar(GPU_CLEAR_SCREEN);
        delay(BOOT_DELAY_AFTER_WELCOME_CLS_MS);
        gpu_green();
        Serial.println(F("WELCOME IntelGen_V2"));
        delay(BOOT_DELAY_WELCOME_LINE_MS);
        Serial.println(F("System OK"));
        omit_next_warmstart_ok = 1;
        toneSystemReady();
        break;
      }

/*******************************************************************************
 * WRONG PASSWORD – erase, show Incorrect Pass, retry
 ******************************************************************************/
      while (i > 0) {
        Serial.write(8);
        Serial.write(' ');
        Serial.write(8);
        i--;
      }
      for (j = 0; j < 10; j++) {
        Serial.write(8);
        Serial.write(' ');
        Serial.write(8);
      }
      gpu_red();
      Serial.print(F("Incorrect Pass"));
      delay(BOOT_DELAY_WRONG_PASS_MS);
      for (j = 0; j < 14; j++) {
        Serial.write(8);
        Serial.write(' ');
        Serial.write(8);
      }
      gpu_green();
      Serial.print(F("Password: "));
    }
  }

  unsigned char *start;
  unsigned char *newEnd;
  unsigned int linelen;
  boolean isDigital;
  boolean alsoWait = false;
  int val; /* Shared scratch: DELAY ms, IF condition, EEPROM byte in ELIST, etc. */

  noTone( kPiezoPin );

/*******************************************************************************
 * WARMSTART / PROMPT / EXECUTE – session tail of loop() (after boot password)
 * ----------------------------------------------------------------------------
 * Labels warmstart, prompt, merge, q*, run_next_statement, execline, and
 * command targets (list, print, …) form the interpreter state machine until BYE.
 ******************************************************************************/
warmstart:
  current_line = 0;
  sp = interp_for_stack + STACK_SIZE;
  if( omit_next_warmstart_ok ) {
    omit_next_warmstart_ok = 0;
  } else {
    gpu_green();
    printmsgNoNL(okmsg);
    line_terminator();
  }

prompt:
  if( triggerRun ){
    triggerRun = false;
    current_line = program_start;
    errorLedOff();
    goto execline;
  }

  gpu_green();

  /* Drain Serial so leftover bytes (e.g. after PC closes port) don't get
   * interpreted as keypresses and cause "all backspace" behaviour. */
  while(Serial.available())
    Serial.read();

  getln( '>' );
  toUppercaseBuffer();

/*******************************************************************************
 * LINE ENTRY – parse line number, merge into program
 * ----------------------------------------------------------------------------
 * User typed "20 PRINT X". Buffer at program_end+2. First - reverse copy line
 * to high memory (program+kRamSize-1 down) so we can parse from start.
 * testnum() parses line number. 0 = direct. 0xFFFF = overflow → qbadline.
 * linelen = text length + 1 (NL) + 3 (header). Write header at txtpos-3.
 * findline() → insertion point. If line exists: compact (remove old line).
 * If txtpos+3.. = NL - delete (line number only). goto prompt.
 * Insert - while linelen>0, shuffle bytes from program_end toward txtpos to make
 * space. space_to_make = min(txtpos-program_end, linelen). Copy backwards.
 ******************************************************************************/
  txtpos = program_end+sizeof(unsigned short);
  while(*txtpos != NL)
    txtpos++;

  {
    unsigned char *dest;
    dest = program + kRamSize - 1;
    while(1)
    {
      *dest = *txtpos;
      if(txtpos == program_end+sizeof(unsigned short))
        break;
      dest--;
      txtpos--;
    }
    txtpos = dest;
  }

  linenum = testnum();
  ignore_blanks();
  if(linenum == 0)
    goto direct;

  if(linenum == 0xFFFF)
    goto qbadline;

  linelen = 0;
  while(txtpos[linelen] != NL)
    linelen++;
  linelen++;
  linelen += sizeof(unsigned short)+sizeof(char);

  if (linelen > 255)
    goto qlinetoolong;

  txtpos -= 3;
  *((unsigned short *)txtpos) = linenum;
  txtpos[sizeof(LINENUM)] = (unsigned char)linelen;


  start = findline();

  /* Remove existing line with same number: compact program by copying bytes
   * from (start+line_len)..program_end down to start. */
  if(start != program_end && *((LINENUM *)start) == linenum)
  {
    unsigned char *dest, *from;
    unsigned tomove;

    from = start + start[sizeof(LINENUM)];  /* first byte after this line */
    dest = start;

    tomove = program_end - from;
    while( tomove > 0)
    {
      *dest = *from;
      from++;
      dest++;
      tomove--;
    }	
    program_end = dest;
  }

  if(txtpos[sizeof(LINENUM)+sizeof(char)] == NL)
  {
    errorLedOff();
    goto prompt;
  }

  if(program_end + linelen >= program + kRamSize)
    goto qoom;

  /* Insert new line: make space by shifting program_end upward. Copy in
   * chunks. space_to_make = gap between program_end and txtpos. Copy bytes
   * from program_end backward to newEnd, then copy line text into start. */
  while(linelen > 0)
  {	
    unsigned int tomove;
    unsigned char *from,*dest;
    unsigned int space_to_make;

    space_to_make = txtpos - program_end;

    if(space_to_make > linelen)
      space_to_make = linelen;
    newEnd = program_end+space_to_make;
    tomove = program_end - start;


    from = program_end;
    dest = newEnd;
    while(tomove > 0)
    {
      from--;
      dest--;
      *dest = *from;
      tomove--;
    }

    for(tomove = 0; tomove < space_to_make; tomove++)
    {
      *start = *txtpos;
      txtpos++;
      start++;
      linelen--;
    }
    program_end = newEnd;
  }
  errorLedOff();
  goto prompt;

/* Error labels: use GOTO_DIV0_OR_EXPRESSION_ERROR / GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR
 * at failure sites (replaces legacy HOW/WHAT routing). qcmd=unknown command.
 * qexpression=EXPRESSION ERROR. qbadline=line number. qoom=out of memory.
 * qreturn=GOSUB ERROR (no matching GOSUB). qlooperr=NEXT without matching FOR. */
qsyntax:
  printErrorWithPointer(syntaxmsg);
  goto prompt;

qcmd:
  printErrorWithPointer(cmdmsg);
  goto prompt;

qexpression:
  printErrorWithPointer(expressionerrmsg);
  goto prompt;

qlooperr:
  printErrorWithPointer(looperrmsg);
  goto prompt;

qoutofdata:
  printErrorWithPointer(outofdatamsg);
  goto prompt;

qbadline:
  printErrorWithPointer(badlinemsg);
  goto prompt;

qtickerr:
  printErrorWithPointer(tickerrmsg);
  goto prompt;

qdivzero:
  print_runtime_red_msg(divzeromsg);
  goto prompt;

qstack:
  print_runtime_red_msg(stackoverflowmsg);
  goto warmstart;

qoom:
  print_runtime_red_msg(outofmemorymsg);
  goto prompt;

qlinetoolong:
  printErrorWithPointer(linelengthmsg);
  goto prompt;

qreturn:
  print_runtime_red_msg(returnmsg);
  goto warmstart;

/*******************************************************************************
 * USER BREAK – ESC during RUN (breakcheck at each statement)
 * ----------------------------------------------------------------------------
 * Same message as breakcheck: BREAK IN <line>, then warmstart.
 ******************************************************************************/
user_break_handler:
  gpu_red();
  printmsgNoNL(breakmsg);
  printmsgNoNL(inmsg);
  printnum(currentLineNumber());
  line_terminator();
  goto warmstart;

/*******************************************************************************
 * STATEMENT & LINE FLOW – run_next_statement, direct, execnextline, execline
 * ----------------------------------------------------------------------------
 * run_next_statement:
 *   Skip ':' separators, ignore_blanks. If NL → execnextline.
 *   Else → interperateAtTxtpos (next statement).
 * direct:
 *   txtpos = program_end+sizeof(LINENUM). If NL → empty line, goto prompt.
 *   Else interperateAtTxtpos (stray ` after blanks → tick error).
 * execnextline:
 *   current_line += line_length (next line). goto execline.
 * execline:
 *   If current_line == program_end → warmstart (RUN finished).
 *   Else txtpos past header, goto interperateAtTxtpos.
 ******************************************************************************/
run_next_statement:
  while(*txtpos == ':')
    txtpos++;
  ignore_blanks();
  if(*txtpos == NL)
    goto execnextline;
  goto interperateAtTxtpos;

direct:
  txtpos = program_end+sizeof(LINENUM);
  if(*txtpos == NL)
    goto prompt;

interperateAtTxtpos:
  if(breakcheck())
    goto user_break_handler;

  IGNORE_AND_REJECT_CMD_TICK();
  if(*txtpos == NL)
    goto execnextline;

  scantable(keywords);  /* txtpos advances past keyword, table_index = KW_xxx */

  switch(table_index)
  {
  case KW_DELAY:
    {
      IGNORE_AND_REJECT_CMD_TICK();
      CLEAR_EXPR_ERR();
      val = expression();
      delay( val );
      goto run_next_statement;
    }

  case KW_LIST:
    goto list;
  case KW_CLS:
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    outchar(GPU_CLEAR_SCREEN);
    errorLedOff();
    goto run_next_statement;
  case KW_MEM:
    goto mem;
  case KW_HI:
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    hi_print_random();
    line_terminator();
    goto run_next_statement;
  case KW_NEW:
    if(txtpos[0] != NL)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    program_end = program_start;
    data_reset_pointers();
    toneNewEvent();
    goto execnextline;
  case KW_RUN:
    data_reset_pointers();
    current_line = program_start;
    errorLedOff();
    goto execline;
  case KW_NEXT:
    goto next;
  case KW_IF:
    IGNORE_AND_REJECT_CMD_TICK();
    CLEAR_EXPR_ERR();
    val = expression();
    if(expression_error || *txtpos == NL)
      GOTO_DIV0_OR_EXPRESSION_ERROR();
    if(val != 0)
      goto interperateAtTxtpos;
    goto execnextline;

  case KW_THEN:
    goto interperateAtTxtpos;

  case KW_GOTO:
    IGNORE_AND_REJECT_CMD_TICK();
    CLEAR_EXPR_ERR();
    linenum = expression();
    if(expression_error || (*txtpos != NL && *txtpos != ':') || !lineExists(linenum))
      goto qbadline;
    current_line = findline();
    goto execline;

  case KW_GOSUB:
    goto gosub;
  case KW_RETURN:
    goto gosub_return; 
  case KW_REM:
    goto execnextline;	// Ignore line completely
  case KW_DATA:
    goto execnextline;	// DATA items are consumed by READ only
  case KW_READ:
    goto readstmt;
  case KW_RESTORE:
    goto restorestmt;
  case KW_FOR:
    goto forloop; 
  case KW_INPUT:
  case KW_INPUT_QMARK:
    goto input; 
  case KW_PRINT:
  case KW_DOT_PRINT:
    goto print;
  case KW_END:
    if(txtpos[0] != NL)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    current_line = program_end;
    goto execline;

  case KW_BYE:
    errorLedOff();
    return;

  case KW_AWRITE:  // AWRITE <pin>, HIGH|LOW
    isDigital = false;
    goto awrite;
  case KW_DWRITE:  // DWRITE <pin>, HIGH|LOW
    isDigital = true;
    goto dwrite;

  case KW_RSEED:
    goto rseed;

  case KW_TONEW:
  case KW_TONEW_BANG:
    alsoWait = true;
    /* fall through */
  case KW_TONE:
    goto tonegen;
  case KW_NOTONE:
    goto tonestop;

  case KW_EFORMAT:
    goto eformat;
  case KW_ESAVE:
    goto esave;
  case KW_ELOAD:
    goto eload;
  case KW_ELIST:
    goto elist;
  case KW_ECHAIN:
    goto echain;

  /* KW_DEFAULT - assignment x = expr (bare form only). Must start with A..Z
   * followed by optional spaces and '='. Else → qcmd (unknown command). */
  case KW_DEFAULT:
    {
      unsigned char *check = txtpos;
      if(*check >= 'A' && *check <= 'Z')
      {
        check++;
        while(*check == SPACE || *check == TAB)
          check++;
        if(*check == '=')
          goto assignment;
      }
      goto qcmd;
    }
  default:
    break;
  }

execnextline:
  if(current_line == NULL) {		// Finished direct line successfully
    errorLedOff();
    goto prompt;
  }
  current_line +=	 current_line[sizeof(LINENUM)];

execline:
  if(current_line == program_end) // Out of lines to run
    goto warmstart;
  txtpos = current_line+sizeof(LINENUM)+sizeof(char);
  goto interperateAtTxtpos;

/* EEPROM commands: ELIST (list until \0), EFORMAT (zero all), ESAVE, ELOAD,
 * ECHAIN (load + run). ESAVE writes program via printline() to outStream=EEPROM. */
elist:
  {
    int i;
    for( i = 0 ; i < (E2END +1) ; i++ )
    {
      val = EEPROM.read( i );

      if( val == '\0' ) {
        goto execnextline;
      }

      if( ((val < ' ') || (val  > '~')) && (val != NL) && (val != CR))  {
        outchar( '?' );
      } 
      else {
        outchar( val );
      }
    }
  }
  goto execnextline;

eformat:
  {
    /* Cover 0..E2END inclusive (last byte was skipped by i < E2END). */
    for (int i = 0; i <= (int)E2END; i++)
    {
      if( (i & 0x03f) == 0x20 ) outchar( '.' );
      EEPROM.write( i, 0 );
    }
    outchar( LF );
  }
  goto execnextline;

esave:
  errorLedOff();
  {
    outStream = kStreamEEProm;
    eepos = 0;

    list_line = findline();
    while(list_line != program_end) {
      printline();
    }
    outchar('\0');

    outStream = kStreamSerial;
    
    goto warmstart;
  }
  
  
echain:
  runAfterLoad = true;

eload:
  errorLedOff();
  program_end = program_start;
  data_reset_pointers();

  eepos = 0;
  inStream = kStreamEEProm;
  inhibitOutput = true;
  delay(EEPROM_LOAD_START_DELAY_MS);
  goto warmstart;

/* INPUT - Parse variable (A..Z). getln('?'), parse expression from input buffer.
 * expression_error → inputagain (retry). Store value in variables_begin[var-'A']. */
input:
  {
    unsigned char var;
    int value;
    IGNORE_AND_REJECT_CMD_TICK();
    if(*txtpos < 'A' || *txtpos > 'Z')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    var = *txtpos;
    txtpos++;
    ignore_blanks();
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
inputagain:
    tmptxtpos = txtpos;
    getln( '?' );
    toUppercaseBuffer();
    txtpos = program_end+sizeof(unsigned short);
    ignore_blanks();
    CLEAR_EXPR_ERR();
    value = expression();
    if(expression_error)
      goto inputagain;
    ((short int *)variables_begin)[var-'A'] = value;
    txtpos = tmptxtpos;

    goto run_next_statement;
  }

/* FOR - Parse var=initial TO terminal [STEP step]. Push stack_for_frame (var,
 * terminal, step, txtpos, current_line). Set variable = initial. goto run_next_statement. */
forloop:
  {
    unsigned char var;
    short int initial, step, terminal;
    IGNORE_AND_REJECT_CMD_TICK();
    if(*txtpos < 'A' || *txtpos > 'Z')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    var = *txtpos;
    txtpos++;
    ignore_blanks();
    if(*txtpos != '=')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    txtpos++;
    ignore_blanks();

    CLEAR_EXPR_ERR();
    initial = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    scantable(to_tab);
    if(table_index != 0)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    terminal = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    scantable(step_tab);
    if(table_index == 0)
    {
      step = expression();
      if(expression_error)
        GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    }
    else
      step = 1;
    ignore_blanks();
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();


    if(*txtpos == NL || *txtpos == ':')
    {
      struct stack_for_frame *f;
      if(sp + sizeof(struct stack_for_frame) < stack_limit)
        goto qstack;

      sp -= sizeof(struct stack_for_frame);
      f = (struct stack_for_frame *)sp;
      ((short int *)variables_begin)[var-'A'] = initial;
      f->frame_type = STACK_FOR_FLAG;
      f->for_var = var;
      f->terminal = terminal;
      f->step     = step;
      f->txtpos   = txtpos;
      f->current_line = current_line;
      goto run_next_statement;
    }
  }
  GOTO_DIV0_OR_EXPRESSION_ERROR();

/* GOSUB - expression() → linenum. Push stack_gosub_frame (txtpos, current_line).
 * current_line = findline(), goto execline. */
gosub:
  IGNORE_AND_REJECT_CMD_TICK();
  CLEAR_EXPR_ERR();
  linenum = expression();
  if(!expression_error && (*txtpos == NL || *txtpos == ':') && lineExists(linenum))
  {
    struct stack_gosub_frame *f;
    if(sp + sizeof(struct stack_gosub_frame) < stack_limit)
      goto qstack;

    sp -= sizeof(struct stack_gosub_frame);
    f = (struct stack_gosub_frame *)sp;
    f->frame_type = STACK_GOSUB_FLAG;
    f->txtpos = txtpos;
    f->current_line = current_line;
    current_line = findline();
    goto execline;
  }
  goto qbadline;

/* NEXT var: In gosub_return loop, find matching STACK_FOR_FLAG. If var matches,
 * increment var by step; if in range, loop; else pop frame and run_next_statement. */
next:
  IGNORE_AND_REJECT_CMD_TICK();
  if(*txtpos < 'A' || *txtpos > 'Z')
    GOTO_DIV0_OR_EXPRESSION_ERROR();
  txtpos++;
  ignore_blanks();
  if(*txtpos != ':' && *txtpos != NL)
    GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

/* gosub_return / next: Walk stack from sp upward. GOSUB frame: return current_line,
 * txtpos. FOR frame: if NEXT var matches, increment var; if still in range,
 * loop; else pop and run_next_statement. Stack order: most recent at lowest addr. */
gosub_return:
  tempsp = sp;
  while(tempsp < interp_for_stack + STACK_SIZE - 1)
  {
    switch(tempsp[0])
    {
    case STACK_GOSUB_FLAG:
      if(table_index == KW_RETURN)
      {
        struct stack_gosub_frame *f = (struct stack_gosub_frame *)tempsp;
        current_line	= f->current_line;
        txtpos			= f->txtpos;
        sp += sizeof(struct stack_gosub_frame);
        goto run_next_statement;
      }
      tempsp += sizeof(struct stack_gosub_frame);
      break;
    case STACK_FOR_FLAG:
      if(table_index == KW_NEXT)
      {
        struct stack_for_frame *f = (struct stack_for_frame *)tempsp;
        if(txtpos[-1] == f->for_var)
        {
          short int *varaddr = ((short int *)variables_begin) + txtpos[-1] - 'A'; 
          *varaddr = *varaddr + f->step;
          if((f->step > 0 && *varaddr <= f->terminal) || (f->step < 0 && *varaddr >= f->terminal))
          {
            txtpos = f->txtpos;
            current_line = f->current_line;
            goto run_next_statement;
          }
          sp = tempsp + sizeof(struct stack_for_frame);
          goto run_next_statement;
        }
      }
      tempsp += sizeof(struct stack_for_frame);
      break;
    default:
      goto warmstart;
    }
  }
  if(table_index == KW_RETURN)
    goto qreturn;
  goto qlooperr;

/* Assignment: var (A..Z) = expression(). Store in variables_begin. */
assignment:
  {
    short int value;
    short int *var;

    IGNORE_AND_REJECT_CMD_TICK();
    if(*txtpos < 'A' || *txtpos > 'Z')
      GOTO_DIV0_OR_EXPRESSION_ERROR();
    var = (short int *)variables_begin + *txtpos - 'A';
    txtpos++;

    ignore_blanks();

    if (*txtpos != '=')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    txtpos++;
    ignore_blanks();
    CLEAR_EXPR_ERR();
    value = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    *var = value;
  }
  goto run_next_statement;

/*******************************************************************************
 * READ – pull next integers from DATA stream
 * ----------------------------------------------------------------------------
 * One or more variables A..Z, comma-separated. OUT OF DATA if stream exhausted.
 * Invariants: data_cur_line = program record of current DATA line, or NULL before
 *   first item / after true exhaustion. data_cur_pos = txtpos within that line’s
 *   text (after DATA keyword), or NULL when the line is chosen but not opened yet
 *   (must run open block below, never assign txtpos = data_cur_pos while NULL).
 ******************************************************************************/
readstmt:
  IGNORE_AND_REJECT_CMD_TICK();
  CLEAR_EXPR_ERR();
  for(;;)
  {
    ignore_blanks();
    if(*txtpos < 'A' || *txtpos > 'Z')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    {
      char varletter;
      short int *varptr;
      short int val;

      varletter = *txtpos++;
      varptr = (short int *)variables_begin + (varletter - 'A');
      tmptxtpos = txtpos;

rd_read_again:
      /* Open stream: discover line if needed, then skip DATA keyword. */
      if(data_cur_line == NULL || data_cur_pos == NULL)
      {
        if(data_cur_line == NULL)
        {
          unsigned char *search_from =
              (data_read_start_line != NULL) ? data_read_start_line : program_start;
          data_cur_line = find_data_line_from(search_from);
          if(data_cur_line == NULL)
          {
            txtpos = tmptxtpos;
            goto qoutofdata;
          }
        }
        txtpos = data_cur_line + sizeof(LINENUM) + 1;
        ignore_blanks();
        scantable(keywords);
        if(table_index != KW_DATA)
        {
          txtpos = tmptxtpos;
          goto qsyntax;
        }
        data_cur_pos = txtpos;
      }

      txtpos = data_cur_pos;
      ignore_blanks();
      if(*txtpos == NL)
      {
        unsigned char *next_data =
            find_data_line_from(next_program_line(data_cur_line));
        if(next_data == NULL)
        {
          txtpos = tmptxtpos;
          goto qoutofdata;
        }
        data_cur_line = next_data;
        data_cur_pos = NULL;
        goto rd_read_again;
      }

      if(!data_parse_number(&val))
      {
        txtpos = tmptxtpos;
        goto qsyntax;
      }
      data_cur_pos = txtpos;
      txtpos = tmptxtpos;
      *varptr = val;
      ignore_blanks();
      if(*txtpos == ',')
      {
        txtpos++;
        ignore_blanks();
        continue;
      }
      if(*txtpos == NL || *txtpos == ':')
        goto run_next_statement;
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    }
  }

/*******************************************************************************
 * RESTORE – reset DATA read pointer
 * ----------------------------------------------------------------------------
 * No operand: scan from program start. With expr: first DATA on or after that
 * line number (findline).
 ******************************************************************************/
restorestmt:
  IGNORE_AND_REJECT_CMD_TICK();
  CLEAR_EXPR_ERR();
  if(*txtpos == NL || *txtpos == ':')
  {
    data_read_start_line = NULL;
    data_cur_line = NULL;
    data_cur_pos = NULL;
    goto run_next_statement;
  }
  {
    short int n;
    n = expression();
    if(expression_error)
      GOTO_DIV0_OR_EXPRESSION_ERROR();
    if(*txtpos != NL && *txtpos != ':')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    linenum = (LINENUM)n;
    data_read_start_line = findline();
    data_cur_line = NULL;
    data_cur_pos = NULL;
  }
  goto run_next_statement;

/*******************************************************************************
 * LIST – whole program, one line, or line range
 * ----------------------------------------------------------------------------
 * LIST           - entire program (from program_start).
 * LIST 100       - single line 100 only (must exist).
 * LIST ,100      - first line through 100 inclusive.
 * LIST 100,      - line 100 through end of program.
 * LIST 100,200   - lines 100..200 inclusive (lo must exist; lo <= hi).
 * LIST ,         - invalid (LINE NUMBER ERROR).
 ******************************************************************************/
list:
  {
    unsigned char saw_comma;
    LINENUM lo, hi;

    lo = (LINENUM)testnum();
    saw_comma = 0;
    hi = 0;
    if(*txtpos == ',')
    {
      txtpos++;
      saw_comma = 1;
      hi = (LINENUM)testnum();
    }

    if(txtpos[0] != NL)
      goto qbadline;

    if(!saw_comma)
    {
      if(lo == 0)
      {
        list_line = program_start;
        while(list_line != program_end)
          printline();
      }
      else
      {
        if(!lineExists(lo))
          goto qbadline;
        linenum = lo;
        list_line = findline();
        printline();
      }
    }
    else
    {
      if(lo == 0 && hi == 0)
        goto qbadline;

      if(lo == 0)
      {
        list_line = program_start;
        while(list_line != program_end)
        {
          LINENUM cur = *((LINENUM *)list_line);
          if(cur > hi)
            break;
          printline();
        }
      }
      else if(hi == 0)
      {
        if(!lineExists(lo))
          goto qbadline;
        linenum = lo;
        list_line = findline();
        while(list_line != program_end)
          printline();
      }
      else
      {
        if(lo > hi)
          goto qbadline;
        if(!lineExists(lo))
          goto qbadline;
        linenum = lo;
        list_line = findline();
        while(list_line != program_end)
        {
          LINENUM cur = *((LINENUM *)list_line);
          if(cur > hi)
            break;
          printline();
        }
      }
    }
  }
  errorLedOff();
  goto warmstart;

/* PRINT - Items separated by ',' (tab) or ';' (no space). '"string"' or expr.
 * ',' → skip, next item. ';' at end → no newline. NL or ':' → line_terminator. */
print:
  if(*txtpos == ':' )
  {
    line_terminator();
    txtpos++;
    goto run_next_statement;
  }
  if(*txtpos == NL)
  {
    goto execnextline;
  }

  while(1)
  {
    IGNORE_AND_REJECT_CMD_TICK();
    if(print_quoted_string())
    {
      ;
    }
    else if(*txtpos == '"' || *txtpos == '\'')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    else
    {
      short int e;
      CLEAR_EXPR_ERR();
      e = expression();
      if(expression_error)
        GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
      printnum(e);
    }

    if(*txtpos == ',')
      txtpos++;	// Skip the comma and move onto the next
    else if(txtpos[0] == ';' && (txtpos[1] == NL || txtpos[1] == ':'))
    {
      txtpos++; // This has to be the end of the print - no newline
      break;
    }
    else if(*txtpos == NL || *txtpos == ':')
    {
      line_terminator();	// The end of the print statement
      break;
    }
    else
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();	
  }
  goto run_next_statement;

/* MEM - Clear screen; SRAM, BASIC, EEPROM bars (showMemoryScreen), then RUN path. */
mem:
  outchar(GPU_CLEAR_SCREEN);
  showMemoryScreen();
  goto run_next_statement;

/*******************************************************************************
 * AWRITE / DWRITE – pin and value expressions
 * ----------------------------------------------------------------------------
 * pin, comma, then HIGH/HI/LOW/LO keywords or numeric expression. analogWrite /
 * digitalWrite. highlow_tab resolves keyword values.
 ******************************************************************************/
awrite:
dwrite:
  {
    short int pinNo;
    short int value;
    unsigned char *txtposBak;

    IGNORE_AND_REJECT_CMD_TICK();
    CLEAR_EXPR_ERR();
    pinNo = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    ignore_blanks();
    if (*txtpos != ',')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    txtpos++;
    ignore_blanks();


    txtposBak = txtpos; 
    scantable(highlow_tab);
    if(table_index != HIGHLOW_UNKNOWN)
    {
      if( table_index <= HIGHLOW_HIGH ) {
        value = 1;
      } 
      else {
        value = 0;
      }
    } 
    else {

      CLEAR_EXPR_ERR();
      value = expression();
      if(expression_error)
        GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    }
    pinMode( pinNo, OUTPUT );
    if( isDigital ) {
      digitalWrite( pinNo, value );
    } 
    else {
      analogWrite( pinNo, value );
    }
  }
  goto run_next_statement;

rseed:
  {
    short int value;

    IGNORE_AND_REJECT_CMD_TICK();
    CLEAR_EXPR_ERR();
    value = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    randomSeed( value );
    goto run_next_statement;
  }

tonestop:
  noTone( kPiezoPin );
  goto run_next_statement;

tonegen:
  {
    short int freq;
    short int duration;

    IGNORE_AND_REJECT_CMD_TICK();
    CLEAR_EXPR_ERR();
    freq = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    ignore_blanks();
    if (*txtpos != ',')
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();
    txtpos++;
    ignore_blanks();


    CLEAR_EXPR_ERR();
    duration = expression();
    if(expression_error)
      GOTO_DIV0_EXPRESSION_OR_SYNTAX_ERROR();

    if( freq == 0 || duration == 0 )
      goto tonestop;

    tone( kPiezoPin, freq, duration );
    if( alsoWait ) {
      delay( duration );
      alsoWait = false;
    }
    goto run_next_statement;
  }
}

/*******************************************************************************
 * LINE TERMINATOR & SETUP – CR/LF, Serial, keyboard, autorun
 * ----------------------------------------------------------------------------
 * line_terminator: Send CR only. GPU advances row when x!=0; ignores LF. CR-only is correct.
 * setup: Serial.begin(kConsoleBaud). while(!Serial) for Leonardo. keyboard.begin.
 * EAUTORUN - If EEPROM[0] is '0'..'9', treat as program start; eload and run.
 ******************************************************************************/
static void line_terminator(void)
{
  outchar(CR);
}

/* setup(): Arduino entry point. Serial at kConsoleBaud. PS/2: kPs2DataPin / kPs2IrqPin.
 * ENABLE_EAUTORUN - If EEPROM[0] is '0'..'9', load from EEPROM and runAfterLoad. */
void setup()
{
  Serial.begin(kConsoleBaud);
  while( !Serial );  /* Leonardo - wait for Serial. Nano - instant. */

  keyboard.begin(kPs2DataPin, kPs2IrqPin);

  /* Default random() repeats every boot unless seeded; RND() benefits from variety. */
  {
    unsigned long seed = (unsigned long)micros();
    unsigned char k;
    for(k = 0; k < 12; k++)
      seed ^= (unsigned long)analogRead(A0) << ((k & 7U) * 2U);
    randomSeed(seed);
  }

  program_start = program;
  program_end = program_start;
  data_reset_pointers();
  variables_begin = (unsigned char *)basic_variable;
  stack_limit = interp_for_stack;
  sp = interp_for_stack + STACK_SIZE;

  pinMode(kErrorLedPin, OUTPUT);
  digitalWrite(kErrorLedPin, LOW);

  tone(kPiezoPin, 523, 60);
  delay(60);
  tone(kPiezoPin, 659, 60);
  delay(60);
  noTone(kPiezoPin);

#ifdef ENABLE_EAUTORUN
  int val = EEPROM.read(0);
  if( val >= '0' && val <= '9' ) {
    program_end = program_start;
    inStream = kStreamEEProm;
    eepos = 0;
    inhibitOutput = true;
    runAfterLoad = true;
    delay(EEPROM_LOAD_START_DELAY_MS);
  }
#endif /* ENABLE_EAUTORUN */

}


/*******************************************************************************
 * I/O – breakcheck (ESC), inchar (keyboard/Serial), outchar (Serial/GPU)
 * ----------------------------------------------------------------------------
 * breakcheck:
 *   During RUN only: if next keyboard/serial byte is ESC (27), consume it and
 *   return true → user_break_handler (start of each statement, before parsing).
 * inchar:
 *   EEPROM stream (NUL ends → serial + optional triggerRun) or blocking
 *   keyboard-then-USB-Serial (for pasting from a PC).
 * outchar:
 *   Honors inhibitOutput; else Serial.write to GPU or EEPROM during ESAVE.
 ******************************************************************************/
static unsigned char breakcheck(void)
{
  if(current_line == NULL || current_line == program_end)
    return 0;
  if(keyboard.available())
    return keyboard.read() == 27;
  if(Serial.available())
    return Serial.read() == 27;
  return 0;
}

/*******************************************************************************
 * inchar – next input byte (blocking on serial path)
 * ----------------------------------------------------------------------------
 * EEPROM path: NUL ends stream → back to serial, optional triggerRun, return CR.
 * Serial path: keyboard first, then host Serial (host backspace bytes discarded).
 ******************************************************************************/
static int inchar(void)
{
  if (inStream == kStreamEEProm)
  {
    int v = EEPROM.read(eepos++);
    if (v == '\0')
    {
      inStream = kStreamSerial;
      inhibitOutput = false;
      if (runAfterLoad)
      {
        runAfterLoad = false;
        triggerRun = true;
      }
      return CR; /* finish current input line so prompt logic completes cleanly */
    }
    delay(EEPROM_LOAD_CHAR_DELAY_MS);
    return v;
  }

  for (;;)
  {
    if (keyboard.available())
      return (int)(unsigned char)keyboard.read();
    if (Serial.available())
    {
      int c = Serial.read();
      /* Discard backspace from Serial (e.g. USB driver after host closes port).
       * Keyboard backspace still works (we read keyboard first above). */
      if (c != 0x08 && c != 127)
        return c;
    }
  }
}

/*******************************************************************************
 * outchar – one byte to GPU serial or EEPROM (ESAVE stream)
 ******************************************************************************/
static void outchar(unsigned char c)
{
  if( inhibitOutput ) return;

  if( outStream == kStreamEEProm ) {
    EEPROM.write( eepos++, c );
  }
  else
    Serial.write(c);
}