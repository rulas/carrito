import os
import sys
import time
import subprocess
import shlex

import adafruit_ads1x15.ads1115 as ADS
import board
import busio
import paho.mqtt.client as mqtt
import pexpect
from adafruit_ads1x15.analog_in import AnalogIn
from tenacity import retry,wait_fixed,retry_if_exception_type

BLE_DEVICE = "90:e2:02:be:49:cb"
POLL_TIME = .2
GAT_CMD = "sudo gatttool -b 90:E2:02:BE:49:CB --char-write-req --handle=0x0012 --value=0x123{}"
THRESHOLD = 2.0

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("carrito/sensor")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def pub_error(msg):
    client.publish("carrito/errors", msg)

def pub_sensor(val):
    client.publish("carrito/sensor", "{:>5.3f}".format(val))

@retry(wait=wait_fixed(3), retry=retry_if_exception_type(ValueError))
def initialize_sensor():
    chan = None
    print("Initializing sensor")
    try:
        # Create the I2C bus
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create the ADC object using the I2C bus
        ads = ADS.ADS1115(i2c)

        # Create single-ended input on channel 0
        chan = AnalogIn(ads, ADS.P0)
    # exc
    except ValueError as e:
        print("Error initializing sensor: %s" % e)
        pub_error("sensor init error: {}".format(str(e)))
        raise
    return chan

@retry(wait=wait_fixed(1))
def turn_gear(val):
    assert 1 <= val <= 5
    cmd = GAT_CMD.format(val)
    try:
        subprocess.run(shlex.split(cmd), check=True)
    except subprocess.CalledProcessError as e:
        # print("Error changing the gears: \ncode:{}\nstdout:{}\nstderr:".format(e.returncode, e.stdout, e.stderr))
        # print("Error changing the gears: \ncode:{}\nstdout:{}\nstderr:".format(e.returncode, e.stdout, e.stderr))
        pub_error("could not change gear to: {}".format(val))
        raise


# @retry(wait=wait_fixed(1), retry=retry_if_exception_type(OSError))
def read_sensor(chan):
    try:
        value, voltage = chan.value, chan.voltage
    except OSError as e:
        print("Error reading sensor, check the connection")
        pub_error("Error reading sensor to: {}".format(str(e)))
        raise

    return value, voltage

    
# Creates the mqtt client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect("localhost", 1883, 60)

chan = initialize_sensor()

print("{:>5}\t{:>5}".format('raw', 'v'))
is_on = False
turn_gear(1)


while True:
    try:
        value, voltage = read_sensor(chan)
    except OSError as e:
        print("Sensor is not working")
        turn_gear(1)
        is_on = False
        time.sleep(.3)
        continue
    print("{:>5}\t{:>5.3f}".format(value, voltage))
    pub_sensor(voltage)
    
    if is_on:
        if voltage < THRESHOLD:
            turn_gear(1)
            is_on = False
    else:
        if voltage >= THRESHOLD:
            turn_gear(5)
            is_on = True
        
    time.sleep(POLL_TIME)
