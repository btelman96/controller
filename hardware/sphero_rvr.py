import sys
import os

import asyncio

from sphero_sdk import SerialAsyncDal
from sphero_sdk import SpheroRvrAsync

current_key_code = -1
driving_keys = [119, 97, 115, 100, 32]
maxSpeed = 64
speed = 0
heading = 0
flags = 0
delay = .5

loop = asyncio.get_event_loop()
rvr = SpheroRvrAsync(
    dal=SerialAsyncDal(
        loop
    )
)

def keycode_callback(keycode):
    global current_key_code
    current_key_code = keycode
    print("Key code updated: ", str(current_key_code))

def move(args):
    global speed
    global current_key_code
    global heading
    command = args['button']['command']
    if command == 'l':
        keycode_callback(97) # A
    if command == 'r':
        keycode_callback(100) # D
    if command == 'f':
        keycode_callback(119) # W
    if command == 'b':
        keycode_callback(115) # S
    if command == '+':
        maxSpeed += 64
    if command == '-':
        maxSpeed -= 64
    if maxSpeed > 255:
        maxSpeed = 255
    elif maxSpeed < -255:
        maxSpeed = -255
    global loop
    loop.run_until_complete(
        asyncio.gather(
            runSingleLoop()
        )
    )

async def main():
    """
    Runs the main control loop for this demo.  Uses the KeyboardHelper class to read a keypress from the terminal.

    W - Go forward.  Press multiple times to increase speed.
    A - Decrease heading by -10 degrees with each key press.
    S - Go reverse. Press multiple times to increase speed.
    D - Increase heading by +10 degrees with each key press.
    Spacebar - Reset speed and flags to 0. RVR will coast to a stop

    """
    global current_key_code
    global speed
    global maxSpeed
    global heading
    global flags
    global delay

    await rvr.wake()

    await rvr.reset_yaw()

async def runSingleLoop():
    if current_key_code == 119:  # W
        speed = maxSpeed
        # go forward
        flags = 0
    elif current_key_code == 97:  # A
        heading -= 10
    elif current_key_code == 115:  # S
        speed = maxSpeed
        # go reverse
        flags = 1
    elif current_key_code == 100:  # D
        heading += 10
    elif current_key_code == 32:  # SPACE
        # reset speed and flags, but don't modify heading.
        speed = 0
        flags = 0

    # check the speed value, and wrap as necessary.
    if speed > 255:
        speed = 255
    elif speed < -255:
        speed = -255

    # check the heading value, and wrap as necessary.
    if heading > 359:
        heading = heading - 359
    elif heading < 0:
        heading = 359 + heading

    # reset the key code every loop
    current_key_code = -1

    # issue the driving command
    await rvr.drive_with_heading(speed, heading, flags)

    # sleep for a .5 seconds
    await asyncio.sleep(delay)

    await rvr.drive_with_heading(0, heading, 0) #full stop

def run_init():
    global loop
    loop.run_until_complete(
        asyncio.gather(
            main()
        )
    )

def setup(robot_config):
    global speed
    global heading
    global flags
    global delay
    delay = robot_config.getfloat('robot', 'straight_delay')
    try:
        run_init()
    except KeyboardInterrupt:
        print("Keyboard Interrupt...")
    