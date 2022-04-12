import json
import requests
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError

info = requests.get('http://localhost:5000/chosen_apps')
apps_dict = info.json()
current_apps_dict = apps_dict.copy()
data = {}
average = {}
current_values = []

while True:

    info = requests.get('http://localhost:5000/chosen_apps')
    apps_dict = info.json()

    if apps_dict != current_apps_dict:

        current_apps_dict = apps_dict

    else:
        numbers = current_apps_dict.keys()

        for number in numbers:
            try:
                response = requests.get(current_apps_dict[number])
                data[number] = response.json()

            except ConnectionError:
                pass
            except JSONDecodeError:
                continue

        try:
            for app in data.values():
                for app_data in app.values():
                    for key, value in app_data.items():
                        try:
                            value = float(value)
                        except ValueError:
                            continue
                        else:
                            current_values.append(value)
        except KeyError:
            continue

        try:
            avg = sum(current_values)/len(current_values)
            current_values.clear()
        except ZeroDivisionError:
            avg = 0
            average['current_measurements_average'] = avg
        else:
            avg = avg.__round__(3)
            average['current_measurements_average'] = avg

        dict_message = json.dumps(average)
        requests.post('http://localhost:5000/aggregation', dict_message, headers={'content-type': 'application/json'})

