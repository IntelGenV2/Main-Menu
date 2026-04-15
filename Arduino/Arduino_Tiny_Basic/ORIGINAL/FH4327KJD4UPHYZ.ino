/******************************************************************* 
*                Arduino TinyBasic VGA PC                          * 
*                                                                  *
*  Version 1 - February the 4th, 2018, Written by Roberto Melzi    * 
*                                                                  *
*  Arduino TinyBasic VGA PC is a simpe, 8-bit retro-PC, composed   * 
*  by two Arduino board. One runs TinyBasic and the PS2 library,   * 
*  while the other runs a code, based on the VGAx library, to      * 
*  generate the output signal for a VGA monitor.                   *
*                                                                  *
*  Both TinyBasic and VGAx requires Arduino IDE version 1.6.4      * 
*  VGAx library does not work for newer or elder software          *
*  versions.                                                       * 
*                                                                  *
*  VGAx Library written By Sandro Maffiodo aka Smaffer.            * 
*  https://github.com/smaffer/vgax                                 * 
*  See also the Arduino forum:                                     * 
*  http://forum.arduino.cc/index.php?topic=328631.0                * 
*  and on Instructables:                                           *
*  http://www.instructables.com/member/Rob%20Cai/instructables/    *
*                                                                  * 
*******************************************************************/ 

#include <VGAX.h>
//#include <math.h>
#define FNT_NANOFONT_HEIGHT 6
#define FNT_NANOFONT_SYMBOLS_COUNT 95
//#include <VGAXUtils.h>

VGAX vga;
//VGAXUtils vgaU;

