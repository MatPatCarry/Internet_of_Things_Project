from flask import Flask, request, render_template
import json

app = Flask(__name__)

data = {}
avg_data = {}
filtered_data = {}
visualized_data = {}
chosen_apps_with_url = {}
chosen_apps_to_aggregate = {}
filter_data_settings = {}
visualize_data_settings = {}
on_off = ''

with open('configuration_file.json', 'r+') as config:
    conf = json.load(config)

settings = conf.copy()


@app.route("/", methods=['GET', 'POST'])
def home():
    global conf
    global settings
    global chosen_apps_with_url
    global chosen_apps_to_aggregate
    global filter_data_settings
    global visualize_data_settings
    message = ''

    if request.method == "POST":

        operation = request.form.get('operation')
        sensor_id = str(request.form.get('sensor_id'))

        if operation == 'new' and sensor_id not in settings.keys():
            settings[sensor_id] = {"protocol": "", "address": request.form['address'], "topic": "", "frequency": 0,
                                   "source": "", "on_off": "OFF"}

            message = f'Nowy czujnik ID: {sensor_id} został dodany! '

        elif operation == 'delete':
            del settings[sensor_id]

            message = f'Czujnik ID: {sensor_id} został usunięty! '

        elif operation == 'aggregate':

            chosen_apps_with_url = {}

            app1 = request.form.get('app1')
            app2 = request.form.get('app2')
            app3 = request.form.get('app3')
            chosen_apps = [app1, app2, app3]

            for id, app in enumerate(chosen_apps):

                if app == 'ok':
                    chosen_apps_with_url[str(id + 1)] = conf[str(id + 1)]['address']

            chosen_apps_to_aggregate = chosen_apps_with_url

        elif operation == 'filter':

            addresses_with_chosen_fields = {}
            first_app_address = request.form['app1_address']
            second_app_address = request.form['app2_address']
            third_app_address = request.form['app3_address']
            agg_data = request.form.get('data_from_agg')

            chosen_addresses = [first_app_address, second_app_address, third_app_address]

            if agg_data == 'yes':
                addresses_with_chosen_fields['http://127.0.0.1:5000/aggregation'] = ['current_measurements_average']

            for index, address in enumerate(chosen_addresses):
                if len(address) != 0:
                    if index == 0:
                        first_field_app1 = request.form.get('f_app1')
                        second_field_app1 = request.form.get('s_app1')
                        third_field_app1 = request.form.get('t_app1')

                        addresses_with_chosen_fields[address] = [first_field_app1, second_field_app1, third_field_app1]
                    elif index == 1:
                        first_field_app2 = request.form.get('f_app2')
                        second_field_app2 = request.form.get('s_app2')
                        third_field_app2 = request.form.get('t_app2')
                        addresses_with_chosen_fields[address] = [first_field_app2, second_field_app2, third_field_app2]
                    else:
                        first_field_app3 = request.form.get('f_app3')
                        second_field_app3 = request.form.get('s_app3')
                        third_field_app3 = request.form.get('t_app3')
                        addresses_with_chosen_fields[address] = [first_field_app3, second_field_app3, third_field_app3]

            filter_data_settings = addresses_with_chosen_fields

        elif operation == 'visualization':
            chosen_apps_to_visualize = {}

            app1 = request.form.get('app1_v')
            app2 = request.form.get('app2_v')
            app3 = request.form.get('app3_v')
            aggregator = request.form.get('aggregator_v')
            filter_app = request.form.get('filter_v')

            auxiliary_chosen_apps_to_visualise = [app1, app2, app3]

            if aggregator == 'ok':
                chosen_apps_to_visualize['aggregator'] = 'http://127.0.0.1:5000/aggregation'

            if filter_app == 'ok':
                chosen_apps_to_visualize['filter'] = 'http://127.0.0.1:5000/filter'

            for id, app in enumerate(auxiliary_chosen_apps_to_visualise):

                if app == 'ok':
                    chosen_apps_to_visualize[str(id + 1)] = conf[str(id + 1)]['address']

            visualize_data_settings = chosen_apps_to_visualize

        else:
            try:

                settings[sensor_id]['protocol'] = request.form['protocol']
                settings[sensor_id]['address'] = request.form['address']
                settings[sensor_id]['topic'] = request.form['broker_topic']
                settings[sensor_id]['frequency'] = request.form['frequency']
                settings[sensor_id]['source'] = request.form['source']
                settings[sensor_id]['on_off'] = request.form.get('on_off')

                for key in (settings[sensor_id]).keys():

                    if key == "protocol":

                        settings[sensor_id][key] = (settings[sensor_id][key]).upper()

                        if settings[sensor_id][key] not in ['HTTP', 'MQTT']:
                            settings[sensor_id][key] = conf[sensor_id][key]

                    if key == "address":

                        if len(settings[sensor_id][key]) == 0:
                            settings[sensor_id][key] = conf[sensor_id][key]

                    if key == 'topic' and settings[sensor_id]['protocol'] == 'MQTT':

                        if settings[sensor_id][key] == '':
                            settings[sensor_id][key] = conf[sensor_id][key]

                    if key == 'frequency':
                        try:
                            settings[sensor_id][key] = float(settings[sensor_id][key])
                        except ValueError:
                            settings[sensor_id][key] = conf[sensor_id][key]
                        else:
                            if settings[sensor_id][key] <= 0:
                                settings[sensor_id][key] = conf[sensor_id][key]

                    if key == "source":
                        if settings[sensor_id][key] not in ['Array_of_Things_Locations.csv',
                                                            'Beach_Weather_Stations_-_Automated_Sensors.csv',
                                                            'Divvy_Bicycle_Stations.csv', 'temp-data-2019.csv',
                                                            'Wearables-DFE.csv']:
                            settings[sensor_id][key] = conf[sensor_id][key]

                    if key == 'on_off':
                        if settings[sensor_id][key] not in ['ON', 'OFF']:
                            settings[sensor_id][key] = conf[sensor_id][key]

                        else:
                            if settings[sensor_id][key] == "ON":
                                message = f'Czujnik ID: {sensor_id} jest teraz aktywny! '
                            elif settings[sensor_id][key] == "OFF":
                                message = f'Czujnik ID: {sensor_id} jest teraz nieaktywny! '

            except KeyError:
                return "", 404

        with open('configuration_file.json', 'w+') as config:
            json.dump(settings, config)

        with open('configuration_file.json', 'r+') as next_config:
            conf = json.load(next_config)

    return render_template("configuration.html", message=message)


