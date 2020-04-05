import sys
import os
import time
import extended_command
import mod_utils
import robot_util

try:
    from sphero_sdk import SpheroRvrObserver
    from sphero_sdk import RawMotorModesEnum
except ImportError:
    logging.critical("You need to install sphero-sdk-raspberrypi-python")
    logging.critical("Please install sphero-sdk-raspberrypi-python for python and restart this script.")
    logging.critical("To install: cd /usr/local/src && sudo git clone https://github.com/sphero-inc/sphero-sdk-raspberrypi-python")
    logging.critical("cd /usr/local/src/sphero-sdk-raspberrypi-python && sudo python setup.py install")
    logging.info("sphero_rvr running in test mode.")
    logging.info("Ctrl-C to quit")
    return
try:
    rvr = SpheroRvrObserver()
except:
    logging.critical("Unable to initialize Sphero SDK! Make sure you have the follow the Sphero SDK guide at https://github.com/sphero-inc/sphero-sdk-raspberrypi-python for setup!")
    logging.info("sphero_rvr running in test mode.")
    logging.info("Ctrl-C to quit")
    return

maxSpeed = 64
turnSpeed = 64
turnDelay = .4
heading = 0
delay = .5
init = False

def setup(robot_config):
    global delay
    global turnDelay
    global turnSpeed
    global maxSpeed
    try:
        delay = robot_config.getfloat('sphero_rvr', 'straight_delay')
        turnDelay = robot_config.getfloat('sphero_rvr', 'turn_delay')
        maxSpeed = robot_config.getfloat('sphero_rvr', 'directional_speed')
        turnSpeed = robot_config.getfloat('sphero_rvr', 'turn_speed')
    except:
        logging.critical("Config [sphero_rvr] not found! Please reset your controller.conf or copy sphero_rvr section from controller.sample.conf")
    if robot_config.getboolean('tts', 'ext_chat'): #ext_chat enabled, add motor commands
        extended_command.add_command('.speed', setSpeed)
        extended_command.add_command('.turn', setSpeed)
    rvr.wake()

def move(args):
    global turnSpeed
    global maxSpeed
    global turnDelay
    global heading
    command = args['button']['command']
    if command == 'l':
        turn(turnSpeed, 0, turnDelay) #spin left
    if command == 'r':
        turn(turnSpeed, 1, turnDelay) #spin right
    if command == 'f':
        drive(maxSpeed, 0, delay) #forwards
    if command == 'b':
        drive(maxSpeed, 1, delay) #backwards
    
    #decrease/increase linear speed
    if command == '+':
        maxSpeed = maxSpeed + 10
    if command == '-':
        maxSpeed = maxSpeed - 10
    
    #check and fix bounds
    if maxSpeed > 255:
        maxSpeed = 255
    elif maxSpeed < -255:
        maxSpeed = -255

    #decrease/increase turn speed
    if command == ']':
        turnSpeed = turnSpeed + 10
    if command == '[':
        turnSpeed = turnSpeed - 10

    #check and fix bounds
    if turnSpeed > 255:
        turnSpeed = 255
    elif turnSpeed < -255:
        turnSpeed = -255

def stop():
    #hard stop. Don't coast
    rvr.raw_motors(
        left_mode=1,
        left_speed=0,  # Valid speed values are 0-255
        right_mode=1,
        right_speed=0  # Valid speed values are 0-255
    )

def drive(speed, mode, delay):
    rvr.reset_yaw()
    # issue the driving command
    rvr.drive_with_heading(speed, 0, mode)

    # sleep for a {delay} seconds
    time.sleep(delay)
    stop()

def turn(turnSpeed, mode, turnDelay):
    leftMode = RawMotorModesEnum.off.value
    rightMode = RawMotorModesEnum.off.value
    if mode == 0: #left
        leftMode = RawMotorModesEnum.reverse.value
        rightMode = RawMotorModesEnum.forward.value
    if mode == 1: #right
        leftMode = RawMotorModesEnum.forward.value
        rightMode = RawMotorModesEnum.reverse.value
    rvr.raw_motors(
        left_mode=leftMode,
        left_speed=turnSpeed,  # Valid speed values are 0-255
        right_mode=rightMode,
        right_speed=turnSpeed  # Valid speed values are 0-255
    )
    time.sleep(turnDelay)
    stop()

def setSpeed(command, args):
    global turnSpeed
    global maxSpeed
    if extended_command.is_authed(args['sender']) == 2: # Owner
        if len(command) >= 2: 
            try:
                if command[0] == ".turn":
                    turnSpeed = int(command[1])
                if command[0] == ".speed":
                    maxSpeed = int(command[1])
            except:
                print ("Error in sphero_rvr.py:", sys.exc_info())
                pass
    