//data size=570 bytes
const unsigned char fnt_nanofont_data[FNT_NANOFONT_SYMBOLS_COUNT][1+FNT_NANOFONT_HEIGHT] PROGMEM={
{ 3, 32, 32, 32, 0, 32, 0, }, //glyph '!' code=0
{ 4, 80, 80, 0, 0, 0, 0, }, //glyph '"' code=1
{ 5, 80, 248, 80, 248, 80, 0, },  //glyph '#' code=2-
{ 5, 120, 160, 112, 40, 240, 0, },  //glyph '$' code=3
{ 5, 136, 16, 32, 64, 136, 0, },  //glyph '%' code=4
{ 5, 96, 144, 104, 144, 104, 0, },  //glyph '&' code=5
{ 2, 32, 64, 0, 0, 0, 0, },  //glyph ''' code=6
{ 2, 64, 128, 128, 128, 64, 0, }, //glyph '(' code=7
{ 2, 128, 64, 64, 64, 128, 0, },  //glyph ')' code=8
{ 4, 0, 80, 32, 80, 0, 0, },  //glyph '*' code=9
{ 4, 0, 32, 112, 32, 0, 0, }, //glyph '+' code=10
{ 2, 0, 0, 0, 0, 32, 64, },  //glyph ',' code=11
{ 4, 0, 0, 112, 0, 0, 0, }, //glyph '-' code=12
{ 2, 0, 0, 0, 0, 64, 0, }, //glyph '.' code=13
{ 5, 8, 16, 32, 64, 128, 0, },  //glyph '/' code=14
//{ 4, 96, 144, 144, 144, 96, 0, }, //glyph '0' code=15
{ 4, 96, 176, 144, 208, 96, 0, }, //glyph '0' code=15
{ 4, 32, 96, 32, 32, 112, 0, },  //glyph '1' code=16
{ 4, 224, 16, 96, 128, 240, 0, }, //glyph '2' code=17
{ 4, 224, 16, 96, 16, 224, 0, },  //glyph '3' code=18
{ 4, 144, 144, 240, 16, 16, 0, }, //glyph '4' code=19
{ 4, 240, 128, 224, 16, 224, 0, },  //glyph '5' code=20
{ 4, 96, 128, 224, 144, 96, 0, }, //glyph '6' code=21
{ 4, 240, 16, 32, 64, 64, 0, }, //glyph '7' code=22
{ 4, 96, 144, 96, 144, 96, 0, },  //glyph '8' code=23
{ 4, 96, 144, 112, 16, 96, 0, },  //glyph '9' code=24
{ 3, 0, 32, 0, 32, 0, 0, }, //glyph ':' code=25
{ 2, 0, 32, 0, 32, 64, 0, },  //glyph ';' code=26 
{ 4, 16, 32, 64, 32, 16, 0, }, //glyph '<' code=27
{ 4, 0, 112, 0, 112, 0, 0, }, //glyph '=' code=28
{ 4, 64, 32, 16, 32, 64, 0, },  //glyph '>' code=29
{ 4, 224, 16, 96, 0, 64, 0, },  //glyph '?' code=30
{ 4, 96, 144, 176, 128, 112, 0, },  //glyph '@' code=31
{ 4, 96, 144, 240, 144, 144, 0, },  //glyph 'A' code=32
{ 4, 224, 144, 224, 144, 224, 0, }, //glyph 'B' code=33
{ 4, 112, 128, 128, 128, 112, 0, }, //glyph 'C' code=34
{ 4, 224, 144, 144, 144, 224, 0, }, //glyph 'D' code=35
{ 4, 240, 128, 224, 128, 240, 0, }, //glyph 'E' code=36
{ 4, 240, 128, 224, 128, 128, 0, }, //glyph 'F' code=37
{ 4, 112, 128, 176, 144, 112, 0, }, //glyph 'G' code=38
{ 4, 144, 144, 240, 144, 144, 0, }, //glyph 'H' code=39
{ 4, 112, 32, 32, 32, 112, 0, },  //glyph 'I' code=40
{ 4, 240, 16, 16, 144, 96, 0, },  //glyph 'J' code=41
{ 4, 144, 160, 192, 160, 144, 0, }, //glyph 'K' code=42
{ 4, 128, 128, 128, 128, 240, 0, }, //glyph 'L' code=43
{ 5, 136, 216, 168, 136, 136, 0, }, //glyph 'M' code=44
{ 4, 144, 208, 176, 144, 144, 0, }, //glyph 'N' code=45
{ 4, 96, 144, 144, 144, 96, 0, }, //glyph 'O' code=46
{ 4, 224, 144, 224, 128, 128, 0, }, //glyph 'P' code=47
{ 4, 96, 144, 144, 144, 96, 16, },  //glyph 'Q' code=48
{ 4, 224, 144, 224, 160, 144, 0, }, //glyph 'R' code=49
{ 4, 112, 128, 96, 16, 224, 0, }, //glyph 'S' code=50
{ 4, 112, 32, 32, 32, 32, 0, }, //glyph 'T' code=51
{ 4, 144, 144, 144, 144, 96, 0, },  //glyph 'U' code=52
{ 4, 80, 80, 80, 80, 32, 0, },  //glyph 'V' code=53
{ 5, 136, 168, 168, 168, 80, 0, },  //glyph 'W' code=54
{ 4, 144, 144, 96, 144, 144, 0, },  //glyph 'X' code=55
{ 4, 80, 80, 32, 32, 32, 0, },  //glyph 'Y' code=56
{ 4, 240, 16, 96, 128, 240, 0, }, //glyph 'Z' code=57
{ 3, 96, 64, 64, 64, 96, 0, }, //glyph '[' code=58
{ 5, 128, 64, 32, 16, 8, 0, },  //glyph '\' code=59
{ 3, 96, 32, 32, 32, 96, 0, },  //glyph ']' code=60
{ 5, 32, 80, 136, 0, 0, 0, }, //glyph '^' code=61
{ 4, 0, 0, 0, 0, 240, 0, }, //glyph '_' code=62
//{ 2, 128, 64, 0, 0, 0, 0, },  //glyph '`' code=63
{ 3, 64, 32, 0, 0, 0, 0, },  //glyph '`' code=63
{ 4, 0, 112, 16, 112, 112, 0, },  //glyph 'a' code=64
{ 4, 64, 112, 80, 80, 112, 0, }, //glyph 'b' code=65
{ 4, 0, 112, 64, 64, 112, 0, }, //glyph 'c' code=66
{ 4, 16, 112, 80, 80, 112, 0, },  //glyph 'd' code=67
{ 3, 0, 112, 112, 64, 112, 0, }, //glyph 'e' code=68
{ 3, 32, 64, 96, 64, 64, 0, },  //glyph 'f' code=69
{ 4, 0, 112, 80, 112, 16, 112, },  //glyph 'g' code=70
{ 3, 64, 114, 80, 80, 80, 0, }, //glyph 'h' code=71
{ 2, 32, 0, 32, 32, 32, 0, }, //glyph 'i' code=72
{ 3, 0, 96, 32, 32, 32, 64, },  //glyph 'j' code=73
{ 4, 64, 80, 96, 80, 80, 0, }, //glyph 'k' code=74
{ 3, 32, 32, 32, 32, 32, 0, }, //glyph 'l' code=75
{ 5, 0, 248, 168, 168, 168, 0, }, //glyph 'm' code=76
{ 3, 0, 112, 80, 80, 80, 0, }, //glyph 'n' code=77
{ 4, 0, 112, 80, 80, 112, 0, }, //glyph 'o' code=78
{ 4, 0, 112, 80, 80, 112, 64, }, //glyph 'p' code=79
{ 4, 0, 112, 80, 80, 112, 16, },  //glyph 'q' code=80
{ 4, 0, 112, 64, 64, 64, 0, }, //glyph 'r' code=81
{ 3, 0, 96, 64, 32, 96, 0, },  //glyph 's' code=82
{ 4, 32, 112, 32, 32, 32, 0, }, //glyph 't' code=83
{ 4, 0, 80, 80, 80, 112, 0, }, //glyph 'u' code=84
{ 4, 0, 80, 80, 80, 32, 0, },  //glyph 'v' code=85
{ 5, 0, 168, 168, 168, 80, 0, },  //glyph 'w' code=86
{ 3, 0, 80, 32, 80, 80, 0, },  //glyph 'x' code=87
{ 4, 0, 80, 80, 112, 16, 112, },  //glyph 'y' code=88
{ 3, 0, 96, 32, 64, 96, 0, },  //glyph 'z' code=89
{ 4, 48, 32, 96, 32, 48, 0, }, //glyph '{' code=90
{ 3, 32, 32, 32, 32, 32, 0, }, //glyph '|' code=91
{ 4, 96, 32, 48, 32, 96, 0, },  //glyph '}' code=92
{ 5, 248, 248, 248, 248, 248, 248, },  //glyph '~' code=93 - full character used for deleting 
{ 4, 48, 64, 224, 64, 240, 0, },  //glyph 'Â£' code=94 
};