@app.route("/configuration_data", methods=['GET'])
def return_config():
    global conf

    if request.method == "GET":
        return conf


@app.route("/chosen_apps", methods=['GET'])
def chosen_apps():
    global chosen_apps_to_aggregate

    if request.method == "GET":
        return chosen_apps_to_aggregate


@app.route('/chosen_fields', methods=['GET'])
def chosen_fields():
    global filter_data_settings

    if request.method == "GET":
        return filter_data_settings


@app.route('/chosen_visualize', methods=['GET'])
def chosen_visualize():
    global visualize_data_settings

    if request.method == 'GET':
        return visualize_data_settings


@app.route('/<url>', methods=['GET', 'POST'])
def data_page(url):
    if url == 'favicon.ico':
        return '', 404

    if request.method == "POST":

        try:
            info = request.get_json()
            data[url] = info
            return '', 200

        except Exception as E:
            print(E)
            return "", 404

    if request.method == 'GET':
        try:
            return data[url], 200

        except KeyError:
            return '', 404


@app.route('/aggregation', methods=['GET', 'POST'])
def average():
    global avg_data

    if request.method == "POST":

        try:
            avg_data = request.get_json()
            return '', 200

        except Exception as E:
            print(E)
            return "", 404

    if request.method == 'GET':
        try:
            return render_template("aggregation.html", avg_data=avg_data)

        except KeyError:
            return '', 404


@app.route('/filter', methods=['GET', 'POST'])
def filtering_data():
    global filtered_data

    if request.method == "POST":

        try:
            filtered_data = request.get_json()
            return '', 200

        except Exception as E:
            print(E)
            return "", 404

    if request.method == 'GET':
        try:
            return filtered_data, 200

        except KeyError:
            return '', 404


@app.route('/visualize', methods=['GET', 'POST'])
def visualize_data():
    global visualized_data
    global visualize_data_settings

    if request.method == "POST":

        try:
            visualized_data = request.get_json()
            return '', 200

        except Exception as E:
            print(E)
            return "", 404

    if request.method == 'GET':
        labels = []
        values = []
        titles = []
        addresses = []

        try:
            for title, data in visualized_data.items():
                label = []
                value = []
                for c_label, c_value in data:
                    label.append(c_label)
                    value.append(c_value)

                labels.append(label)
                values.append(value)
                title_to_add = "'" + str(title) + "'"
                titles.append(title_to_add.upper())

            length = int(len(titles))

            try:
                for id, address in visualize_data_settings.items():
                    addresses.append(address)
            except KeyError:
                pass

        except KeyError:
            return '', 404

        return render_template('visualization.html', labels=labels, values=values, titles=titles, length=length,
                               addresses=addresses)


if __name__ == '__main__':
    app.run(debug=True)
