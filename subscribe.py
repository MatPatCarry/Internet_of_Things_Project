import paho.mqtt.client as mqtt
import requests
import json


client_sub = mqtt.Client("C3")

with open('//app2/conf2.json') as cf:
    settings = json.load(cf)


def on_message(client, userdata, msg):
    mess = msg.payload.decode("utf-8")
    print(mess)


sensor_id = "2"

try:
    broker = settings['config']["address"]
    subject = settings['config']["topic"]

    client_sub.connect(broker)
    client_sub.subscribe(subject)
    client_sub.on_message = on_message
    client_sub.loop_forever()

except IndexError:
    print("Incorrect input")
