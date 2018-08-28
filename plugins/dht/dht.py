#!/usr/bin/python
import os
import time
import yaml
import Adafruit_DHT
from influxdb import InfluxDBClient

CONFIG_FILE = "/etc/sensors/dht.yml"
CONFIG = {}
CLIENT = None
ONLINE = True
OFFLINE_DB = "/var/run/sensors/dht_measurements.yml"

MAX_REFRESH = {
    11: 1,
    22: 2
}

def configure():
    CONFIG = {
        'sensor': {
            'name': 'dht',
            'model_number': 11,
            'pin': None,
            'location': 'Unknown',
            'refresh_rate': 1
        },
        'influxdb': {
            'host': '127.0.0.1',
            'port': 8086,
            'auth': {
                'username': None,
                'password': None
            },
            'database': 'db',
            'measurement': 'sensors'
        }
    }

    with open(CONFIG_FILE, 'r') as stream:
        config = yaml.load(stream)

    CONFIG.update(config)

    if MAX_REFRESH[CONFIG['sensor']['model_number']] > CONFIG['sensor']['refresh_rate']:
        CONFIG['sensor']['refresh_rate'] = MAX_REFRESH[CONFIG['sensor']['model_number']]
        print("[WARN] Your refresh rate is too high for this model: set to default")
    
    CLIENT = InfluxDBClient(host=CONFIG['influxdb']['host'], port=CONFIG['influxdb']['port'], user=CONFIG['influxdb']
                    ['auth']['username'], password=CONFIG['influxdb']['auth']['password'], database=CONFIG['influxdb']['database'])


def get_mesure():
    humidity, temperature = Adafruit_DHT.read(
        CONFIG['sensor']['model_number'], CONFIG['sensor']['pin'])

    if not humidity or not temperature:
        time.sleep(MAX_REFRESH[CONFIG['sensor']['model_number']])
        return get_mesure

    # Glitch fix
    if humidity > 100:
        time.sleep(MAX_REFRESH[CONFIG['sensor']['model_number']])
        return get_mesure

    return humidity, temperature


def send_mesure(humidity, temperature):  
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    data = []

    if not ONLINE:
        with open(OFFLINE_DB, 'r') as stream:
            data = yaml.load(stream)

    data.push({
            "measurement": CONFIG['influxdb']['measurement'],
            "tags": {
                "location": CONFIG['sensor']['location'],
                "name": CONFIG['sensor']['name']
            },
            "time": "{}".format(now),
            "fields": {
                "temperature": temperature,
                "humidity": humidity
            }
        })

    if CLIENT.write_points(data):
        if not ONLINE and os.path.exists(OFFLINE_DB):
            os.remove(OFFLINE_DB)
        ONLINE = True
    else:
        ONLINE = False
        with open(OFFLINE_DB, 'w') as db:
            yaml.dump(data, db)
    
    


def main():
    configure()

    while True:

        humidity, temperature = get_mesure()
        send_mesure(humidity, temperature)
        time.sleep(CONFIG['sensor']['refresh_rate'])

if __name__ == "__main__":
    main()
