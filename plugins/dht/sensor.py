#!/usr/bin/python
import time
import Adafruit_DHT
from influxdb import InfluxDBClient

sensor = Adafruit_DHT.DHT11
pin = 18

room = 'Salon'
client = InfluxDBClient(host='192.168.1.150', port=8086)
database = 'iotdb'
client.switch_database(database)

while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ")

    if not humidity or not temperature:
	continue

    data = [ 
    {
         "measurement": "sensors",
         "tags": {
             "room": room
         },
         "time": "{}".format(now),
         "fields": {
             "temperature": temperature,
             "humidity": humidity
         }
    }
    ]
    print data
    client.write_points(data)
    time.sleep(30)
