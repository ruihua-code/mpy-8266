import ujson


class WifiConfigFile:
    def __init__(self):
        self.file = 'wifi_config.json'

    def save(self, ssid, password):
        """保存WiFi配置到文件"""
        config = {
            "ssid": ssid,
            "password": password
        }
        with open(self.file, "w") as f:
            f.write(ujson.dumps(config))

    def read(self):
        """从文件读取WiFi配置"""
        try:
            with open(self.file, "r") as f:
                config = ujson.loads(f.read())
                return config["ssid"], config["password"]
        except Exception as e:
            print("Error reading WiFi config:", e)
            return None, None