static const char str33[] PROGMEM="!"; 
static const char str34[] PROGMEM="\""; 
static const char str35[] PROGMEM="#";
static const char str36[] PROGMEM="$";
static const char str37[] PROGMEM="%";
static const char str38[] PROGMEM="&";
static const char str39[] PROGMEM="'";
static const char str40[] PROGMEM="(";
static const char str41[] PROGMEM=")";
static const char str42[] PROGMEM="*";
static const char str43[] PROGMEM="+";
static const char str44[] PROGMEM=",";
static const char str45[] PROGMEM="-";
static const char str46[] PROGMEM=".";
static const char str47[] PROGMEM="/";
static const char str48[] PROGMEM="0";
static const char str49[] PROGMEM="1";
static const char str50[] PROGMEM="2";
static const char str51[] PROGMEM="3";
static const char str52[] PROGMEM="4";
static const char str53[] PROGMEM="5";
static const char str54[] PROGMEM="6";
static const char str55[] PROGMEM="7";
static const char str56[] PROGMEM="8";
static const char str57[] PROGMEM="9";
static const char str58[] PROGMEM=":";
static const char str59[] PROGMEM=";";
static const char str60[] PROGMEM="<";
static const char str61[] PROGMEM="=";
static const char str62[] PROGMEM=">";
static const char str63[] PROGMEM="?";
static const char str64[] PROGMEM="@"; 
static const char str65[] PROGMEM="A"; 
static const char str66[] PROGMEM="B"; 
static const char str67[] PROGMEM="C"; 
static const char str68[] PROGMEM="D"; 
static const char str69[] PROGMEM="E";
static const char str70[] PROGMEM="F";
static const char str71[] PROGMEM="G";
static const char str72[] PROGMEM="H";
static const char str73[] PROGMEM="I";
static const char str74[] PROGMEM="J";
static const char str75[] PROGMEM="K";
static const char str76[] PROGMEM="L";
static const char str77[] PROGMEM="M";
static const char str78[] PROGMEM="N";
static const char str79[] PROGMEM="O";
static const char str80[] PROGMEM="P";
static const char str81[] PROGMEM="Q";
static const char str82[] PROGMEM="R";
static const char str83[] PROGMEM="S";
static const char str84[] PROGMEM="T";
static const char str85[] PROGMEM="U";
static const char str86[] PROGMEM="V";
static const char str87[] PROGMEM="W";
static const char str88[] PROGMEM="X";
static const char str89[] PROGMEM="Y";
static const char str90[] PROGMEM="Z";
static const char str91[] PROGMEM="[";
static const char str92[] PROGMEM="\\"; 
static const char str93[] PROGMEM="]";
static const char str94[] PROGMEM="^";
static const char str95[] PROGMEM="_";
static const char str96[] PROGMEM="`";
static const char str97[] PROGMEM="a";
static const char str98[] PROGMEM="b";
static const char str99[] PROGMEM="c";
static const char str100[] PROGMEM="d";
static const char str101[] PROGMEM="e";
static const char str102[] PROGMEM="f"; 
static const char str103[] PROGMEM="g";
static const char str104[] PROGMEM="h";
static const char str105[] PROGMEM="i";
static const char str106[] PROGMEM="j";
static const char str107[] PROGMEM="k";
static const char str108[] PROGMEM="l";
static const char str109[] PROGMEM="m";
static const char str110[] PROGMEM="n";
static const char str111[] PROGMEM="o";
static const char str112[] PROGMEM="p"; 
static const char str113[] PROGMEM="q";
static const char str114[] PROGMEM="r";
static const char str115[] PROGMEM="s";
static const char str116[] PROGMEM="t";
static const char str117[] PROGMEM="u";
static const char str118[] PROGMEM="v";
static const char str119[] PROGMEM="w";
static const char str120[] PROGMEM="x";
static const char str121[] PROGMEM="y";
static const char str122[] PROGMEM="z"; 
static const char str123[] PROGMEM="{";
static const char str124[] PROGMEM="|";
static const char str125[] PROGMEM="}";
static const char str126[] PROGMEM="~";
//static const char str127[] PROGMEM="ì";

