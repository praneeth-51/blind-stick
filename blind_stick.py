import RPi.GPIO as GPIO
import time
import os

# Left sensor
left_trigger = 2 #pin 3
left_echo = 3   #pin 5

# Right sensor
right_trigger = 14 #pin 8
right_echo = 15    #pin 10

# Front sensor
front_trigger = 23 #pin 16
front_echo = 24    # pin 18

# Variables
audio_speed = 1
max_range = 0.4  # meters

# Light and vibrator
light_pin = 17 # pin 11
vibrator_pin = 12 #pin 32

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)

GPIO.setup(left_trigger, GPIO.OUT)
GPIO.setup(left_echo, GPIO.IN)

GPIO.setup(right_trigger, GPIO.OUT)
GPIO.setup(right_echo, GPIO.IN)

GPIO.setup(front_trigger, GPIO.OUT)
GPIO.setup(front_echo, GPIO.IN)

GPIO.setup(light_pin, GPIO.OUT)
GPIO.setup(vibrator_pin, GPIO.OUT)


def announce(text):
    if text:
        os.system(f"pico2wave -w temp.wav -l en-US '{text}'")
        os.system(f"sox temp.wav -t alsa default tempo {audio_speed}")


def light(state):
    GPIO.output(light_pin, state)


def vibration(state):
    GPIO.output(vibrator_pin,state)

def getDistance(TRIG, ECHO):
    GPIO.output(TRIG, True)
    time.sleep(0.00001) # 10 micro sec delay
    GPIO.output(TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    timeout = time.time() + 0.1  # 100ms timeout for signal
    while GPIO.input(ECHO) == 0:
        start_time = time.time()
        if time.time() > timeout:
            return max_range  # Default safe distance if sensor fails

    timeout = time.time() + 0.1
    while GPIO.input(ECHO) == 1:
        stop_time = time.time()
        if time.time() > timeout:
            return max_range  # Default safe distance if sensor fails

    # Calculate distance
    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 200  # Speed of sound: 34300 cm/s

    return round(distance, 2)


try:
    while True:
        light(True)   # light on
        front_distance = getDistance(front_trigger, front_echo) #calculate the front sensor distance
        left_distance = getDistance(left_trigger, left_echo)  #calculate the left sensor distance
        right_distance = getDistance(right_trigger, right_echo)  # calculate the right sensor distance
        
        print(f"Distance [Left: {left_distance}m, Front: {front_distance}m, Right: {right_distance}m]")
        vibration(True)   # VIBRATION  ON

        messages = {   # conditions
            (False, False, False): "",
            (False, False, True): f"Object at right in {right_distance} meters", 
            (False, True, False): f"Object at front in {front_distance} meters",
            (False, True, True): "Take left",
            (True, False, False): f"Object at left in {left_distance} meters",
            (True, False, True): "Go straight",
            (True, True, False): "Take right",
            (True, True, True): "Go back",
        }

        key = (left_distance < max_range, front_distance < max_range, right_distance < max_range) # get conditions

        if key in messages:
            announce(messages[key]) ## announce the message
        light(False) # light off
        vibration(False) # vibration of
        time.sleep(1)  # Small delay to allow loop execution

except KeyboardInterrupt:
    print("Stopped by user")
    GPIO.cleanup()    # clean the gpio pins
