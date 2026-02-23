import network
from time import sleep


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("Scanning...")
networks = wlan.scan()
print("Available WiFi Networks:")
for ssid, bssid, channel, rssi, authmode, hidden in networks:
    print(f"SSID: {ssid.decode()}, BSSID: {bssid}, Channel: {channel}, RSSI: {rssi}, AuthMode: {authmode}, Hidden: {hidden}")