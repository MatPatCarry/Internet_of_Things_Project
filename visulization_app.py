import json
import requests
from bs4 import BeautifulSoup
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError

info = requests.get('http://localhost:5000/chosen_visualize')
apps_to_visualize_dict = info.json()
current_apps_to_visualize_dict = apps_to_visualize_dict.copy()
downloaded_data = {}
apps_numbers = {}
filtered_data = {}
avg_values = []

while True:

    filtered_apps = {}
    filtered_values = {}
    avg = {}

    info = requests.get('http://localhost:5000/chosen_visualize')
    apps_to_visualize_dict = info.json()

    if apps_to_visualize_dict != current_apps_to_visualize_dict:
        current_apps_to_visualize_dict = apps_to_visualize_dict
        avg_values.clear()

    for app, address in current_apps_to_visualize_dict.items():

        if address == 'http://127.0.0.1:5000/aggregation':
            try:
                response = requests.get(address)
                soup = BeautifulSoup(response.content, 'html5lib')
                get_div = soup.find('div', attrs={'class': 'div2'})
                result = get_div.find('b')

                try:
                    for element in ['<b>', '</b>']:
                        result = str(result).strip(element)
                    avg_values.append((str(len(avg_values) + 1) + ' measurement', float(result)))
                    filtered_data['Average value'] = avg_values.copy()
                except (TypeError, ValueError):
                    continue

            except ConnectionError:
                pass
            except JSONDecodeError:
                continue
        else:

            try:
                response = requests.get(address)
                downloaded_data[address] = response.json()

            except ConnectionError:
                pass
            except JSONDecodeError:
                continue

    try:
        for url, app in downloaded_data.items():
            app_measures = []
            for number, app_data in app.items():
                current_x_value = ''
                current_y_value = None
                for key, value in app_data.items():
                    if key in ['Station Name', 'date', 'Measurement Timestamp']:
                        current_x_value = value
                    elif key in ['Total Docks', 'temp', 'Air Temperature']:
                        current_y_value = value

                if current_x_value != '' and current_y_value is not None:
                    measure = (current_x_value, float(current_y_value))
                    app_measures.append(measure)

            if url == 'http://127.0.0.1:5000/nowy':
                title = 'Total Docks'

            if url == 'http://127.0.0.1:5000/temp':
                title = 'Temperature'

            if url == 'http://127.0.0.1:5000/locations':
                title = 'Air temperature'

            filtered_data[title] = app_measures.copy()

    except KeyError:
        continue

    filtered_data_message = json.dumps(filtered_data)
    requests.post('http://localhost:5000/visualize', filtered_data_message, headers={'content-type': 'application/json'})
    filtered_data.clear()
    downloaded_data.clear()