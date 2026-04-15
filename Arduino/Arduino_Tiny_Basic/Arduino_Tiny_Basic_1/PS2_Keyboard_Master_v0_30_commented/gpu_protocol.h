#ifndef GPU_PROTOCOL_H
#define GPU_PROTOCOL_H

/*******************************************************************************
 * CPU → VGA GPU serial protocol (must match VGA_Graphics_Slave_v1_5.ino)
 * ----------------------------------------------------------------------------
 * CR (13): If cursor x != 0, newline (x=0, y+=6). GPU does not print '>' (CPU does).
 * LF (10): Ignored so CRLF does not double-advance.
 * GPU_COLOR_TICK (96 '`'): Color step only; slave does not advance cursor.
 *   Cycle: green→yellow→red→green. Used in PRINT strings, getln prompt, LIST, boot art.
 * GPU_BLOCK (126 '~'): Solid block in current color (borders, MEM bars).
 * CTRLH / 127: Backspace — erase one cell, GPU draws black at new position.
 * GPU_CLEAR_SCREEN (12, Ctrl+L): Clear framebuffer; cursor and color NOT reset.
 * GPU_COLOR_RESET (14, SI): Reset print pen to default green.
 *   PRINT sends SI before each quoted string body so a leading tick counts from green.
 *   Errors: red (SI + two ticks); OK and ">" prompt: green (SI).
 * Layout: ~23–24 chars per row safe; GPU wraps when x > 120.
 ******************************************************************************/

/* SI — reset VGA print color to default green */
#define GPU_COLOR_RESET 0x0E

/* Backtick — advance color without moving cursor */
#define GPU_COLOR_TICK '`'

/* Tilde — filled cell for borders / bar graphs */
#define GPU_BLOCK '~'

/* Ctrl+L — clear screen (see slave handler for cursor/color behavior) */
#define GPU_CLEAR_SCREEN 12

#endif
