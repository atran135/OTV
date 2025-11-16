#include <Arduino.h>
#include <math.h>

int mission_check = 0;
int mission_phase = 0;

double x_coord = 0.0;
double y_coord = 0.0;
double angle   = 0.0;

unsigned long last_aruco_read = 0;
unsigned long aruco_int = 5000;

const double ARENA_X = 4.0;
const double ARENA_Y = 2.0;

#define IN1 5
#define IN2 16
#define IN3 17
#define IN4 18
#define ENA 14
#define ENB 25

#define IN5 19
#define IN6 23
#define IN7 12
#define IN8 13
#define ENC 26
#define END 27

void pwm_set(int ch, double v) {
  int out = (int)(fabs(v) * 255.0);
  out = constrain(out, 0, 255);
  ledcWrite(ch, out);
}

void set_motor(int pinA, int pinB, int pwm_ch, double v) {
  if (v >= 0) {
    digitalWrite(pinA, HIGH);
    digitalWrite(pinB, LOW);
  } else {
    digitalWrite(pinA, LOW);
    digitalWrite(pinB, HIGH);
  }
  pwm_set(pwm_ch, v);
}

void mecanum(double vx, double vy, double w) {
  double FL = vx - vy - w;
  double FR = vx + vy + w;
  double RL = vx + vy - w;
  double RR = vx - vy + w;

  set_motor(IN1, IN2, 0, FL);
  set_motor(IN5, IN6, 2, FR);
  set_motor(IN3, IN4, 1, RL);
  set_motor(IN7, IN8, 3, RR);
}

void stop_motors() {
  mecanum(0, 0, 0);
}

void readArucoLine() {
  static char buf[200];
  if (!Serial.available()) return;
  size_t len = Serial.readBytesUntil('\n', buf, sizeof(buf)-1);
  buf[len] = '\0';
  if (len == 0) return;

  int scanned = 0;
  double tx, ty, ta;
  int tflag;
  scanned = sscanf(buf, "%lf %lf %lf %d", &tx, &ty, &ta, &tflag);
  if (scanned >= 3) {
    x_coord = tx;
    y_coord = ty;
    angle = ta;
    if (scanned == 4) mission_check = tflag;
    return;
  }

  if (strstr(buf, "START") != NULL) {
    mission_check = 1;
    return;
  }
  if (strstr(buf, "STOP") != NULL) {
    mission_check = 0;
    return;
  }
}

bool at_pos(double tx, double ty, double tol) {
  return fabs(x_coord - tx) < tol && fabs(y_coord - ty) < tol;
}

void orient() {
  if (angle > 0.2)  mecanum(0, 0, -0.2);
  else if (angle < -0.2) mecanum(0, 0, 0.2);
}

void wall_follow() {
  if (y_coord < ARENA_Y/2) mecanum(0.1, 0, 0);
  else mecanum(-0.1, 0, 0);
}

void cross_log() {
  mecanum(0.2, 0, 0);
}

double mission_y = 0;
double goal_y = 0;

void setup() {
  Serial.begin(115200);

  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(IN5, OUTPUT); pinMode(IN6, OUTPUT);
  pinMode(IN7, OUTPUT); pinMode(IN8, OUTPUT);

  ledcAttachPin(ENA, 0); ledcAttachPin(ENB, 1);
  ledcAttachPin(ENC, 2); ledcAttachPin(END, 3);
  ledcSetup(0, 20000, 8);
  ledcSetup(1, 20000, 8);
  ledcSetup(2, 20000, 8);
  ledcSetup(3, 20000, 8);

  stop_motors();
  Serial.println("OTV navigation booted. Send ArUco lines or 'START' to begin.");
}

unsigned long nowMillis() {
  return millis();
}

void loop() {
  if (mission_check != 1) {
    readArucoLine();
    return;
  }

  if (mission_phase == 0) {
    if (y_coord > ARENA_Y * 0.75) {
      mission_y = ARENA_Y * 0.25;
      goal_y = ARENA_Y * 0.90;
    } else {
      mission_y = ARENA_Y * 0.75;
      goal_y = ARENA_Y * 0.10;
    }
    mission_phase = 1;
    Serial.print("Mission phase 1. mission_y=");
    Serial.print(mission_y);
    Serial.print(" goal_y=");
    Serial.println(goal_y);
  }

  unsigned long now = nowMillis();
  if (now - last_aruco_read >= aruco_int) {
    readArucoLine();
    last_aruco_read = now;
    Serial.print("Aruco read: x=");
    Serial.print(x_coord, 3);
    Serial.print(" y=");
    Serial.print(y_coord, 3);
    Serial.print(" a=");
    Serial.print(angle, 3);
    Serial.print(" mission_check=");
    Serial.println(mission_check);
  }

  if (mission_phase == 1) {
    orient();
    wall_follow();
    if (x_coord > 3.0 && x_coord < 3.4) cross_log();

    double dx = 2.0 - x_coord;
    double dy = mission_y - y_coord;
    mecanum(dx * 0.3, dy * 0.3, 0);

    if (at_pos(2.0, mission_y, 0.15)) {
      stop_motors();
      delay(2000);
      mission_phase = 2;
      Serial.println("Arrived at mission site. Entering mission task phase.");
    }
  }

  if (mission_phase == 2) {
    Serial.println("Perform mission task (placeholder).");
    delay(3000);
    mission_phase = 3;
  }

  if (mission_phase == 3) {
    orient();
    double dx = 2.0 - x_coord;
    double dy = goal_y - y_coord;
    mecanum(dx * 0.3, dy * 0.3, 0);

    if (at_pos(2.0, goal_y, 0.15)) {
      stop_motors();
      Serial.println("Reached goal zone. Parking.");
      while (true) {
        delay(1000);
      }
    }
  }

  readArucoLine();
}
