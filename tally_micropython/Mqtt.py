"""
This code is for a microcontroller (ESP32, Raspberry Pi Pico W, etc.) running MicroPython. 
It connects to a WiFi network, subscribes to an MQTT topic for tally light updates from vMix,
and controls a physical tally light based on the received messages.

If you want run program, you should install MicroPython on your device and ensure you have the 'umqtt.simple' library available.
"""

from machine import Pin, unique_id, reset
from utime import sleep
from umqtt.simple import MQTTClient
import network
import json

TALLY_LIGHT_PIN = 2  # Change to the correct pin for the tally light

tall_diode = Pin(TALLY_LIGHT_PIN, Pin.OUT)  


"""
To configure the device, create a 'setting.json' file in the same directory with the following content:
{
    "SSID": "your_wifi_ssid",
    "PASSWORD": "your_wifi_password",
    "MQTT_BROKER_IP": "your_mqtt_broker_ip",
    "MQTT_PORT": 1883,
    "MQTT_TALLY_TOPIC": "vmix/tally",
    "CAMERA_POSITION": "0" 
}
CAMERA_POSITION is the input of the tally light (0 for camera 1, 1 for camera 2, etc.) and will be used to subscribe to the correct MQTT topic.

CAMERA_POSITION 0 means input 1 in vMix, CAMERA_POSITION 1 means input 2 in vMix, and so on.
"""
with open('setting.json', 'r') as f:
    settings = json.load(f)
SSID = settings['SSID']
PASSWORD = settings['PASSWORD']
MQTT_BROKER_IP = settings['MQTT_BROKER_IP']
MQTT_PORT = settings['MQTT_PORT']
MQTT_TALLY_TOPIC = settings['MQTT_TALLY_TOPIC']
CAMERA_POSITION = settings['CAMERA_POSITION']  # Get the camera position from settings

id = unique_id().hex()

topic = f"{MQTT_TALLY_TOPIC}/{CAMERA_POSITION}"  # Create a topic specific to the camera position
client_id = f"vMixTallyClient_{CAMERA_POSITION}_{id}"  # Create a unique client ID for this camera position


def blink_tally_diode(times, delay):
    for _ in range(times):
        tall_diode.value(1)  # Turn on the tally diode
        sleep(delay)
        tall_diode.value(0)  # Turn off the tally diode
        sleep(delay)

def connect():
    wlan = network.WLAN(network.STA_IF)
    try:
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            print("Connecting to WiFi...")
            blink_tally_diode(1, 0.3) # Blink the tally diode to indicate connection attempt
            
        print("Connected to WiFi:", wlan.ifconfig())
    except Exception as e:
        print("Failed to connect to WiFi:", e)
        blink_tally_diode(3, 0.1)  # Blink the tally diode fast to indicate WiFi connection failure
        reset()  # Reset the device if WiFi connection fails
    return wlan

def mqtt_connect():
    try:
        print("Connecting to MQTT broker at", MQTT_BROKER_IP, ":", MQTT_PORT)
        client = MQTTClient(client_id, MQTT_BROKER_IP, port=MQTT_PORT)
        client.connect()
        print("Connected to MQTT broker")
        return client
    except Exception as e:
        print("Failed to connect to MQTT broker:", e)
        blink_tally_diode(1, 0.3)
        blink_tally_diode(2, 0.1)  # Blink the tally diode fast to indicate MQTT connection failure
        return None
    
def mqtt_sub_callback(topic, msg):
    print("Received MQTT message:", topic.decode(), msg.decode())
    
    if msg.decode() == "1":
        tall_diode.value(1)  
    else:
        tall_diode.value(0)  

wlan = connect()
mqtt_client = None
while not mqtt_client:
    mqtt_client = mqtt_connect()


if mqtt_client:
    mqtt_client.set_callback(mqtt_sub_callback)
    mqtt_client.subscribe(topic, qos=0)
    print(f"Subscribed to MQTT topic: {topic}")

while True:
    try:
        if not wlan.isconnected():
            print("WiFi connection lost. Reconnecting...")
            wlan = connect()    
        mqtt_client.check_msg()  # Check for new MQTT messages
    except Exception as e:
        print("Error checking MQTT messages:", e)
        mqtt_client = None
        while not mqtt_client:
            mqtt_client = mqtt_connect()
    
