import network
from zrh_server import ZrhSocket


class ZrhAp:
    def __init__(self):
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid='zrh_esp_ap',
                       authmode=network.AUTH_WPA_WPA2_PSK, password='zrh123456')
        while self.ap.active() == False:
            pass
        print("AP started")
        print(self.ap.ifconfig())

    def start_server(self):
        zrhSocket = ZrhSocket()
        zrhSocket.start()
