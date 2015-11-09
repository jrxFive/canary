'''HTTP GET Requests to retrieve timeseries data from different backends'''

import requests
import falcon
import json

class AvailableBackends(object):
    '''Falcon resource to return json list containing all possible backends'''

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(get_backends())

def backend_influxdb(influx_params):
    '''
        Pull timeseries data from influxdb REST API

        :param influx_params: Dictionary containing influxdb connection info.
        :type influx_params: dict

        :returns: tuple containing a 2d array of timeseries data, the timeseries index, and the value index

        Fields:

        - protocol - http or https
        - host     - address of the influxdb server
        - port     - port the influxdb instance is listening on
        - database - name of the influxdb database
        - series   - name of the database series
        - epoch    - epoch format for timestamp
    '''

    if 'protocol' not in influx_params:
        influx_params['protocol'] = 'http'

    url = "{protocol}://{host}:{port}/query".format(
        protocol=influx_params['protocol'],
        host=influx_params['host'],
        port=influx_params['port'])

    params = {
        "db": influx_params['database'],
        "epoch": influx_params['epoch'],
        "q": "select value from {series}".format(series=influx_params['series'])
    }

    response = requests.get(url, params=params)

    return response.json()["results"][0]["series"][0]["values"], 0, 1

def backend_graphite(graphite_params):
    '''
        Pull timeseries data from influxdb REST API

        :param graphite_params: Dictionary containing graphite connection info.
        :type graphite_params: dict

        :returns: tuple containing a 2d array of timeseries data, the timeseries index, and the value index

        Fields:

        - protocol - http or https
        - host     - address of the influxdb server
        - port     - port the influxdb instance is listening on
        - target   - targeted data set
        - from     - start time of data to return
        - until    - end time of data to return
    '''

    if 'protocol' not in graphite_params:
        graphite_params['protocol'] = 'http'

    url = "{protocol}://{host}:{port}/render".format(
        protocol=graphite_params['protocol'],
        host=graphite_params['host'],
        port=graphite_params['port'])

    params = {
        "target": graphite_params['target'],
        "from": graphite_params['from'],
        "until": graphite_params['until'],
        "format": "json"
    }

    response = requests.get(url, params=params)

    return response.json()[0]['datapoints'], 1, 0

def _pull_backend(backend, params):
    if backend == "influxdb":
        return backend_influxdb(params)
    elif backend == "graphite":
        return backend_graphite(params)

def get_backends():
    static_globals = globals()
    return [x[8:] for x in static_globals if x[:8] == "backend_"]