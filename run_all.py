import subprocess
from TCPSub_MQTTPub import main, set_kill_threads_flag
import sys
import os
import argparse
import psutil
import signal

MOSQUITTO_PATH = r"C:\Program Files\Mosquitto"

MQTT_BROKER_PROCESS_NAME = r"mosquitto.exe"
MQTT_BROKER_CONFIGURATION = r"mosquitto.conf"

mqttBrokerProcess = None


def signal_handler(sig, frame):
    if sig == signal.SIGINT:
        print("\n[System] Shutting down gracefully...")
        # Terminate the MQTT broker process
        if mqttBrokerProcess:
            mqttBrokerProcess.terminate()
            mqttBrokerProcess.wait()
            print("[System] MQTT broker process terminated.")
        # Set the flag to kill threads in TCPSub_MQTTPub
        set_kill_threads_flag(True)

def process_exists(process_name):
    for proc in psutil.process_iter():
        try:
            if proc.name() == process_name:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    """call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())
    """




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Mosquitto MQTT Broker server and TCP_MQTT bridge.")
    parser.add_argument("--mqtt_config", type=str, help=rf"A optional mosquitto.conf path. Default is {MOSQUITTO_PATH}\{MQTT_BROKER_CONFIGURATION}")
    args = parser.parse_args()

    if (args.mqtt_config):
        MQTT_BROKER_CONFIGURATION = str(args.mqtt_config)
    else:
        MQTT_BROKER_CONFIGURATION = rf"{MOSQUITTO_PATH}\{MQTT_BROKER_CONFIGURATION}"

    if (process_exists(MQTT_BROKER_PROCESS_NAME)):
        # Kill process
        for proc in psutil.process_iter():
            try:
                if proc.name() == MQTT_BROKER_PROCESS_NAME:
                    proc.kill()
                    print(f"[System] Existing {MQTT_BROKER_PROCESS_NAME} process killed with PID {proc.pid}.")
            except Exception as e:
                print("Error:", e)
        


    mqttBrokerProcess = subprocess.Popen([f"{MOSQUITTO_PATH}\\{MQTT_BROKER_PROCESS_NAME}", "-c", f"{MQTT_BROKER_CONFIGURATION}"], stdout=subprocess.PIPE, text=True)
    if mqttBrokerProcess:
        print(f"[System] MQTT broker started with PID {mqttBrokerProcess.pid}.")
    signal.signal(signal.SIGINT, signal_handler)
    

    # Run TCP_MQTT
    main()
