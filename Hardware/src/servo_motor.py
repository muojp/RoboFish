# -*- coding: utf-8 -*-
import FaBo9Axis_MPU9250
import RPi.GPIO as GPIO
import smbus
import random
import time
#GPIO init
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#-----Servo code-------------
#initialize
SERVOPIN = 23 #サーボは23Pinに接続
GPIO.setup(SERVOPIN,GPIO.OUT) #GPIOは出力に設定
servo = GPIO.PWM(SERVOPIN,50) #PWMを50Hzに設定
servo.start(10) #サーボを竿を下げた状態でスタート
def syakuri():
  for i in range(random.randint(1,3)): #しゃくりを1~3回で行う
    servo.ChangeDutyCycle(8.5) #竿が上がる方向にサーボを動かす
    time.sleep(0.15) #サーボが上がるまで待機
    servo.ChangeDutyCycle(10) #竿を下げる方向にサーボを動かす。
    time.sleep(1) #１回しゃくりをした後少し待機

#-----Motor code-------------
#initialize
HALL_SENSOR = 22 #ホールセンサを22Pinに接続
GPIO.setup( HALL_SENSOR, GPIO.IN ) #GPIOを入力に設定
bus = smbus.SMBus(1) #i2c通信を開始

# 指定した回転数になるまで回転数をカウント。
def count_rotation(num):
  i = 0
  while True:
    while GPIO.input( HALL_SENSOR ):
      pass
    while not GPIO.input( HALL_SENSOR ):
      pass
    i += 1
    if i >= num: break

# speedは0x1から0x3Aで指定
def forward(speed):
  cmd = 0x01 #モータを正転させるコマンド
  sval = cmd | ((speed+5)<<2) #スピードを設定して送信するデータを1Byte作成
  bus.write_i2c_block_data(0x64,0x00,[sval]) #生成したデータを送信

# speedは0x1から0x3Aで指定
def back(speed):
  cmd = 0x02 #モータを逆転させるコマンド
  sval = cmd | ((speed+5)<<2) #スピードを設定して送信するデータを1Byte作成
  bus.write_i2c_block_data(0x64,0x00,[sval]) #生成したデータを送信

def stop():
  bus.write_i2c_block_data(0x64,0x00,[0x00]) #モータへの電力の供給を停止(惰性で動き続ける)

def brake():
  bus.write_i2c_block_data(0x64,0x00,[0x03]) #モータをブレーキさせる

# モータを回して釣り糸を垂らす。
# (逆に巻かれたらbackをforwardにしてください)
def down(speed,rot):
  back(speed)
  count_rotation(rot)
  stop()
  brake()

# モータを回して釣り糸を巻く。
# (逆に垂らされたらforwardをbackにしてください)
def up(speed,rot):
  forward(speed)
  count_rotation(rot)
  stop()
  brake()

#-----Finalizer--------------
# 後始末(最後に必ず呼び出すこと)
def fin():
  servo.stop() #サーボを停止
  stop() #モータ停止
  bus.close() #i2c通信を閉じる

#============================
# サンプルコード

try:
  while True:
    print "Down"
    down(0x10,5) #糸を垂らす
    time.sleep(3) #3秒待つ
    print "Up"
    up(0x3f,5) #糸を巻く
    time.sleep(3) #3秒待つ
    print "Syakuri"
    syakuri() #しゃくりをする
    time.sleep(3) #3秒待つ
except KeyboardInterrupt:
  fin()