void setup() {
  vga.begin();
  Serial.begin(4800); 
}

byte x = 0; 
byte y = 0; 
byte myNumber;
byte colorMain = 2; 
unsigned int counter; 

void loop() {
   counter++; 
   if (counter == 20000){
      //counter = 0; 
      vgaPrintAscii(byte(95), x, y, colorMain);
   }
   if (counter == 40000){
      counter = 0; 
      vgaPrintAscii(byte(95), x, y, 0);
   }

   if (Serial.available() > 0) {
      myNumber = Serial.read();
      vgaPrintAscii(byte(95), x, y, 0);
      switch (myNumber){
         
         case 13: // Enter
            x = 0;
            y += 6; 
         break;
        
         case 27: // Esc
            vga.clear(0); 
            x = 0; 
            y = 0;
         break;
         
         case 32: // Space 
            x += 5; 
         break;
         
         case 38: // color change using the caracther "&"
            colorMain += 1; 
            if (colorMain == 4) {
               colorMain = 1;
            }
         break; 
         
         case 127: // Del
            if (x == 0) {
               if (y == 0) {
               // do nothing
               }
               else{
                  x = 115;
                  y = y - 6; 
               }
            }
            else
            {
               x += -5; 
            }
            vgaPrintAscii(byte(126), x, y, 0);
         break;
         
         default: 
            vgaPrintAscii(myNumber, x, y, colorMain);
            x += 5; 
         break; 
      }
      //vga.delay(2); 
      //Serial.println(myNumber);  
      if (x > 115){ x = 0; y += 6; }   
      if (y > 54) { vga.clear(0); x = 0; y = 0; }
   }
} //----------------------- end of main loop ---------------------------- 

