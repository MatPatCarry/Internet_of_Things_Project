import json
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError


info = requests.get('http://localhost:5000/chosen_fields')
fields_dict = info.json()
current_fields_dict = fields_dict.copy()
downloaded_data = {}
apps_numbers = {}
filtered_data = {}

while True:

    filtered_apps = {}
    filtered_values = {}
    avg = {}
    info = requests.get('http://localhost:5000/chosen_fields')
    fields_dict = info.json()

    if fields_dict != current_fields_dict:
        current_fields_dict = fields_dict

    for address, fields in current_fields_dict.items():

        if address == 'http://127.0.0.1:5000/aggregation':
            try:
                response = requests.get(address)
                soup = BeautifulSoup(response.content, 'html5lib')
                get_div = soup.find('div', attrs={'class': 'div2'})
                result = get_div.find('b')

                try:
                    for element in ['<b>', '</b>']:
                        result = str(result).strip(element)
                    avg['current_measurements_average'] = result
                    filtered_data['aggregation_app'] = avg.copy()
                except TypeError:
                    continue

            except ConnectionError:
                pass
            except JSONDecodeError:
                continue

        try:
            response = requests.get(address)
            downloaded_data[address] = response.json()

        except ConnectionError:
            pass
        except JSONDecodeError:
            continue

    try:
        for url, app in downloaded_data.items():
            for number, app_data in app.items():
                for key, value in app_data.items():
                    if key in current_fields_dict[url]:
                        filtered_values[key] = value
                filtered_apps[number] = filtered_values.copy()
            filtered_data[url] = filtered_apps.copy()
            filtered_values.clear()
            filtered_apps.clear()
    except KeyError:
        continue

    filtered_data_message = json.dumps(filtered_data)
    requests.post('http://localhost:5000/filter', filtered_data_message, headers={'content-type': 'application/json'})
    filtered_data.clear()
    downloaded_data.clear()
