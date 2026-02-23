import socket
import threading
import time
from paho.mqtt import client as mqtt_client

import sys
import signal

# Configuration
VMIX_IP = '127.0.0.1'
VMIX_PORT = 8099
MQTT_BROKER = 'localhost'
MQTT_PORT = 1883
MQTT_TOPIC = 'vmix/tally'

vmix_thread = None
client_mqtt: mqtt_client.Client = None

# Variable to hold the current tally state
current_tally_state = []
state_lock = threading.Lock()
tally_state_condition = threading.Condition(state_lock)

# Variable to track connection state
connection_state: bool 
connection_state_lock = threading.Lock()

def signal_handler(sig, frame):
    if sig == signal.SIGINT:
        print("\n[System] Shutting down gracefully...")
        client_mqtt.disconnect()
        vmix_thread.join(timeout=1) 
        sys.exit(0)



def vmix_client_thread():
    """
    Function to handle the vMix TCP client connection, subscribe to tally updates, and update the current tally state.
    """
    global current_tally_state
    global connection_state
    
    while True:
        # Create a TCP socket and attempt to connect to vMix
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0) 
        
        connected = False
        try:
            print(f"[vMix] Trying to connect {VMIX_IP}:{VMIX_PORT}...")
            s.connect((VMIX_IP, VMIX_PORT))
            print("[vMix] Connected.")
            connected = True
            with connection_state_lock:
                connection_state = True
            
            # Sending SUBSCRIBE command to vMix to receive tally updates
            s.sendall(b'SUBSCRIBE TALLY\r\n')
            
            buffer = ""
            while True:
                try:
                    
                    # Receive data from vMix
                    data = s.recv(1024)
                    if not data:
                        print("[vMix] Server closed connection.")
                        break
                    
                    buffer += data.decode('utf-8')
                    
                    # Process complete lines in the buffer
                    while '\r\n' in buffer:
                        line, buffer = buffer.split('\r\n', 1)
                        
                        if line.startswith('TALLY OK'):
                            # Format: TALLY OK 01210...
                            parts = line.split(' ')
                            if len(parts) >= 3:
                                tally_string = parts[-1]
                                # Convert the tally string to a list of integers
                                new_state = [int(char) for char in tally_string]
                                
                                # Check if the state has changed and update the current tally state
                                with state_lock:
                                    state_changed = (new_state != current_tally_state)
                                    if state_changed:
                                        current_tally_state = new_state
                                        tally_state_condition.notify_all()
                                
                except socket.timeout:

                    continue
                except Exception as e:
                    print(f"[vMix] Error: {e}")
                    break

        except ConnectionRefusedError:
            print("[vMix] Cannot connect to vMix. Is it running?")
            with connection_state_lock:
                connection_state = False
        except Exception as e:
            with connection_state_lock:
                connection_state = False
            print(f"[vMix] General error: {e}")
        finally:
            if connected:
                s.close()
            # Wait before trying to reconnect
            time.sleep(3)

if __name__ == "__main__":
    # Start the vMix client thread
    vmix_thread = threading.Thread(target=vmix_client_thread, daemon=True)
    vmix_thread.start()
    

    client_mqtt = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2)
    client_mqtt.connect(MQTT_BROKER, MQTT_PORT)
    print(f"[MQTT] Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT}")
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        with tally_state_condition:
            tally_state_condition.wait(timeout=5.0)  # Wait for a state change or timeout
    
            for i, state in enumerate(current_tally_state):
                client_mqtt.publish(f"{MQTT_TOPIC}/{i}", str(state), qos=0)
                print(f"[MQTT] Published: {MQTT_TOPIC}/{i} = {state}")
    
    vmix_thread.join()

    
            