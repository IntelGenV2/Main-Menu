/******************************************************************* 
*  ArduinoVGAgame - Version 2 - September the 29th 2017            * 
*                                                                  *
*  Arduino VGA Game is a game consolle for VGA monitors,           * 
*  written by Roberto Melzi, running for Arduino software          * 
*  IDE version 1.6.4                                               * 
*  VGAx library does not work for newer or elder software          *
*  versions.                                                       * 
*  The consolle includes the games:                                *
*  Pong, Breakout, Bomber, Etch-a-Sketch and Tetris.               *
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
#include <math.h>
#include <VGAXUtils.h> 

#define FNT_NANOFONT_HEIGHT 6
#define FNT_NANOFONT_SYMBOLS_COUNT 95
#define PADDLE_HEIGHT 8
#define PADDLE_WIDTH 2
#define RIGHT_PADDLE_X (VGAX_WIDTH-4)
#define LEFT_PADDLE_X 2
#define MAX_Y_VELOCITY 0.1
#define WHEEL_ONE_PIN 2 //analog
#define WHEEL_TWO_PIN 1 //analog
#define BUTTON_1_PIN 13 //digital 
#define BUTTON_2_PIN 5  //digital
#define BUTTON_3_PIN 11 //digital
#define BUTTON_4_PIN 12 //digital
#define BUTTON_5_PIN 10 //digital
// NB: pin A0 is used for the sound 

VGAX vga;
VGAXUtils vgaU;

//data size=570 bytes
const unsigned char fnt_nanofont_data[FNT_NANOFONT_SYMBOLS_COUNT][1+FNT_NANOFONT_HEIGHT] PROGMEM={
{ 1, 128, 128, 128, 0, 128, 0, }, //glyph '!' code=0
{ 3, 160, 160, 0, 0, 0, 0, }, //glyph '"' code=1
//{ 5, 80, 248, 80, 248, 80, 0, },  //glyph '#' code=2
{ 5, 240, 240, 240, 240, 240, 240, },  //glyph '#' = 'full rectangle' code=2
//{ 5, 32, 160, 240, 120, 32, 32, },  //glyph '#' = 'planeR' code=2
{ 3, 80, 32, 112, 112, 32, 0, },  //glyph '$' = 'bomb' code=3
{ 5, 32, 40, 120, 240, 32, 32, },  //glyph '%' = 'planeL' code=4
{ 5, 96, 144, 104, 144, 104, 0, },  //glyph '&' code=5
{ 5, 248, 248, 248, 248, 248, 248, },  //glyph ''' = 'rectangle 5 x 6' code=6
//{ 5, 120, 160, 112, 40, 240, 0, },  //glyph '$' code=3
//{ 5, 136, 16, 32, 64, 136, 0, },  //glyph '%' code=4
//{ 5, 96, 144, 104, 144, 104, 0, },  //glyph '&' code=5
//{ 2, 128, 64, 0, 0, 0, 0, },  //glyph ''' code=6
{ 2, 64, 128, 128, 128, 64, 0, }, //glyph '(' code=7
{ 2, 128, 64, 64, 64, 128, 0, },  //glyph ')' code=8
{ 3, 0, 160, 64, 160, 0, 0, },  //glyph '*' code=9
{ 3, 0, 64, 224, 64, 0, 0, }, //glyph '+' code=10
{ 2, 0, 0, 0, 0, 128, 64, },  //glyph ',' code=11
{ 3, 0, 0, 224, 0, 0, 0, }, //glyph '-' code=12
{ 1, 0, 0, 0, 0, 128, 0, }, //glyph '.' code=13
{ 5, 8, 16, 32, 64, 128, 0, },  //glyph '/' code=14
{ 4, 96, 144, 144, 144, 96, 0, }, //glyph '0' code=15
{ 3, 64, 192, 64, 64, 224, 0, },  //glyph '1' code=16
{ 4, 224, 16, 96, 128, 240, 0, }, //glyph '2' code=17
{ 4, 224, 16, 96, 16, 224, 0, },  //glyph '3' code=18
{ 4, 144, 144, 240, 16, 16, 0, }, //glyph '4' code=19
{ 4, 240, 128, 224, 16, 224, 0, },  //glyph '5' code=20
{ 4, 96, 128, 224, 144, 96, 0, }, //glyph '6' code=21
{ 4, 240, 16, 32, 64, 64, 0, }, //glyph '7' code=22
{ 4, 96, 144, 96, 144, 96, 0, },  //glyph '8' code=23
{ 4, 96, 144, 112, 16, 96, 0, },  //glyph '9' code=24
{ 1, 0, 128, 0, 128, 0, 0, }, //glyph ':' code=25
{ 2, 0, 128, 0, 0, 128, 64, },  //glyph ';' code=26
{ 3, 32, 64, 128, 64, 32, 0, }, //glyph '<' code=27
{ 3, 0, 224, 0, 224, 0, 0, }, //glyph '=' code=28
{ 3, 128, 64, 32, 64, 128, 0, },  //glyph '>' code=29
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
{ 3, 224, 64, 64, 64, 224, 0, },  //glyph 'I' code=40
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
{ 3, 224, 64, 64, 64, 64, 0, }, //glyph 'T' code=51
{ 4, 144, 144, 144, 144, 96, 0, },  //glyph 'U' code=52
{ 3, 160, 160, 160, 160, 64, 0, },  //glyph 'V' code=53
{ 5, 136, 168, 168, 168, 80, 0, },  //glyph 'W' code=54
{ 4, 144, 144, 96, 144, 144, 0, },  //glyph 'X' code=55
{ 3, 160, 160, 64, 64, 64, 0, },  //glyph 'Y' code=56
{ 4, 240, 16, 96, 128, 240, 0, }, //glyph 'Z' code=57
{ 2, 192, 128, 128, 128, 192, 0, }, //glyph '[' code=58
{ 5, 128, 64, 32, 16, 8, 0, },  //glyph '\' code=59
{ 2, 192, 64, 64, 64, 192, 0, },  //glyph ']' code=60
{ 5, 32, 80, 136, 0, 0, 0, }, //glyph '^' code=61
{ 4, 0, 0, 0, 0, 240, 0, }, //glyph '_' code=62
{ 2, 128, 64, 0, 0, 0, 0, },  //glyph '`' code=63
{ 3, 0, 224, 32, 224, 224, 0, },  //glyph 'a' code=64
{ 3, 128, 224, 160, 160, 224, 0, }, //glyph 'b' code=65
{ 3, 0, 224, 128, 128, 224, 0, }, //glyph 'c' code=66
{ 3, 32, 224, 160, 160, 224, 0, },  //glyph 'd' code=67
{ 3, 0, 224, 224, 128, 224, 0, }, //glyph 'e' code=68
{ 2, 64, 128, 192, 128, 128, 0, },  //glyph 'f' code=69
{ 3, 0, 224, 160, 224, 32, 224, },  //glyph 'g' code=70
{ 3, 128, 224, 160, 160, 160, 0, }, //glyph 'h' code=71
{ 1, 128, 0, 128, 128, 128, 0, }, //glyph 'i' code=72
{ 2, 0, 192, 64, 64, 64, 128, },  //glyph 'j' code=73
{ 3, 128, 160, 192, 160, 160, 0, }, //glyph 'k' code=74
{ 1, 128, 128, 128, 128, 128, 0, }, //glyph 'l' code=75
{ 5, 0, 248, 168, 168, 168, 0, }, //glyph 'm' code=76
{ 3, 0, 224, 160, 160, 160, 0, }, //glyph 'n' code=77
{ 3, 0, 224, 160, 160, 224, 0, }, //glyph 'o' code=78
{ 3, 0, 224, 160, 160, 224, 128, }, //glyph 'p' code=79
{ 3, 0, 224, 160, 160, 224, 32, },  //glyph 'q' code=80
{ 3, 0, 224, 128, 128, 128, 0, }, //glyph 'r' code=81
{ 2, 0, 192, 128, 64, 192, 0, },  //glyph 's' code=82
{ 3, 64, 224, 64, 64, 64, 0, }, //glyph 't' code=83
{ 3, 0, 160, 160, 160, 224, 0, }, //glyph 'u' code=84
{ 3, 0, 160, 160, 160, 64, 0, },  //glyph 'v' code=85
{ 5, 0, 168, 168, 168, 80, 0, },  //glyph 'w' code=86
{ 3, 0, 160, 64, 160, 160, 0, },  //glyph 'x' code=87
{ 3, 0, 160, 160, 224, 32, 224, },  //glyph 'y' code=88
{ 2, 0, 192, 64, 128, 192, 0, },  //glyph 'z' code=89
{ 3, 96, 64, 192, 64, 96, 0, }, //glyph '{' code=90
{ 1, 128, 128, 128, 128, 128, 0, }, //glyph '|' code=91
{ 3, 192, 64, 96, 64, 192, 0, },  //glyph '}' code=92
//{ 3, 96, 192, 0, 0, 0, 0, },  //glyph '~' code=93
{ 5, 32, 160, 240, 120, 32, 32, }, //= 'planeR' code=93
{ 4, 48, 64, 224, 64, 240, 0, },  //glyph '£' code=94
};

static const char str10[] PROGMEM="#"; 
static const char str15[] PROGMEM="Red wins!"; 
static const char str16[] PROGMEM="Green wins!"; 
static const char str18[] PROGMEM="Game Over!!!"; 
static const char str21[] PROGMEM="########";
static const char str30[] PROGMEM="Choose Arcade Game"; 
static const char str31[] PROGMEM="Pong"; 
static const char str32[] PROGMEM="Breakout"; 
static const char str33[] PROGMEM="Bomber"; 
static const char str34[] PROGMEM="Etch-a-Sketch"; 
static const char str35[] PROGMEM="Tetris"; 
static const char str40[] PROGMEM="X"; 
static const char str51[] PROGMEM="~"; //planeR
static const char str52[] PROGMEM="%"; //planeL
static const char str53[] PROGMEM="$"; //bomb
static const char str54[] PROGMEM="'"; //rectangle 5 x 6
static const char str59[] PROGMEM="'''''''"; //clear 'Hit' banner 
static const char str510[] PROGMEM="Hit!!!"; //'Hit' banner
static const char str511[] PROGMEM="Arduino VGA Bomber"; 
static const char str512[] PROGMEM="by Laurence Bosch"; 
static const char str515[] PROGMEM="Game Over!!!"; 
static const char str613[] PROGMEM="Game"; 
static const char str614[] PROGMEM="Over!"; 

void setup() {
  //Serial.begin(9600); 
  vga.begin();
  randomSeed(1);  
}

//-------------------------------- variables definition Pong ----------------------------
boolean buttonOneStatus; 
boolean buttonTwoStatus; 
boolean buttonThreeStatus; 
boolean buttonFourStatus; 
boolean buttonFiveStatus; 
byte wheelOnePosition; 
byte wheelTwoPosition;
byte state = 1; 
byte shot; // pong, bomber, breakout 
byte rightPaddleY;
byte leftPaddleY;
byte rightPaddleY0; 
byte leftPaddleY0; 
byte ballX; 
byte ballY; 
byte scoreR; 
byte scoreL; 
int beginning; // deve restare int poichè può assumere valori negativi, anche in breakout e bombard 
byte ticPosition = 12; 
float ballPX; // pong, breakout. No bomber
int ballPY; // pong, breakout, bomber //************** era un int
float ballVx; // già condivisa tra pong e bomber
float ballVy; // già condivisa tra pong e bomber
// ------------------------------------------ Variable definition Breakout ---------------------------- 
int speedX; //bomber e breakout 
int speedY; 
int speedT; //pong, breakout e bomber 
float variableFloat_2; //bomber, breakout 
float variableFloat_1; //bomber, breakout  
byte padPosition; 
byte padPositionOld; //bombard, breakout, tetris 
byte ballXold;
byte ballYold; 
byte gameStep; 
boolean cancelSafe; 
byte hitScore; 
byte lives = 8; //---------- qui lascio lives = 8 per pong. E' definito anche in fondo a parameterPongIni() ----------------
byte ballX0;
byte ballY0; 
byte iDel;
byte jDel; 
byte ballXhit; 
byte ballYhit; 
static const float pi PROGMEM = 3.1415926;
byte nBricks; 
byte color; 
static const float speedIncrement PROGMEM = 1.259921; //cubic root of two. Every three levels speed doubles --------------------
//----------------------------------------- Variable definition Bomber ---------------------------------------
int bombX; 
byte bomberVariableA; //only in bomber
byte score; 
byte bomberVariableB; //only in bomber
//-------------------------------------------------- variable specific for Tetris -----------------------------
byte block[4][2]={{0,0},{0,0},{0,0},{0,0}};
byte blockExt[4][2]={{0,0},{0,0},{0,0},{0,0}};
byte blockOld[4][2]={{0,0},{0,0},{0,0},{0,0}};
byte blockTmp[4][2]={{0,0},{0,0},{0,0},{0,0}};
byte blockTr[4][2]={{0,0},{0,0},{0,0},{0,0}};
byte yLine[4] = {0,0,0,0}; 
byte yLineTmp[4] = {0,0,0,0}; 
//----------------------------------------------------Variables definition end --------------------------------

//------------------------------------------------------------------------------------------------------

void processInputs() {
  buttonOneStatus = digitalRead(BUTTON_1_PIN); // ---------------- tasto nero
  buttonTwoStatus = digitalRead(BUTTON_2_PIN); // ---------------- tasto blu 
  buttonThreeStatus = digitalRead(BUTTON_3_PIN); // -------------- tasto rosso
  buttonFourStatus = digitalRead(BUTTON_4_PIN); // --------------- tasto giallo 
  buttonFiveStatus = digitalRead(BUTTON_5_PIN); // --------------- tasto verde 
  wheelOnePosition = 127 - byte(analogRead(WHEEL_ONE_PIN)/8); //to change direction of the wheel remove "127 -" ---------------------
  wheelTwoPosition = byte(analogRead(WHEEL_TWO_PIN)/8); 
}

void buttonZeroing(){
  buttonOneStatus = 0;
  buttonTwoStatus = 0; 
  buttonThreeStatus = 0; 
  buttonFourStatus = 0; 
}

void parameterPongIni() { // ------------ Pong ---------------------------------------------------------------- 
   parameterPongIni0(); 
   lives = 8;  
}

void parameterPongIni0() { // ------------ Pong ---------------------------------------------------------------- 
  rightPaddleY0 = (rightPaddleY + 26)%50 + 1; 
  leftPaddleY0 = (leftPaddleY + 26)%50 + 1; 
  ballVx = random(100, 160)/1000. + (scoreL + scoreR)/200.; //----- pong horizontal speed ----- from 0.1 to 0.16, up to 0.23 -------- 
  ballVy = random(-40, 40)/1000.;                           //----- pong vertical speed --------------- 
}

void parameterIniBomber() { // Bomber 
  shot = 12; 
  score = 80; 
  speedX = 256*(10 + random(VGAX_WIDTH - 20));
  speedY = 10 + random(VGAX_HEIGHT/4);
  bomberVariableA = byte(speedX/256);
  ballVx = speedY + 4;
  speedT = 25 + random(50); 
  variableFloat_2 = speedT/256. - random(-10,10)/100.; 
  variableFloat_1 = random(10)/200.; 
  lives = 0;
  buttonOneStatus = 0; 
}

void gameIniBreakout(){ // Breakout
  ballPX = 70.;
  ballPY = 3000;
  cancelSafe = 0;
  hitScore = 0; 
  nBricks = 0;
  color = 1; 
  lives = 9; 
  speedT = 80; //------------ Breakout ball speed at the beginning ---------------- 
  gameStep = 0; 
  beginning = 0; 
  variableFloat_1 = 180./4; 
  padPositionOld = 115;
  padPosition = 114;
  parameterUpdate(); 
  drawLives(); 
  drawBorderBreakout();
  drawBricksGrid(gameStep); 
}

void waitForStart(){ //-------------------------------------- Pong waiting screen --------------------------------------------------
   buttonZeroing(); 
   if(scoreR == lives || scoreR == 0){
      processInputs(); 
      ballY = byte(((wheelTwoPosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
      drawGameScreen(); 
   }
   if(scoreL == lives){
      processInputs(); 
      ballY = byte(((wheelOnePosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
      drawGameScreen(); 
    }
    if (buttonOneStatus == 1 || buttonTwoStatus == 1){ 
       ballPX = ballX; 
       ballPY = ballY*100;
       parameterPongIni(); 
       scoreL = 0; 
       scoreR = 0; 
       drawScore(); 
       buttonZeroing();
       state = 3; 
    }
    if (buttonThreeStatus == 1) { state = 0; vga.delay(200); }
}

void drawPaddles(){ // Pong
    // ----------------- draw right paddle -----------------------------------------------
    rightPaddleY = byte(((wheelOnePosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 1);
    shot = RIGHT_PADDLE_X; 
    if (rightPaddleY != rightPaddleY0 || beginning > 0){
      vgaU.draw_column(shot, rightPaddleY0, rightPaddleY0 + PADDLE_HEIGHT, 0);
      vgaU.draw_column(shot + 1, rightPaddleY0, rightPaddleY0 + PADDLE_HEIGHT, 0);
      vgaU.draw_column(shot, rightPaddleY, rightPaddleY + PADDLE_HEIGHT, 2);
      vgaU.draw_column(shot + 1, rightPaddleY, rightPaddleY + PADDLE_HEIGHT, 2);
    }
    // ----------------- draw left paddle -------------------------------------------------
    leftPaddleY = byte(((wheelTwoPosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 1);
    shot = LEFT_PADDLE_X;
    if (leftPaddleY != leftPaddleY0 || beginning > 0){
       vgaU.draw_column(shot, leftPaddleY0, leftPaddleY0 + PADDLE_HEIGHT, 0);
       vgaU.draw_column(shot + 1, leftPaddleY0, leftPaddleY0 + PADDLE_HEIGHT, 0);
       vgaU.draw_column(shot, leftPaddleY, leftPaddleY + PADDLE_HEIGHT, 1);
       vgaU.draw_column(shot + 1, leftPaddleY, leftPaddleY + PADDLE_HEIGHT, 1);
    }
}

void drawBall(){ // Pong
   if ((ballX != iDel) || (ballY != jDel)){
      vga.putpixel(iDel, jDel, 0);
      vga.putpixel(iDel, jDel + 1, 0);
      vga.putpixel(iDel + 1, jDel, 0);
      vga.putpixel(iDel + 1, jDel + 1, 0);
      vga.putpixel(ballX, ballY, 3);
      vga.putpixel(ballX, ballY + 1, 3);
      vga.putpixel(ballX + 1, ballY, 3);
      vga.putpixel(ballX + 1, ballY + 1, 3);
   }
}

void drawNet(){ // Pong 
   for(int i=1; i<VGAX_HEIGHT - 4; i += 6) {
      vgaU.draw_column(VGAX_WIDTH/2, i, i + 3, 3);
   }
}

void drawPlaneBomber() { // --------------- draw plane ----------------------------------------------  
   if(speedT > 0 && ballX != ballX0) {
      vgaPrint(str54, ballX0, ballY0, 0); 
      vgaPrint(str51, ballX, ballY, 1);
   }
   if(speedT < 0 && ballX != ballX0) {
      vgaPrint(str54, ballX0, ballY0, 0); 
      vgaPrint(str52, ballX, ballY, 1);
   }
}

void drawBombBomber() { // -------------------- draw bomb -----------------------------------------------
   vgaPrint(str53, bomberVariableB, ballVy, 0);
   vgaPrint(str53, bombX, byte(ballPY/100), 2);
}

void drawBombBomberard() { // ----------------- draw bombard --------------------------------------------
    if (padPosition != padPositionOld) {
      vgaU.draw_column(padPositionOld, VGAX_HEIGHT-4, VGAX_HEIGHT-7, 0); 
      vgaU.draw_row(VGAX_HEIGHT-4, padPositionOld-2, padPositionOld+3, 0); 
      vgaU.draw_row(VGAX_HEIGHT-3, padPositionOld-5, padPositionOld+6, 0); 
      vgaU.draw_row(VGAX_HEIGHT-2, padPositionOld-5, padPositionOld+6, 0); 
     
      vgaU.draw_column(padPosition, VGAX_HEIGHT-4, VGAX_HEIGHT-7, 3); 
      vgaU.draw_row(VGAX_HEIGHT-4, padPosition-2, padPosition+3, 3); 
      vgaU.draw_row(VGAX_HEIGHT-3, padPosition-5, padPosition+6, 3); 
      vgaU.draw_row(VGAX_HEIGHT-2, padPosition-5, padPosition+6, 3); 
   }
}

void drawShotBomber() { // --------------------- draw shot ----------------------------------------------
   if ( beginning == shot - 1) {
      vgaU.draw_column(padPositionOld, 2, VGAX_HEIGHT - 7, 0);
   }
   if ( beginning == shot) {
      vgaU.draw_column(padPosition, 2, VGAX_HEIGHT - 7, 1);
      vga.delay(5); 
   }
}

void drawScoreBomber() { // Bomber
   vgaU.draw_line(VGAX_WIDTH - (116 - 1), 1, VGAX_WIDTH - score/2 - 1, 1, 0);  
   vga.putpixel(VGAX_WIDTH - 116, 1, (lives + 2)%3 + 1);
   vgaU.draw_line(VGAX_WIDTH - 1 , 1, VGAX_WIDTH - score/2, 1, 3);  
}

void drawGameScreenBomber() { // ----------------- main function to draw Bomber game screen ---------------------------
   drawPlaneBomber();
   drawBombBomber();
   drawScoreBomber(); 
   vgaU.draw_row(VGAX_HEIGHT-1, VGAX_WIDTH, 1, 2); 
   drawBombBomberard(); 
   drawShotBomber(); 
}

void parameterUpdate() { // Breakout
  variableFloat_2 = variableFloat_1/180.* pi; 
  if (speedX > 0) {speedX = int(sin(variableFloat_2)*speedT);} else {speedX = int(-sin(variableFloat_2)*speedT);} 
  if (speedY > 0) {speedY = int(cos(variableFloat_2)*speedT);} else {speedY = int(-cos(variableFloat_2)*speedT);} 
}

void drawLives() { // Breakout
    vgaPrint(str10, 110, 10, 0);
    if (lives > 0) {vgaPrintNumber(lives, 110, 10, 3);}
    if(lives == 0) {gameOverBreakout();} 
}

void gameOverBreakout() { // Breakout
  vgaTone(660, 200); 
  vgaTone(330, 200);
  vgaTone(165, 200); 
  vgaTone(82, 200);
  vgaPrint(str18, 25, 40, 1);
  ballStart(); 
  //if (state != 1){ 
  if (state == 4){ 
     vga.clear(0); 
     gameIniBreakout(); 
  }
  vga.delay(300);
  buttonZeroing();
}

void ballStart(){ // Breakout
   ballPX = padPosition; 
   ballPY = 5500; 
   ballCoordinatesBreakout(); 
   ballY = 55; 
   drawBallBreakout(ballX, ballY, 2); 
   while (buttonOneStatus == 0 && state == 4){
      padPositionOld = padPosition; 
      processInputs();
      padPosition = map(wheelOnePosition, 127, 0, 7, 93); 
      if (padPosition != padPositionOld){
         drawPadBreakout(padPositionOld, 0); 
         drawPadBreakout(padPosition, 1);
         drawBallBreakout(ballX, ballY, 0); 
         ballPX = padPosition; 
         ballPY = 5500; 
         ballCoordinatesBreakout(); 
         ballY = 55; 
         drawBallBreakout(ballX, ballY, 2); 
      }
      if (buttonThreeStatus == 1){ // --------------------- ritorna al menu iniziale -------------------------
         state = 0; 
         buttonZeroing(); 
         vga.clear(0);
         vga.delay(300);
      }
   }
}

void drawBorderBreakout() { // Breakout 
   vgaU.draw_line(0, 0, 0, 59, 3);
   vgaU.draw_line(0, 0, 99, 0, 3);
   vgaU.draw_line(0, 59, 99, 59, 3);
   vgaU.draw_line(99, 0, 99, 60, 3);
}

void drawPadBreakout(byte padPosition, byte color) { // Breakout
   vgaU.draw_line(padPosition - 6, 58, padPosition + 6, 58, color);
   vgaU.draw_line(padPosition - 6, 57, padPosition + 6, 57, color);
}

void brick(byte x, byte y, byte col) { // Breakout
   vgaU.draw_line(x - 5, y + 1, x + 5, y + 1 , col);
   vgaU.draw_line(x - 5, y - 1, x + 5, y - 1 , col);
   vga.putpixel(x - 5, y, col); 
   vga.putpixel(x + 4, y, col); 
}

void drawBricksGrid(int n) { // Breakout
  nBricks = 0; 
  if (n%3 == 0) {   
    for (int i = 1; i <= int(100/13 - 1); i++) {
      for (int j = 1; j < 5; j++) {
         color = (i + j)%3 + 1; 
         brick(8 + i*12, 3 + j*4, color); 
         if (color |= 0) {nBricks++;}
      }
    }
  }
  if (n%3 == 1) {   
    for (int i = 0; i <= int(100/13); i++) {
      for (int j = 0; j < 7; j++) {
         color = (i + j)%4 + 0; 
         brick(8 + i*12, 3 + j*4, color); 
         if (color |= 0) {nBricks++;}
      }
    }
  }
  if (n%3 == 2) {   
    for (int i = 0; i <= int(100/13); i++) {
      for (int j = 0; j < 7; j++) {
         color = (i + j)%3 + 1; 
         brick(8 + i*12, 3 + j*4, color); 
         if (color |= 0) {nBricks++;}
      }
    }
  }
}

void searchHitBrick(int bX, int bY) { // Breakout
   ballX0 = 120;
   ballY0 = 60;
   for (int i = 0; i <= int(100/13); i++) {
      for (int j = 0; j < 7; j++) {
         if (abs(8 + i*12 - bX) < ballX0){
            ballX0 = abs(8 + i*12 - bX); 
            iDel = i;
         }
         if (abs(1 + 2 + j*4 - bY) < ballY0){
            ballY0 = abs(1 + 2 + j*4 - bY); 
            jDel = j;
         }
      }
   }
   brick(8 + iDel*12, 3 + jDel*4, 0); 
   nBricks--; 
   if (nBricks == 0){nextlivesBreakout();}
}

void drawBallBreakout(byte x, byte y, byte col) { // Breakout
   vga.putpixel(x, y, col); 
   vga.putpixel(x + 1, y, col); 
   vga.putpixel(x, y + 1, col); 
   vga.putpixel(x + 1, y + 1, col);
}

void ballCoordinatesBreakout() { // Breakout
  ballXold = ballX; 
  ballYold = ballY; 
  ballPX += float(speedX/1000.);
  ballPY += speedY/10.;
  ballX = byte(ballPX); 
  ballY = byte(ballPY/100); 
}

void nextlivesBreakout() { // Breakout
  gameStep++; 
  speedT = speedIncrement*speedT; 
  drawBricksGrid(gameStep); 
}

void drawBorder() { // Pong
    vgaU.draw_line(0,0,VGAX_WIDTH-1,0,3);
    vgaU.draw_line(0,VGAX_HEIGHT-1,VGAX_WIDTH-1,VGAX_HEIGHT-1,3);
    vgaU.draw_line(0,0,0,VGAX_HEIGHT-1,3);
    vgaU.draw_line(VGAX_WIDTH-1,0,VGAX_WIDTH-1,VGAX_HEIGHT,3);
}

void drawScore() { // ---------------- Pong score and win --------------------------------------------
    vgaPrint(str10, 52, 4, 0);
    vgaPrint(str10, 64, 4, 0);
    vgaPrintNumber(scoreL, 52, 4, 1); 
    vgaPrintNumber(scoreR, 64, 4, 2);
    if(scoreL == lives) {
       vgaPrint(str15, 12, 24, 1);
       ballX = VGAX_WIDTH - 6; 
       buttonZeroing(); 
       while(buttonOneStatus == 0 && buttonTwoStatus == 0 && buttonThreeStatus == 0){
          processInputs(); 
          ballY = byte(((wheelOnePosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
          drawGameScreen(); 
       }
    }
    if(scoreR == lives) {
       vgaPrint(str16, 66, 24, 2);
       ballX = 4; 
       buttonZeroing(); 
       while(buttonOneStatus == 0 && buttonTwoStatus == 0 && buttonThreeStatus == 0){
          processInputs(); 
          ballY = byte(((wheelTwoPosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
          drawGameScreen(); 
       }
    }
    if(scoreL == lives || scoreR == lives){ //---------------------------- Pong end --------------------- 
       buttonZeroing(); 
       do{ 
          processInputs(); 
       } while (buttonOneStatus == 0 && buttonTwoStatus == 0 && buttonThreeStatus == 0);  
       if (buttonThreeStatus == 1){ 
          state = 0;
          vga.delay(300);
       }
       else{
          vga.delay(300);
          parameterPongIni();
          drawPongStartScreen(); 
          state = 2; 
       }
    }
}

void drawPongStartScreen() { // Pong 
   vgaPrint(str10, 52, 4, 0);
   vgaPrint(str10, 64, 4, 0);
   vgaPrintNumber(0, 52, 4, 1);
   vgaPrintNumber(0, 64, 4, 2);
   vgaPrint(str16, 66, 24, 0);
   vgaPrint(str15, 12, 24, 0);
   vgaPrint(str21, 11, 24, 0);
   vgaPrint(str21, 65, 24, 0);
   drawBorder(); 
   drawGameScreen(); 
   buttonZeroing(); 
   vga.delay(200);
} 

void drawGameScreen() { // Pong 
    drawBall(); 
    drawPaddles(); 
    drawNet(); 
    iDel = ballX;
    jDel = ballY; 
    leftPaddleY0 = leftPaddleY;
    rightPaddleY0 = rightPaddleY; 
}

void gameOverSoundBomber() { // Bomber
   vga.delay(300);
   vgaTone(660, 200); 
   vgaTone(330, 200);
   vgaTone(165, 200); 
   vgaTone(82, 200);
}

void bomberHitSoundBomber() { //Bomber
   vgaTone(880, 200); 
   vgaTone(440, 200); 
   vgaTone(220, 200);
   vgaTone(110, 200); 
}

void nextlivesSoundBomber() { //Bomber
   vgaTone(440, 100);
   vgaTone(880, 100);
}

//------------------------------------------- the next three voids are shared ----------------------------------------------
void vgaTone(int freq, byte time) {
   vga.tone(freq);
   vga.delay(time); 
   vga.noTone(); 
}

void vgaPrint(const char* str, byte x, byte y, byte color){
   vga.printPROGMEM((byte*)fnt_nanofont_data, FNT_NANOFONT_SYMBOLS_COUNT, FNT_NANOFONT_HEIGHT, 3, 1, str, x, y, color);
}

void vgaPrintNumber(byte number, byte x, byte y, byte color){
   char scoreChar[2];
   sprintf(scoreChar,"%d",number);
   vga.printSRAM((byte*)fnt_nanofont_data, FNT_NANOFONT_SYMBOLS_COUNT, FNT_NANOFONT_HEIGHT, 1, 1, scoreChar, x, y, color);
}

// -------------------------------------- This is the main loop of the game -----------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
void loop() {
  if (state != 5) {processInputs(); } //tetris has its own processInputsTetris()
  if(state == 1 || state == 0) { drawStartMenu(); } 
  if(state == 2) { waitForStart(); }  // Pong 
  if(state == 3) { pong(); }
  if(state == 4) { breakout(); }
  if(state == 5) { tetris(); }
  if(state == 6) { bomber(); }
  if(state == 7) { drawingToy(); }
  //if(state == 8) { vga.clear(0); state = 1;} 
} 
// ------------------------------------------- end of main loop -----------------------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

//------------------------------------------------------- start screen -------------------------------------------------------
void drawStartMenu(){
   if (state == 0) {
      state = 1; 
      ballX = 4;
      ballY = 20;
      iDel = 21;
      jDel = 21; 
      vga.clear(0);
   }
   vgaPrint(str30, 20, 2, 3);  // Choose a game
   vgaPrint(str31, 38, 12, 2); // pong
   vgaPrint(str32, 38, 20, 2); // breakout
   vgaPrint(str33, 38, 28, 2); // bomber 
   vgaPrint(str34, 38, 36, 2); // drawing toy 
   vgaPrint(str35, 38, 44, 2); // tetris 
   vgaPrint(str40, 26, ticPosition, 1); 
   vga.delay(50);
   processInputs(); 
   if (buttonOneStatus == 1){ //game selector (X) moves down ---------------
      buttonZeroing(); 
      vgaPrint(str40, 26, ticPosition, 0); 
      ticPosition += 8; 
      if (ticPosition > 44) {ticPosition = 12;}
      vgaPrint(str40, 26, ticPosition, 1);
      vga.delay(200);
   }
   if (buttonThreeStatus == 1){ //game selector (X) moves up ---------------
      buttonZeroing(); 
      vgaPrint(str40, 26, ticPosition, 0); 
      ticPosition -= 8; 
      if (ticPosition < 12) {ticPosition = 44;}
      vgaPrint(str40, 26, ticPosition, 1);
      vga.delay(200);
   }
   if (buttonFourStatus == 1){ //game choice ---------------------------
      buttonZeroing(); 
      vga.clear(0);
      if (ticPosition == 12) { // Pong
         lives = 8; // ----- correzione baco seconda partita pong 
         scoreR = 0;
         scoreL = 0; 
         parameterPongIni0(); // ---------- evita che i paddle all'inizio si cancellino 
         iDel = 21;
         jDel = 21; 
         state = 2; 
         ballX = 4; 
         ballY = byte(((wheelTwoPosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
         drawPongStartScreen(); 
      } 
      if (ticPosition == 20) { // Breakout 
         state = 4;
         buttonZeroing(); 
         gameIniBreakout(); 
         vga.delay(200); 
      } 
      if (ticPosition == 28) { // Bomber
         parameterIniBomber(); 
         state = 6;
      } 
      if (ticPosition == 36) { // drawing Toy 
         color = 1; 
         state = 7;
      } 
      if (ticPosition == 44) { // Tetris
         tetrisIni(); 
         state = 5;
      } 
   }
}
//----------------------------------------------- start screen end -----------------------

//----------------------------------------------- pong -------------------------------------------------- 
void pong(){ 
    
     ballPX += ballVx;     // float
     ballPY += int(ballVy*100); // int 
     ballX = byte(ballPX);
     ballY = byte(ballPY/100.);
    
     if(ballY < 1 || ballY >= VGAX_HEIGHT - 2 ) {
        ballVy = -ballVy;
        ballPY += int(ballVy*100);
        ballY = byte(ballPY/100);
        vgaTone(880,30); 
     }; 
     
     // ---------------------------------------- left paddle hit -------------------------------------------------
     if(ballVx < 0 && ballX == LEFT_PADDLE_X+PADDLE_WIDTH -1 && ballY >= leftPaddleY - 1 && ballY <= leftPaddleY + PADDLE_HEIGHT) { 
        ballVx = -ballVx;
        ballVy += 0.2 * ((ballY - leftPaddleY + 1) - (PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2);
        vgaTone(660, 30);
        drawScore();
        beginning = 2; 
        drawPaddles(); 
      }
     //----------------------------------------- right paddle hit --------------------------------------------------
     if(ballVx > 0 && ballX == RIGHT_PADDLE_X - 1 && ballY >= rightPaddleY - 1 && ballY <= rightPaddleY + PADDLE_HEIGHT) { 
        ballVx = -ballVx;
        ballVy += 0.2 * ((ballY - rightPaddleY + 1) - (PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2);
        vgaTone(660, 30);
        drawScore();
        beginning = 2; 
        drawPaddles(); 
     }
     
     //limit vertical speed
     if(ballVy > MAX_Y_VELOCITY) ballVy = MAX_Y_VELOCITY;
     if(ballVy < -MAX_Y_VELOCITY) ballVy = -MAX_Y_VELOCITY;
     
     if(ballX <= 0) { // ------------------------- ball out from left ------------------------------------------
        vgaTone(220, 200);
        scoreR++; 
        drawScore();  
        ballX = 4;   
        beginning = 1;  
        while(buttonTwoStatus == 0 && buttonThreeStatus == 0){
           processInputs(); 
           ballY = byte(((wheelTwoPosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
           drawGameScreen(); 
           beginning = 0; 
        }
        ballPX = ballX; 
        ballPY = ballY*100;
        parameterPongIni(); 
        drawBorder();
     }
     if(ballX >= VGAX_WIDTH - 2) { // ------------ ball out from right ------------------------------------------
        vgaTone(220, 200); 
        scoreL++; 
        drawScore();      
        ballX = VGAX_WIDTH - 6;   
        beginning = 1; 
        while(buttonOneStatus == 0 && buttonThreeStatus == 0){
           processInputs(); 
           ballY = byte(((wheelOnePosition) * (VGAX_HEIGHT-PADDLE_HEIGHT-1))/ 128 + 4);
           drawGameScreen(); 
           beginning = 0; 
        }
        if (buttonThreeStatus == 0) {state == 0;} //--------------------- to exit pong ----------------------------
        ballPX = ballX; 
        ballPY = ballY*100;
        parameterPongIni(); 
        drawBorder(); 
        ballVx = -ballVx;
     }
     if (state == 1 || state == 0) {
        vga.clear(0); 
        vga.delay(300);
     }
     else {drawGameScreen();} //-------------------------------- Pong end check ---------------------
     beginning -= 1; 
     //beginning = 0; 
     beginning = constrain(beginning, 0, 10); 
  }
// ---------------------------------------- void pong() end ---------------------------------------------


// ----------------------------------------------- breakout -----------------------------------
void breakout(){
  if (beginning == 0){ 
     padPositionOld = padPosition; 
     processInputs();
     padPosition = map(wheelOnePosition, 127, 0, 7, 93); 
     gameIniBreakout(); 
     ballStart(); 
     beginning = 1; 
  }
  padPositionOld = padPosition; 
  processInputs();
  //buttonOneStatus = 1; // for debugging ----------------------
  padPosition = map(wheelOnePosition, 127, 0, 7, 93); 

  if (padPosition != padPositionOld) {
     drawPadBreakout(padPositionOld, 0); 
     drawPadBreakout(padPosition, 1);
  }
  
  ballCoordinatesBreakout(); 
  
  if ( ballX != ballXold || ballY != ballYold) { 
     if (cancelSafe == 0) {
        drawBallBreakout(ballXold, ballYold, 0); 
        cancelSafe = 1; 
     }
     if (vga.getpixel(ballX, ballY) != 0) {hitScore += 1;}
     if (vga.getpixel(ballX + 1, ballY) != 0) {hitScore += 2;}
     if (vga.getpixel(ballX, ballY + 1) != 0) {hitScore += 4;}
     if (vga.getpixel(ballX + 1, ballY + 1) != 0) {hitScore += 8;}
     if (hitScore == 0) { //------------------------------- ball did not hit anything and can go ahead --------------
        drawBallBreakout(ballX, ballY, 2); 
        cancelSafe = 0; 
     }
     else { //--------------------------------- ball in breakout has hit something -------------------------- 
        if (hitScore == 3 | hitScore == 12) {
            speedY = -speedY;
        }
        else {
           if (hitScore == 5 | hitScore == 10) {
              speedX = -speedX;
           }
           else {
              speedX = -speedX;
              speedY = -speedY;
           }
        }
        if (ballY > 55) {
           if (vga.getpixel(ballX, ballY + 1) == 1 | vga.getpixel(ballX + 1, ballY + 1) == 1) { //-------------- breakout ball hits the paddle ----------------------- 
              variableFloat_1 = variableFloat_1 - 2*speedX/abs(speedX)*(padPosition - ballX); 
              if (variableFloat_1 < 20) {variableFloat_1 = 20;}
              if (variableFloat_1 > 70) {variableFloat_1 = 70;}
              parameterUpdate(); 
           } 
           else { //------------ breakout ball hits the bottom ----------------------- 
              lives = lives - 1; 
              if (lives |= 0) { vgaTone(110, 100); }
              drawLives(); 
              if (state == 4 ) { ballStart(); } 
              cancelSafe = 0; 
              speedY = - abs(speedY); 
           }
        }
        else if (ballX > 1 && ballX + 1 < 99 && ballY > 1) { //-------------- ball hits a brick otherwise it has it the border -------------- 
           vgaTone(440,30);
           if (hitScore == 1 | hitScore == 3 ) {ballXhit = ballX; ballYhit = ballY;}
           if (hitScore == 2 | hitScore == 10) {ballXhit = ballX + 1; ballYhit = ballY;}
           if (hitScore == 8 | hitScore == 12) {ballXhit = ballX + 1; ballYhit = ballY + 1;}
           if (hitScore == 4 | hitScore == 5) {ballXhit = ballX; ballYhit = ballY + 1;}
           searchHitBrick(ballXhit, ballYhit); 
        }
        if (ballPY <= 0) { //per baco ball che scompare da sopra ------------------------------------
           speedY = -speedY;
        }
        hitScore = 0; 
      }
   }
}
// ---------------------------------------- void breakout() end ---------------------------------------------

void drawingToy() { //--------------------------- drawing toy --------------------------------------------- 
  processInputs(); 
  ballX = byte(map(wheelOnePosition, 0, 128, VGAX_WIDTH - 1, 1));
  ballY = byte(map(wheelTwoPosition, 128, 0, VGAX_HEIGHT - 1, 1));
  vga.putpixel(ballX, ballY, color);
  if (buttonTwoStatus == 1 || buttonFourStatus == 1) {
     vga.clear(0);
     vgaTone(262, 80);
     vgaTone(330, 80);
     vgaTone(392, 80);
     vgaTone(524, 80);
  }
  if (buttonOneStatus == 1) {
    color += 1; 
    if (color == 4) 
       {color = 0;} 
    vgaTone(440, 60);  
    vga.delay(200); 
  }
  if(buttonThreeStatus == 1) {
     vga.clear(0);
     vga.delay(200); 
     state = 1;
  }
} 
// ---------------------------------------- void drawingToy() end ---------------------------------------------

// ---------------------------------------- Bomber---------------------------------------------------------------------------------------------------------------
void bomber() { 
     if (beginning == shot) {  // shot button has been hit ----------------------------------
        if (padPosition > int(speedX/256) - 2 - lives && padPosition < int(speedX/256) + 2 + lives) { // plane is hit -------------- 
           speedX = -2560; 
           score += 16;
           vgaTone(110, 60);
         }
         if (padPosition > (bombX - 2 ) && padPosition < (bombX + 2)) { // bomb is hit ----------------
            ballVx = speedY + 4;
            bomberVariableA = byte(speedX/256);
            variableFloat_2 = speedT/256. - 0.1*lives + random(-100,100)/1000.; 
            variableFloat_1 = 0.1*lives + random(100)/1000.; 
            iDel = 0;
            score += 16; 
            vgaTone(165, 60);
          }
     }     
 
     if( int(speedX/256) > VGAX_WIDTH || speedX < 0) {  // -------------- plane has escaped -----------------------------
        if (score > 2*(3 + lives)) { score += -2*(3 + lives); } else {score = 0;}
        speedT = random(50) + 50 + 50*lives; 
        speedY = random(VGAX_HEIGHT*2/3*100)/100 + 2; 
        if(random(1000) > 500)
           {speedX = 2560;} 
        else {
           speedX = 256*(VGAX_WIDTH - 10); 
           speedT = -speedT; 
        }
     }
     
     speedX += speedT; // plane next position -------------------------------------------------------
                                              
     bombX = bomberVariableA + variableFloat_2*iDel; // bomb position and trajectory ----------------------------------------------
     ballPY = 100.*ballVx + 60.*variableFloat_1*iDel + 8.*iDel*iDel/(60. - 20.*lives); //NB do not forget the "." otherwise ballPY will be an integer
     if(ballPY > 100*(VGAX_HEIGHT - 5) || bombX < 0 || bombX > VGAX_WIDTH){ //---------- the bomb hits the ground ------------------------------------
        if(bombX >= padPosition - 6 && bombX < padPosition + 6){ //---------------- the bomber has been hit ------------------------------------------
           vgaPrint(str510, 50, 10, 1); 
           bomberHitSoundBomber(); 
           vgaPrint(str59, 50, 10, 0); 
           vgaPrint(str59, 51, 10, 0); 
           if (score > 60) { score += -60; } else {score = 0;}
        }
        ballVx = speedY + 4;
        bomberVariableA = byte(speedX/256);
        variableFloat_2 = speedT/256 - 0.1*lives + random(-100,100)/1000.; 
        variableFloat_1 = 0.1*lives + random(100)/1000.; 
        iDel = 0;
     }
     else {iDel = iDel + 1;}
     // check the shot ---------------------------------------------------------
     if(beginning != 0 ) {
        beginning += -1; 
     }
       if ( buttonOneStatus == 1 && beginning == 0) {
          if (score > 1) { score += -1; } else {score = 0;} //******************************** essendo score raddoppiato, qui va lasciato -1 ****************************
          beginning = shot; 
          padPositionOld = padPosition;
          buttonOneStatus = 0; 
        }
         
        // check score state and Game Over ----------------------------------------------------- 
        if(score == 0) { // --------------- bomber Game Over !!! -------------------------------  
           buttonZeroing(); 
           gameOverSoundBomber(); 
           vgaPrint(str515, 40, 20, 1); 
           parameterIniBomber(); 
           padPositionOld = padPosition + 1;   
           do
           {
              processInputs(); 
           } while (buttonOneStatus == 0 && buttonTwoStatus == 0 && buttonThreeStatus == 0);  
           vga.delay(100);
           vga.clear(0); 
           if (buttonThreeStatus == 1){
              state = 0; 
              vga.delay(200);
           }
           buttonZeroing(); 
        }
        if (score > 232) {
          score = 116;
          nextlivesSoundBomber(); 
          lives++; 
     }
     ballX = byte(speedX/256); 
     ballY = byte(speedY); 
     padPosition = byte((((128 - wheelOnePosition)) * (VGAX_WIDTH - 12))/ 128 + 6);
     if(state == 1) {
        vga.clear(0); 
     }
     else{
        drawGameScreenBomber(); 
     }
     bomberVariableB = byte(bombX); //bomb X - int 
     ballVy = ballPY/100.; //bomb Y - both float
     ballX0 = ballX; //plane X - byte 
     ballY0 = ballY; //plane Y - byte 
     padPositionOld = padPosition; // pad position 
     if (buttonThreeStatus == 1) { 
        state = 0; 
        vga.delay(200);
     } 
}
// ---------------------------------------- void bomber() end ---------------------------------------------

// ---------------------------------------- Tetris --------------------------------------------------------
void processInputsTetris() { //buttonTwoStatus = digitalRead(A5); can be added for ballXhitwise rotation 
  if(buttonFiveStatus == 1) {
     buttonThreeStatus = digitalRead(BUTTON_3_PIN);
     buttonFourStatus = digitalRead(BUTTON_5_PIN); 
     buttonOneStatus = digitalRead(BUTTON_1_PIN);
     buttonFiveStatus = 0;
     vga.delay(25);
  }
  else{
     if(buttonThreeStatus == 1) {
        buttonFiveStatus = digitalRead(BUTTON_4_PIN);
        buttonFourStatus = digitalRead(BUTTON_5_PIN); 
        buttonOneStatus = digitalRead(BUTTON_1_PIN);
        buttonThreeStatus = 0;
        vga.delay(25);
     }
     else{
        if(buttonFourStatus == 1) {
           buttonFiveStatus = digitalRead(BUTTON_4_PIN);
           buttonThreeStatus = digitalRead(BUTTON_3_PIN); 
           buttonOneStatus = digitalRead(BUTTON_1_PIN);
           buttonFourStatus = 0;
           vga.delay(25);
        }
        else{
           if(buttonOneStatus == 1) {
              buttonFiveStatus = digitalRead(BUTTON_4_PIN);
              buttonThreeStatus = digitalRead(BUTTON_3_PIN); 
              buttonFourStatus = digitalRead(BUTTON_5_PIN);                                          
              buttonOneStatus = 0;
              //vga.delay(25);                                                                    
           }
           else{
              buttonFiveStatus = digitalRead(BUTTON_4_PIN); 
              buttonThreeStatus = digitalRead(BUTTON_3_PIN);
              buttonFourStatus = digitalRead(BUTTON_5_PIN); 
              buttonOneStatus = digitalRead(BUTTON_1_PIN);
           }
        }
     }
  }
  //button = buttonThreeStatus || buttonOneStatus; 
}

void tetrisIni(){
  padPositionOld = 0; 
  ballXold = 60; 
  ballYold = 6; 
  scoreL = 0; 
  scoreR = 0; //tetris score 
  ballXhit = 1; 
  ballYhit = 0;  
  color = 1; 
  hitScore = 0; 
  jDel = 0; 
  nBricks = 0; 
  beginning = 0;
  shot = 14; //tetris speed 
}

void clearInputs() {
  buttonFiveStatus = 0; 
  buttonThreeStatus = 0;
  buttonFourStatus = 0; 
  buttonOneStatus = 0;
  //button = 0; 
}

void drawMenu() {
  vga.clear(0);
  tetrisIni(); 
  drawGameScreenTetris();
  drawscoreR(scoreR);
}

void drawscoreR(int i) {
    if (i > 39){
       scoreR = 0;
       i = 0; 
       if (shot > 5 ) {shot = shot - 3;}
       else {shot = shot - 1;}
       if (shot < 3) {shot = 2;}
    }
    vgaU.draw_line(20, 10, 20, 50, 3); 
    vgaU.draw_line(20, 50, 20, 50 - i, 1); 
    vgaU.draw_line(19, 10, 22, 10, 3); 
    vgaU.draw_line(19, 50, 22, 50, 3); 
}
    
void drawBorderTetris() {
   // total screen size = 120/60
   // tetris game board: width = 30; heigh = 60
   vgaU.draw_line(44,0,78,0,3);
   vgaU.draw_line(44,59,78,59,3);
   vgaU.draw_line(44,0,44,59,3);
   vgaU.draw_line(78,0,78,60,3);
}

// --------------------- this is for the beginning game window ------------------------ 
void drawStartScreen() {
   drawBorderTetris(); 
   drawGameScreenTetris(); 
   //button = 0;
   vga.delay(200);
} 

// ---------------------- this is the main function to draw the game screen -----------
void drawGameScreenTetris() {
  drawBorderTetris(); 
}

// ----------------------- Tetriminos definition --------------------------------------
void blockDef(int i) {
  if (i == 1){
  // O
  block[0][0] = 0;
  block[0][1] = 0;
  block[1][0] = 1;
  block[1][1] = 0;
  block[2][0] = 0;
  block[2][1] = 1;
  block[3][0] = 1;
  block[3][1] = 1;
  color = 1; 
  }
  if (i == 2){
  // L
  block[0][0] = -1;
  block[0][1] = 0;
  block[1][0] = 0;
  block[1][1] = 0;
  block[2][0] = 1;
  block[2][1] = 0;
  block[3][0] = -1;
  block[3][1] = 1;
  color = 2; 
  }
  if (i == 3){
  // J
  block[0][0] = -1;
  block[0][1] = 0;
  block[1][0] = 0;
  block[1][1] = 0;
  block[2][0] = 1;
  block[2][1] = 0;
  block[3][0] = 1;
  block[3][1] = 1;
  color = 3; 
  }
  if (i == 4){
  // I
  block[0][0] = -1;
  block[0][1] = 0;
  block[1][0] = 0;
  block[1][1] = 0;
  block[2][0] = 1;
  block[2][1] = 0;
  block[3][0] = 2;
  block[3][1] = 0;
    color = 1; 
  }
  if (i == 5){
  // S
  block[0][0] = -1;
  block[0][1] = 0;
  block[1][0] = 0;
  block[1][1] = 0;
  block[2][0] = 0;
  block[2][1] = 1;
  block[3][0] = 1;
  block[3][1] = 1;
  color = 2; 
  }
  if (i == 6){
  // Z
  block[0][0] = -1;
  block[0][1] = 1;
  block[1][0] = 0;
  block[1][1] = 1;
  block[2][0] = 0;
  block[2][1] = 0;
  block[3][0] = 1;
  block[3][1] = 0;
  color = 3; 
  }
  if (i == 7){
  // T
  block[0][0] = -1;
  block[0][1] = 0;
  block[1][0] = 0;
  block[1][1] = 0;
  block[2][0] = 0;
  block[2][1] = 1;
  block[3][0] = 1;
  block[3][1] = 0;
  color = 1; 
  }
}

// -------------------------- expansion for 4:3 monitors ------------------------------ 
void blockExtension() {
   for (int i = 0; i < 4; i++){
      blockExt[0][0] = block[0][0]*3;
      blockExt[0][1] = block[0][1]*2;
      blockExt[1][0] = block[1][0]*3;
      blockExt[1][1] = block[1][1]*2;
      blockExt[2][0] = block[2][0]*3;
      blockExt[2][1] = block[2][1]*2;
      blockExt[3][0] = block[3][0]*3;
      blockExt[3][1] = block[3][1]*2;
   }
}
 
void blockRotation(int ballXhit){
  for (int i = 0; i < 4; i++){
     blockOld[0][0] = block[0][0];
     blockOld[0][1] = block[0][1];
     blockOld[1][0] = block[1][0];
     blockOld[1][1] = block[1][1];
     blockOld[2][0] = block[2][0];
     blockOld[2][1] = block[2][1];
     blockOld[3][0] = block[3][0];
     blockOld[3][1] = block[3][1];
  }
  for (int i = 0; i < 4; i++){
     block[0][0] = blockOld[0][1]*ballXhit;
     block[0][1] = -blockOld[0][0]*ballXhit;
     block[1][0] = blockOld[1][1]*ballXhit;
     block[1][1] = -blockOld[1][0]*ballXhit;
     block[2][0] = blockOld[2][1]*ballXhit;
     block[2][1] = -blockOld[2][0]*ballXhit;
     block[3][0] = blockOld[3][1]*ballXhit;
     block[3][1] = -blockOld[3][0]*ballXhit;
  }
}
void blockTranslation(int x, int y) {
   for (int i = 0; i < 4; i++){
      blockTr[0][0] = blockExt[0][0] + x;
      blockTr[0][1] = blockExt[0][1] + y;
      blockTr[1][0] = blockExt[1][0] + x;
      blockTr[1][1] = blockExt[1][1] + y;
      blockTr[2][0] = blockExt[2][0] + x;
      blockTr[2][1] = blockExt[2][1] + y;
      blockTr[3][0] = blockExt[3][0] + x;
      blockTr[3][1] = blockExt[3][1] + y;
   }
}

void delBlock(){
  if (hitScore == 1) {hitScore = 0;} 
  else {
      for (int i = 0; i < 4; i++){
         vgaU.draw_line(blockTr[i][0],blockTr[i][1],blockTr[i][0] + 3,blockTr[i][1],0);
         vgaU.draw_line(blockTr[i][0],blockTr[i][1] + 1,blockTr[i][0] + 3,blockTr[i][1] + 1,0);   
      }
   }
}

void drawBlock(){
  for (int i = 0; i < 4; i++){
     vgaU.draw_line(blockTr[i][0],blockTr[i][1],blockTr[i][0] + 3,blockTr[i][1], color);
     vgaU.draw_line(blockTr[i][0],blockTr[i][1] + 1,blockTr[i][0] + 3,blockTr[i][1] + 1, color);   
  }
  for (int i = 0; i < 4; i++){
     blockTmp[0][0] = blockTr[0][0];
     blockTmp[0][1] = blockTr[0][1];
     blockTmp[1][0] = blockTr[1][0];
     blockTmp[1][1] = blockTr[1][1];
     blockTmp[2][0] = blockTr[2][0];
     blockTmp[2][1] = blockTr[2][1];
     blockTmp[3][0] = blockTr[3][0];
     blockTmp[3][1] = blockTr[3][1];
  }
}

void drawBlockTmp(){
  for (int i = 0; i < 4; i++){
     vgaU.draw_line(blockTmp[i][0],blockTmp[i][1],blockTmp[i][0] + 3,blockTmp[i][1], color);
     vgaU.draw_line(blockTmp[i][0],blockTmp[i][1] + 1,blockTmp[i][0] + 3,blockTmp[i][1] + 1, color);   
  }
}

void checkBlock(){ 
  gameStep = 0;  
  for (int i = 0; i < 4; i++){
     gameStep = gameStep + vga.getpixel(blockTr[i][0], blockTr[i][1]) + vga.getpixel(blockTr[i][0] + 2, blockTr[i][1]);
  }
}

void replaceBlock(){
     blockExtension(); 
     blockTranslation(ballXold, ballYold); 
     checkBlock();
     if (gameStep == 0){
        drawBlock(); 
     }
     else // ---------- "else" is executed if the block cannot get down  ----------------- 
     {
        drawBlockTmp(); 
        checkForFullLine(); // ---- check if the line is filled when the block cennot get down anymore ---------------------- 
        scoreL = 1; 
        hitScore = 1; 
        if (ballYold < 8) {
           gameOver();
        }
     }
     vga.delay(1);
}

void gameOver(){ // ------------------------------------------- tetris Game Over! --------------------------------------------------
   scoreL = 0; 
   scoreR = 0;
   shot = 14;
   clearInputs(); 
   beginning = 0; 
   vgaPrint(str613, 92, 30, 1);
   vgaPrint(str614, 92, 38, 1);
   vga.delay(300);
   vgaTone(660, 200); 
   vgaTone(330, 200);
   vgaTone(165, 200); 
   vgaTone(82, 200);
   while (buttonFiveStatus == 0 && buttonThreeStatus == 0 && buttonFourStatus == 0 && buttonOneStatus == 0) {
      processInputsTetris(); 
      vga.delay(100);
   }
   if (buttonThreeStatus == 1) { 
      state = 1; 
      vga.delay(200);
   }
   clearInputs();  
   vga.clear(0);  
}

void drawballY0(){ // ----- draw next block on the right side -------------------------------- 
     blockExtension(); 
     blockTranslation(100, 10); 
     vgaU.draw_line(95, 8, 112, 8, 0);
     vgaU.draw_line(95, 9, 112, 9, 0);
     vgaU.draw_line(95, 10, 112, 10, 0);
     vgaU.draw_line(95, 11, 112, 11, 0);
     vgaU.draw_line(95, 12, 112, 12, 0);
     vgaU.draw_line(95, 13, 112, 13, 0);
     vgaU.draw_line(95, 14, 112, 14, 0);
     vgaU.draw_line(95, 15, 112, 15, 0);
     drawBlock(); 
}

void checkBlockTranslation(){
     ballXold = ballXold + ballYhit; 
     blockExtension(); 
     blockTranslation(ballXold, ballYold); 
     checkBlock();
     if (gameStep == 0){
        drawBlock(); 
     }
     else
     {
        ballXold = ballXold - ballYhit; 
        blockExtension(); 
        blockTranslation(ballXold, ballYold); 
        drawBlock(); 
     }
     vga.delay(50);
}

void checkBlockRotation(){
     //x = x + ballYhit; 
     blockExtension(); 
     blockTranslation(ballXold, ballYold); 
     checkBlock();
     if (gameStep == 0){
        drawBlock(); 
     }
     else
     {
        ballXhit = -ballXhit; 
        blockRotation(ballXhit); 
        blockExtension(); 
        blockTranslation(ballXold, ballYold); 
        drawBlock(); 
     }
     vga.delay(50);
}

void checkForFullLine() { // --------------------- check if the line is full and must be deleted --------------
   for (int i = 0; i < 4; i++){
      for (int j = 45; j < 76; j += 3) {
         if (vga.getpixel(j, blockTmp[i][1]) >0){jDel++; }
      }
      if (jDel == 11) { // ---- line is full and must be deleted ----------------------------------------------------------
         vgaU.draw_line(45, blockTmp[i][1], 78, blockTmp[i][1], 0); 
         vgaU.draw_line(45, blockTmp[i][1] + 1, 78, blockTmp[i][1] + 1, 0);   
         yLineTmp[padPositionOld] = blockTmp[i][1]; 
         yLine[padPositionOld] = blockTmp[i][1]; 
         padPositionOld++; 
         vgaTone(660,30); 
      }
      jDel = 0; 
    }
    if (yLineTmp[padPositionOld - 1] < yLine[0]) { // ------------ qui va capito se va < o > (penso >) ----------------------
       for (int i = 0; i < padPositionOld; i++) { // ------------- inversion ---------------------------------------
          yLine[i] = yLineTmp[padPositionOld - i - 1]; 
       }
    }
    for (int i = 0; i < padPositionOld; i++){   // ----------- block translation to lower position -------------- 
      for (int y = yLine[i] - 2; y > 0; y = y - 2) {
         for (int x = 45; x < 76; x += 3) {
            iDel = vga.getpixel(x, y); 
            if (iDel > 0) {
               vgaU.draw_line(x, y , x + 3, y , 0);
               vgaU.draw_line(x, y + 1, x + 3, y + 1, 0);
               vgaU.draw_line(x, y + 2, x + 3, y + 2, iDel);
               vgaU.draw_line(x, y + 3, x + 3, y + 3, iDel);
            } 
         }
      }
   }
   if (padPositionOld != 0) {
      scoreR = scoreR + 2*int(pow(2, padPositionOld));
      vgaTone(990,30); 
   } 
   drawscoreR(scoreR); 
   padPositionOld = 0; 
}

//-----------------------------------------------------------------------------------------------
//----------------------------------- tetris main loop ------------------------------------------
//-----------------------------------------------------------------------------------------------

void tetris() {
  processInputsTetris(); 
  if (scoreL < 2){ // --------------- to generate new tetraminos --------------------------------
     ballX0 = ballY0; 
     if (scoreL == 0 ) { // -------------- only at the game beginning  -------------------------
        drawMenu(); 
        ballX0 = 2 + byte(random(6)); // -------------- tetraminos "O" is excluded -----------------
        buttonFiveStatus = 0; 
        buttonThreeStatus = 0;
        buttonFourStatus = 0; 
        buttonOneStatus = 0; 
     }
     drawGameScreenTetris();
     drawscoreR(scoreR);
     ballY0 = 1 + byte(random(7));
     blockDef(ballY0);
     drawballY0();
     blockDef(ballX0);
     ballXold = 57; 
     ballYold = 5; 
     buttonFiveStatus = 1; 
     scoreL = 2; 
  }
  if (buttonThreeStatus == 1){ // ------------------------ rotation -------------------------
     //if (buttonTwoStatus == 1){ballXhit = -1;}
     if (buttonThreeStatus == 1){ballXhit = 1;}
     delBlock();
     blockRotation(ballXhit); 
     checkBlockRotation(); 
  }
  if (buttonFiveStatus == 1 || buttonFourStatus == 1){ // ------- translation ----------------------
     if (buttonFiveStatus == 1){ballYhit = 3;}
     if (buttonFourStatus == 1){ballYhit = -3;}
     delBlock();
     checkBlockTranslation();
  }
  beginning++; 
  if (beginning % shot > shot - 2 || buttonOneStatus == 1){ // --- Tetraminos falling ----------
     if (shot < 3) {shot = 2;}
     ballYold = ballYold + 2;
     delBlock(); 
     replaceBlock(); 
  }
  else
  {vga.delay(10 + 2*shot);}
}
//-----------------------------------------------------------------------------------------------
//--------------------- This is the end of the main loop ----------------------------------------
//-----------------------------------------------------------------------------------------------

