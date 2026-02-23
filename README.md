# vMix MQTT tally light

vMix MQTT tally light is an application written in Python that retrieves information about the status of indicator lights from vMix using the TCP API and publishes this information via the MQTT protocol. 

## Repository 
The source code contain *TCPSub_MQTTPub.py* script, which is responsible for connecting to the vMix TCP API, retrieving the status of the tally lights, and publishing this information to an MQTT broker. The script uses the `paho-mqtt` library for MQTT communication and the `socket` library for TCP communication.

Folder *tally_micropython* contains a MicroPython script that can be run on a microcontroller to subscribe to the MQTT topics published by the main script and control physical tally light accordingly.

## Usage of TCPSub_MQTTPub.py
To use the vMix MQTT tally light, follow these steps:
1. Install and run MQTT broker (e.g. Mosquitto) on your machine.
2. Run vMix and ensure that the TCP API is enabled and configured correctly.
3. Install the required Python libraries using pip:
   ```
   pip install paho-mqtt
   ```
4. Configure the TCP connection to the vMix API and the MQTT broker settings in the *TCPSub_MQTTPub.py* script.
5. Run the *TCPSub_MQTTPub.py* script.

## Usage of MicroPython script
To use the MicroPython script for controlling the tally light, follow these steps:
1. Flash the MicroPython firmware onto your microcontroller (e.g. ESP32 or Raspberry Pi Pico 2W).
2. Install the required MicroPython library 'umqtt.simple' on your microcontroller.
3. Configure the MQTT broker settings in the MicroPython script.
4. Upload the MicroPython script to your microcontroller and run it.
