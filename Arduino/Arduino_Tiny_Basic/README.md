# Tiny BASIC Arduino Computer

## Overview

This repository contains a Tiny BASIC interpreter configured to run on **two Arduino boards**.  

---

## Memory Constraints

Because the Arduino Nano (ATmega328P) has **2 KB of SRAM**, user programs and variables must fit within a few hundred bytes (the rest is consumed by the interpreter). Only **26 integer variables (A–Z)** are typically available, each storing a 16-bit signed value (–32768 to 32767). EEPROM usage (1 KB) is supported for saving and loading one Tiny BASIC program at a time.

**Key Implications**:
- Large or complex programs are **not feasible**.  
- Only a limited number of GOSUB/RETURN or FOR/NEXT nestings are possible.  
- Saving to EEPROM is limited by its capacity (1 KB).

---

## Necessary Hardware and Features

1. **Master Arduino**  
   - Executes (runs) the Tiny BASIC interpreter.  
   - Handles PS/2 keyboard signals.  
   - Manages program logic and EEPROM-based storage.

2. **Slave Arduino**  
   - Receives serial or parallel data from the Master.  
   - Produces VGA signals for a monitor.  

3. **PS/2 Keyboard**  
   - Provides user input directly to the Master Arduino.  

4. **Speaker (Optional)**  
   - Emits audible (sound-based) signals or tones when instructed by Tiny BASIC commands.  

5. **EEPROM (Built in)**  
   - Stores programs.  
   - No SD card or file system is supported.

---

## Basic Usage

1. **Load the Code**  
   - Upload `PS2_Keyboard_Master.ino` to the Master Arduino.  
   - Upload `VGA_Graphics_Slave.ino` to the Slave Arduino.  

2. **Wiring**  
   - Connect the Master Arduino’s serial (or parallel) pins to the Slave Arduino according to the schematic.  
   - Attach the PS/2 keyboard to the Master’s designated pins (Data and Clock).  
   - Link the Slave Arduino’s VGA pins to a VGA connector.  

3. **Power and Test**  
   - Provide 5V (or 3.3V, depending on board) to both Arduinos.  
   - Turn on the monitor; you should see a Tiny BASIC prompt.  
   - Type commands via the PS/2 keyboard.

---

## Command Reference

Below is a **concise** list of typical Tiny BASIC commands supported in this project.

1. **`PRINT`**  
   - Outputs text or variable values.  
   - Example:  
     ```basic
     PRINT "HELLO"
     PRINT X
     ```

2. **`INPUT`**  
   - Requests user input from the keyboard and stores it in a variable.  
   - Example:  
     ```basic
     INPUT A
     ```

3. **`LET`**  
   - Assigns a value to a variable.  
   - Example:  
     ```basic
     LET X = 10
     ```

4. **`IF ... THEN ...`**  
   - Performs a conditional jump or statement.  
   - Example:  
     ```basic
     IF X = 10 GOTO 100
     ```

5. **`GOTO`**  
   - Transfers program control to a specified line number.  
   - Example:  
     ```basic
     GOTO 100
     ```

6. **`GOSUB ... RETURN`**  
   - Calls a subroutine at a specified line number and returns control afterward.  
   - Example:  
     ```basic
     100 GOSUB 500
     110 PRINT "DONE"
     120 END

     500 PRINT "SUBROUTINE"
     510 RETURN
     ```

7. **`FOR ... TO ... [STEP ...] ... NEXT ...`**  
   - Implements a looping structure.  
   - Example:  
     ```basic
     FOR I = 1 TO 5
       PRINT I
     NEXT I
     ```

8. **`REM`**  
   - Inserts a comment line.  
   - Example:  
     ```basic
     REM THIS IS A COMMENT
     ```

9. **`LIST`**  
   - Displays the current program in memory.  
   - Example:  
     ```basic
     LIST
     ```

10. **`RUN`**  
    - Executes the program from the beginning.  
    - Example:  
      ```basic
      RUN
      ```

11. **`NEW`**  
    - Clears the program from memory.  
    - Example:  
      ```basic
      NEW
      ```

12. **`END`**  
    - Terminates program execution.  
    - Example:  
      ```basic
      END
      ```

13. **`CLS`** *(If supported)*  
    - Clears the VGA screen.  
    - Example:  
      ```basic
      CLS
      ```

14. **`POKE` / `PEEK`** *(If memory manipulation is enabled)*  
    - `POKE` writes a value to a memory address.  
    - `PEEK` reads a value from a memory address.  

15. **EEPROM Commands**
    - **`ESAVE`** – Saves the current program to EEPROM.  
    - **`ELOAD`** – Loads the previously saved program from EEPROM.  

16. **Custom Sound or Graphics Commands** *(If your code provides them)*  
    - Example:  
      ```basic
      SOUND 440, 10
      PLOT X, Y
      ```
17. **Write / Read to Pins**
    - **`DWRITE` / `DREAD` / `AWRITE` / `AREAD`**
    - Controls pins from the command prompt
    - Example:
      ```basic
      DWRITE 10, HIGH
      DWRITE 10, LOW
      ```
18. **Change Text Color**
    - **`SHIFT + &`**
