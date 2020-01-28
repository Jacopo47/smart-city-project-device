import Adafruit_DHT
import time
import sys
import os
from walrus import Database

DHT11 = Adafruit_DHT.DHT11
DHT11_PIN = 21  # use of pin BCM numeration

if len(sys.argv) < 4:
    print("Please specify all arguments! Required:\n zone;\n device name;\n lat;\n long;")
    exit(1)

zone = sys.argv[1]
device_name = sys.argv[2]
lat = sys.argv[3]
long = sys.argv[4]

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", "6379"))
redis_pw = os.getenv("REDIS_PW", "NONE")


def redis_connection():
    if redis_pw == "NONE":
        return Database(host=redis_host, port=redis_port, db=0)
    else:
        return Database(host=redis_host, port=redis_port, db=0, auth=redis_pw)


while True:
    humidity, temperature = Adafruit_DHT.read_retry(DHT11, DHT11_PIN, retries=2, delay_seconds=1)

    if humidity is not None and temperature is not None:
        print('Temperature={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
        stream = redis_connection().Stream("sensor:stream")
        value = {
            'zone': zone,
            'name': device_name,
            'temperature': temperature,
            'humidity': humidity,
            'latitude': lat,
            'longitude': long
        }
        print(stream.add(value))
    else:
        print('Sensor read error... retry!!!')
    time.sleep(20)
