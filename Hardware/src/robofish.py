# -*- coding: utf-8 -*- 
import smbus
import time
import threading
import RPi.GPIO as GPIO
import sys

## DRV8830 Default I2C slave address
SLAVE_ADDRESS  = 0x64

''' DRV8830 Register Addresses '''
## sample rate driver
CONTROL = 0x00

## Value motor.
FORWARD = 0x01
BACK = 0x02
STOP = 0x00

## Value of hall sensor.
HALL_SENSOR = 22 #ホールセンサを22Pinに接続
## Value of servo.
SERVO_PIN = 23 #サーボは23Pinに接続
#PWMを50Hzに設定
PWM_HZ = 50

## smbus
bus = smbus.SMBus(1)

class Robot(threading.Thread):   
    flg = True
    myServo = ""
#class Robot():   
    def __init__(self, address=SLAVE_ADDRESS): 
        self.address = address
        self.c = 0
        threading.Thread.__init__(self)
        print "init"
       
        self.flg = True
      
    def run(self):
        print "run"
        self.count()
    
    def rod_move(self, angle):
        angle = self.map(angle, 0,180,2,12.5)
        print angle
        self.myServo.ChangeDutyCycle(angle)
    
    def refresh(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(HALL_SENSOR, GPIO.IN) #GPIOを入力に設定
        GPIO.setup(SERVO_PIN , GPIO.OUT) #GPIOを入力に設定
        self.myServo = GPIO.PWM(SERVO_PIN ,PWM_HZ) 
        self.myServo.start(10)

    def rod_stop(self):
        print "rod_stop"
        self.myServo.stop()
        GPIO.cleanup()
    
    def map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def get_reel_count(self):
        return self.c
    
    def reset_reel_count(self):
        self.c = 0
    
    # 指定した回転数になるまで回転数をカウント。
    def count(self):
        while self.flg:
            while GPIO.input( HALL_SENSOR ):
                pass
            while not GPIO.input( HALL_SENSOR ):
                pass
            if self.direction == FORWARD:
                self.c += 1
            elif self.direction == BACK:
                self.c -= 1
            #sys.stdout.write("\rcount %d   " % self.c)
            #sys.stdout.flush()
            time.sleep(0.01)
                      
    # speedは1-100で指定
    def reel_forward(self, speed):
        if speed < 0:
            print "value is over 1,  must define 1-100 as speed."
            return
        elif speed > 100:
            print "value is under 100,  must define 1-100 as speed."
            return
        self.direction = FORWARD
        s = self.map(speed, 1, 100, 1, 58)
        sval = FORWARD | ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        bus.write_i2c_block_data(self.address,CONTROL,[sval]) #生成したデータを送信

    def reel_stop(self):
        bus.write_i2c_block_data(self.address,CONTROL,[STOP]) #モータへの電力の供給を停止(惰性で動き続ける)
        
    # speedは0-100で指定
    def reel_back(self, speed):
        if speed < 0:
            print "value is over 1,  must define 1-100 as speed."
            return
        elif speed > 100:
            print "value is under 100,  must define 1-100 as speed."
            return
        self.direction = BACK
        s= self.map(speed, 1, 100, 1, 58)
        sval = BACK| ((s+5)<<2) #スピードを設定して送信するデータを1Byte作成
        bus.write_i2c_block_data(self.address,CONTROL,[sval]) #生成したデータを送信

    def reel_brake(self):
        bus.write_i2c_block_data(self.address,CONTROL,[0x03]) #モータをブレーキさせる
        