//---------------------------------------------------------------------------------------------------------------------------

void vgaPrint2(const char* str, byte x, byte y, byte color){
   vga.printSRAM((byte*)fnt_nanofont_data, FNT_NANOFONT_SYMBOLS_COUNT, FNT_NANOFONT_HEIGHT, 3, 1, str, x, y, color);
}

void vgaPrint(const char* str, byte x, byte y, byte color){
   vga.printPROGMEM((byte*)fnt_nanofont_data, FNT_NANOFONT_SYMBOLS_COUNT, FNT_NANOFONT_HEIGHT, 3, 1, str, x, y, color);
}

void vgaPrintAscii(byte number, byte x, byte y, byte color){
  
   if ( number == 33) {vgaPrint(str33, x, y, color);}
   if ( number == 34) {vgaPrint(str34, x, y, color);}
   if ( number == 35) {vgaPrint(str35, x, y, color);}
   if ( number == 36) {vgaPrint(str36, x, y, color);}
   if ( number == 37) {vgaPrint(str37, x, y, color);}
   //if ( number == 38) {vgaPrint(str38, x, y, color);}
   if ( number == 39) {vgaPrint(str39, x, y, color);}
   if ( number == 40) {vgaPrint(str40, x, y, color);}
   if ( number == 41) {vgaPrint(str41, x, y, color);}
   if ( number == 42) {vgaPrint(str42, x, y, color);}
   if ( number == 43) {vgaPrint(str43, x, y, color);}
   if ( number == 44) {vgaPrint(str44, x, y, color);}
   if ( number == 45) {vgaPrint(str45, x, y, color);}
   if ( number == 46) {vgaPrint(str46, x, y, color);}
   if ( number == 47) {vgaPrint(str47, x, y, color);}
   if ( number == 48) {vgaPrint(str48, x, y, color);}
   if ( number == 49) {vgaPrint(str49, x, y, color);}
   if ( number == 50) {vgaPrint(str50, x, y, color);}
   if ( number == 51) {vgaPrint(str51, x, y, color);}
   if ( number == 52) {vgaPrint(str52, x, y, color);}
   if ( number == 53) {vgaPrint(str53, x, y, color);}
   if ( number == 54) {vgaPrint(str54, x, y, color);}
   if ( number == 55) {vgaPrint(str55, x, y, color);}
   if ( number == 56) {vgaPrint(str56, x, y, color);}
   if ( number == 57) {vgaPrint(str57, x, y, color);}
   if ( number == 58) {vgaPrint(str58, x, y, color);}
   if ( number == 59) {vgaPrint(str59, x, y, color);}
   if ( number == 60) {vgaPrint(str60, x, y, color);}
   if ( number == 61) {vgaPrint(str61, x, y, color);}
   if ( number == 62) {vgaPrint(str62, x, y, color);}
   if ( number == 63) {vgaPrint(str63, x, y, color);}
   if ( number == 64) {vgaPrint(str64, x, y, color);}
   if ( number == 65) {vgaPrint(str65, x, y, color);}
   if ( number == 66) {vgaPrint(str66, x, y, color);}
   if ( number == 67) {vgaPrint(str67, x, y, color);}
   if ( number == 68) {vgaPrint(str68, x, y, color);}
   if ( number == 69) {vgaPrint(str69, x, y, color);}
   if ( number == 70) {vgaPrint(str70, x, y, color);}
   if ( number == 71) {vgaPrint(str71, x, y, color);}
   if ( number == 72) {vgaPrint(str72, x, y, color);}
   if ( number == 73) {vgaPrint(str73, x, y, color);}
   if ( number == 74) {vgaPrint(str74, x, y, color);}
   if ( number == 75) {vgaPrint(str75, x, y, color);}
   if ( number == 76) {vgaPrint(str76, x, y, color);}
   if ( number == 77) {vgaPrint(str77, x, y, color);}
   if ( number == 78) {vgaPrint(str78, x, y, color);}
   if ( number == 79) {vgaPrint(str79, x, y, color);}
   if ( number == 80) {vgaPrint(str80, x, y, color);}
   if ( number == 81) {vgaPrint(str81, x, y, color);}
   if ( number == 82) {vgaPrint(str82, x, y, color);}
   if ( number == 83) {vgaPrint(str83, x, y, color);}
   if ( number == 84) {vgaPrint(str84, x, y, color);}
   if ( number == 85) {vgaPrint(str85, x, y, color);}
   if ( number == 86) {vgaPrint(str86, x, y, color);}
   if ( number == 87) {vgaPrint(str87, x, y, color);}
   if ( number == 88) {vgaPrint(str88, x, y, color);}
   if ( number == 89) {vgaPrint(str89, x, y, color);}
   if ( number == 90) {vgaPrint(str90, x, y, color);}
   if ( number == 91) {vgaPrint(str91, x, y, color);}
   if ( number == 92) {vgaPrint(str92, x, y, color);}
   if ( number == 93) {vgaPrint(str93, x, y, color);}
   if ( number == 94) {vgaPrint(str94, x, y, color);}
   if ( number == 95) {vgaPrint(str95, x, y, color);}
   if ( number == 96) {vgaPrint(str96, x, y, color);}
   if ( number == 97) {vgaPrint(str97, x, y, color);}
   if ( number == 98) {vgaPrint(str98, x, y, color);}
   if ( number == 99) {vgaPrint(str99, x, y, color);}
   if ( number == 100) {vgaPrint(str100, x, y, color);}
   if ( number == 101) {vgaPrint(str101, x, y, color);}
   if ( number == 102) {vgaPrint(str102, x, y, color);}
   if ( number == 103) {vgaPrint(str103, x, y, color);}
   if ( number == 104) {vgaPrint(str104, x, y, color);}
   if ( number == 105) {vgaPrint(str105, x, y, color);}
   if ( number == 106) {vgaPrint(str106, x, y, color);}
   if ( number == 107) {vgaPrint(str107, x, y, color);}
   if ( number == 108) {vgaPrint(str108, x, y, color);}
   if ( number == 109) {vgaPrint(str109, x, y, color);}
   if ( number == 110) {vgaPrint(str110, x, y, color);}
   if ( number == 111) {vgaPrint(str111, x, y, color);}
   if ( number == 112) {vgaPrint(str112, x, y, color);}
   if ( number == 113) {vgaPrint(str113, x, y, color);}
   if ( number == 114) {vgaPrint(str114, x, y, color);}
   if ( number == 115) {vgaPrint(str115, x, y, color);}
   if ( number == 116) {vgaPrint(str116, x, y, color);}
   if ( number == 117) {vgaPrint(str117, x, y, color);}
   if ( number == 118) {vgaPrint(str118, x, y, color);}
   if ( number == 119) {vgaPrint(str119, x, y, color);}
   if ( number == 120) {vgaPrint(str120, x, y, color);}
   if ( number == 121) {vgaPrint(str121, x, y, color);}
   if ( number == 122) {vgaPrint(str122, x, y, color);}
   if ( number == 123) {vgaPrint(str123, x, y, color);}
   if ( number == 124) {vgaPrint(str124, x, y, color);}
   if ( number == 125) {vgaPrint(str125, x, y, color);}
   if ( number == 126) {vgaPrint(str126, x, y, color);}
}
