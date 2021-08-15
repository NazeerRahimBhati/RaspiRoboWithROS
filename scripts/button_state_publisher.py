#!/usr/bin/env python

import rospy
from std_msgs.msg import String

import RPi.GPIO as GPIO
import time

GPIO.setmode (GPIO.BCM)
GPIO.setwarnings (False)

# Define GPIO pins of motors
en1=2
in1=3
in2=4
en2=17
in3=27
in4=22

GPIO.setup (en1, GPIO.OUT)
GPIO.setup (en2, GPIO.OUT)
GPIO.output (en1, 1)
GPIO.output (en2, 1)

class Motor:
    def __init__ (self, pinFwd, pinBack, frequency=20, maxSpeed=100):
        #  Configure GPIO
        GPIO.setup (pinFwd,  GPIO.OUT)
        GPIO.setup (pinBack, GPIO.OUT)

        #  get a handle to PWM
        self._frequency = frequency
        self._maxSpeed = maxSpeed
        self._pwmFwd  = GPIO.PWM (pinFwd,  frequency)
        self._pwmBack = GPIO.PWM (pinBack, frequency)
        self.stop()

    def forwards (self, speed):
        self.move (speed)

    def backwards (self, speed):
       self.move (-speed)

    def stop (self):
        self.move (0)

    def move (self, speed):
        #  set limits
        if speed > self._maxSpeed:
            speed = self._maxSpeed
        if speed < -self._maxSpeed:
            speed = -self._maxSpeed
        #  turn on the motors
        if speed < 0:
            self._pwmFwd.start(0)
            self._pwmBack.start(-speed)
        else:
            self._pwmFwd.start(speed)
            self._pwmBack.start(0)

class Wheelie:
    def __init__ (self):
        self.rightWheel = Motor (in2, in1)
        self.leftWheel = Motor (in3, in4)

    def stop (self):
        self.leftWheel.stop()
        self.rightWheel.stop()

    def goForward (self, speed = 100):
        self.rightWheel.forwards (speed)
        self.leftWheel.forwards (speed)

    def goBackward (self, speed = 100):
        self.rightWheel.backwards (speed)
        self.leftWheel.backwards (speed)
    
    def goLeft (self, speed = 100):
        self.rightWheel.backwards (speed)
        self.leftWheel.forwards (speed)

    def goRight (self, speed = 100):
        self.rightWheel.forwards (speed)
        self.leftWheel.backwards (speed)



class MinimalSubscriber():
    def __init__(self):
        self.subscription = rospy.Subscriber('move', String, self.listener_callback)
        self.subscription  # prevent unused variable warning
        self.wheelie = Wheelie()

    def listener_callback(self, msg):
        command = msg.data
        if command == 'forward':
            print('Moving forward')
            self.wheelie.goForward()
        elif command == 'backward':
            print('Moving backward')
            self.wheelie.goBackward()
        elif command == 'left':
            print('Turning left')
            self.wheelie.goBackward()
        elif command == 'right':
            print('Turning right')
            self.wheelie.goRight()
        elif command == 'stop':
            print('Stopping')
            self.wheelie.stop()
        else:
            print('Unknown command, stopping instead')
            self.wheelie.stop()

def main():
    #  initialize the wheelie node
    rospy.init_node('Node', anonymous = True)
    minimal_subscriber = MinimalSubscriber()

    #  wait for incoming commands
    rospy.spin()

    #  Interrupt detected, shut down
    minimal_subscriber.wheelie.stop()
    GPIO.cleanup()
    minimal_subscriber.destroy_node()
    rospy.shutdown()


if __name__ == '__main__':
    main()





