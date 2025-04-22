import network
import time
from zrh_server import ZrhSocket
from zrh_wifi_config import WifiConfigFile
from zrh_ap import ZrhAp


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    wifiConfigFile = WifiConfigFile()
    ssid, password = wifiConfigFile.read()
    print("wifi config:", ssid, password)
    if ssid is not None:
        wlan.connect(ssid, password)

connectCount = 0
while not wlan.isconnected():
    print("connecting...")
    connectCount += 1
    time.sleep(1)
    if connectCount > 10:
        print("connect timeout")
        zrhAp = ZrhAp()
        zrhAp.start_server()
        break
    if wlan.isconnected():
        print("connect success:", wlan.ifconfig())

server = ZrhSocket()
server.start()
