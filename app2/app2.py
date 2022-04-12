import json
import time
import paho.mqtt.client as mqtt
import pandas as pd
import requests

path = 'conf2.json'


def service():

    with open(path) as cf:
        settings = json.load(cf)

    return settings


settings_data = service()

sensor_id = settings_data['ID']
sensor_config = settings_data['config']

with open('../csv_files/' + str(sensor_config["source"]), encoding="utf-8") as file:
    df = pd.read_csv(file)


def posting_data(settings):

    protocol = settings["protocol"]
    address = settings["address"]
    broker_topic = settings['topic']
    frequency = settings["frequency"]
    on_off = settings['on_off']

    if on_off == 'OFF':

        while True:

            response = requests.get('http://localhost:5000/configuration_data')
            data_dict = response.json()

            if sensor_id in data_dict.keys():

                if data_dict[sensor_id]['on_off'] == "OFF":
                    continue

                else:
                    break

    hel = []

    cols = df.columns
    columns = list(cols)
    data = {}
    json_data = {}

    if protocol == "MQTT":

        client = mqtt.Client("C1")
        client.connect(address)
        client.loop_start()

        while True:

            response = requests.get('http://localhost:5000/configuration_data')
            data_dict = response.json()

            if data_dict[sensor_id]['on_off'] == 'OFF':
                continue

            else:

                col1, col2 = columns[0:2]
                col3 = columns[-2]

                data[col1] = str(df[col1][len(hel)])
                data[col2] = str(df[col2][len(hel)])
                data[col3] = str(df[col3][len(hel)])

                hel.append(data)

                json_data[len(hel)] = data.copy()
                display = json.dumps(json_data)

                client.publish(broker_topic, payload=display)

                if sensor_id in data_dict.keys():

                    with open(path, 'w+') as new_config:

                        new_configuration_data = data_dict[sensor_id]
                        json.dump({"ID": sensor_id, "config": new_configuration_data}, new_config)

                    if data_dict[sensor_id] != settings:
                        return False

                time.sleep(frequency)

    elif protocol == "HTTP":

        while True:

            response = requests.get('http://localhost:5000/configuration_data')
            data_dict = response.json()

            if sensor_id in data_dict.keys():

                if data_dict[sensor_id]['on_off'] == 'OFF':
                    continue

                else:

                    col1, col2, col3 = columns[2:]

                    data[col1] = str(df[col1][len(hel)])
                    data[col2] = str(df[col2][len(hel)])
                    data[col3] = str(df[col3][len(hel)])

                    hel.append(data)

                    json_data[len(hel)] = data.copy()
                    display = json.dumps(json_data)

                    requests.post(address, display, headers={'content-type': 'application/json'})

                    if sensor_id in data_dict.keys():

                        with open(path, 'w+') as new_config:

                            new_configuration_data = data_dict[sensor_id]
                            json.dump({"ID": sensor_id, "config": new_configuration_data}, new_config)

                        if data_dict[sensor_id] != settings:
                            return False

                    time.sleep(frequency)


while True:

    if not posting_data(sensor_config):

        settings_data = service()
        sensor_config = settings_data['config']

        with open('../csv_files/' + str(sensor_config['source']), encoding="utf-8") as file:
            df = pd.read_csv(file)


