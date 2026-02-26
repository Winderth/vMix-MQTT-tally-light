import subprocess
from TCPSub_MQTTPub import main
import sys
import os
import argparse
import psutil

MOSQUITTO_PATH = r"C:\Program Files\Mosquitto"

MQTT_BROKER_PROCESS_NAME = r"mosquitto.exe"
MQTT_BROKER_CONFIGURATION = r"mosquitto.conf"


def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Mosquitto MQTT Broker server and TCP_MQTT bridge.")
    parser.add_argument("--mqtt_config", type=str, help=rf"A optional mosquitto.conf path. Default is {MOSQUITTO_PATH}\\{MQTT_BROKER_CONFIGURATION}")


    args = parser.parse_args()

    if (args.mqtt_config):
        MQTT_BROKER_CONFIGURATION = str(args.mqtt_config)

    if (process_exists(MQTT_BROKER_PROCESS_NAME)):
        # Kill process
        for proc in psutil.process_iter():
            try:
                if proc.name == MQTT_BROKER_PROCESS_NAME:
                    proc.kill()
            except Exception as e:
                print("Error:", e)
        


    mqttBrokerProcess = subprocess.Popen([f"{MOSQUITTO_PATH}\\{MQTT_BROKER_PROCESS_NAME}", "-c", f"{MOSQUITTO_PATH}\\{MQTT_BROKER_CONFIGURATION}"], stdout=subprocess.PIPE, text=True)

    

    # Run TCP_MQTT
    main()
