from credentials import trafiklab_key
import requests
from collections import namedtuple
from pprint import pprint
from datetime import datetime
from glogger.gLogger import GLogger
import json
import logging


class Trafiklab(object):
    SITE_ID_SICKLAKAJ="1550"
    BASE_URL = "http://api.sl.se/api2/realtimedeparturesV4.{schema}?key={key}&siteid={siteid}&timewindow={timewindow}"

    def get_full_response(self, url):
        # Returns a dict from the JSON provided by the Trafiklab API, given a compliant REST call
        import requests
        response=requests.get(url)
        return response.json()

    def get_trams(self):
        # Returns a namedtuple of tram destinations and departure times (values, as displayed on boards)
        response = requests.get(self.endpoint).json()
        self.log.info(response)
        trams = []
        Departure = namedtuple('Departure', ['destination', 'display_time', 'line_number'])
        for dept in response["ResponseData"]["Trams"]:
            self.log.info("Got {}".format(dept))
            trams.append(Departure(dept["Destination"], dept["DisplayTime"], dept['LineNumber']))
        return trams

    def get_buses(self, **kwargs):
        # Returns a namedtuple of bus destinations and departure times (values, as displayed on boards)
        response = requests.get(self.endpoint).json()
        # self.log.info(response)
        buses = []
        Departure = namedtuple('Departure', ['destination', 'display_time', 'line_number'])
        for dept in response["ResponseData"]["Buses"]:
            buses.append(Departure(dept["Destination"], dept["DisplayTime"], dept["LineNumber"]))
        return buses

    def set_endpoint(self, schema, key, site_id, time_window):
        self.endpoint = self.BASE_URL.format(schema=schema, key=key, siteid=site_id, timewindow=time_window)
        return endpoint

    def __init__(self, schema='json', siteid=None, timewindow='30'):
        self.log = GLogger().get_logger()
        self.log.info("Trafiklab object initiated")
        self.API_KEY = trafiklab_key.key
        if not siteid:
            self.home_station = self.SITE_ID_SICKLAKAJ
        else:
            self.home_station = siteid
        self.endpoint = self.BASE_URL.format(schema=schema,
                                             key=self.API_KEY,
                                             siteid=self.home_station,
                                             timewindow=timewindow)


class StopPointFetcher(object):     #TODO: Change name to reflect expanded scope
    """
    This class interacts with the Stops and Lines directory API https://www.trafiklab.se/api/sl-hallplatser-och-linjer-2
    """
    def __init__(self, schema='json', granularity='StopPoint'):  #TODO: Use json parameter in endpoint string formatter
        self.log = GLogger(name=__name__).get_logger()
        self.granularity = granularity
        self.API_KEY = trafiklab_key.key_stops_and_lines
        self.endpoint = ('http://api.sl.se/api2/LineData.{1}?model={2}&key={0}'
                         .format(self.API_KEY, schema, granularity))

    def get_stop_points(self):
        result = requests.get(self.endpoint).json()
        self.log.info("Queried for {}".format(self.granularity))
        return result

    def download_stop_points(self):
        datetime_string = datetime.now().strftime('%Y%m%d-%H%M')
        filename = 'sl_{1}_{0}.json'.format(datetime_string, self.granularity)
        with open(filename,'w') as f:
            f.write(json.dumps(self.get_stop_points()))
            self.log.info("{1} data written to {0}".format(filename, self.granularity))
        return 200

class StopLookuper(object):
    def __init__(self):
        self.log = GLogger(name='StopLookuperLog').get_logger()
        self.API_KEY = trafiklab_key.key_platsuppslag
        self.endpoint = 'http://api.sl.se/api2/typeahead.{}?key={}&searchstring={}stationsonly=True&maxresults=10'

    def lookup_stop(self, search_items, fmt='json'):
        assert isinstance(search_items, list)
        search_string = ','.join(search_items)
        response = requests.get(self.endpoint.format(fmt, self.API_KEY, search_string))
        return response


class StopLookuper2(object):
    def __init__(self):
        self.log = GLogger(name='StopLookuperLog').get_logger()
        self.API_KEY = trafiklab_key.key_close_stops
        self.endpoint = 'http://api.sl.se/api2/nearbystops.{}?key={}&originCoordLat={}&originCoordLong={}&maxresults={}&radius={}'

    def find_stop(self, lat, long, **kwargs):
        fmt = kwargs.get('fmt') or 'json'
        max_results = kwargs.get('max_results') or 5
        radius = kwargs.get('radius') or 1000
        response = requests.get(self.endpoint.format(fmt, self.API_KEY, lat, long, max_results, radius))
        return response




# class SiteFetcher(object):
#     def __init__(self, schema='json'):
#         self.log = GLogger(name="SiteFetcherLog: " + __name__).get_logger()
#         self.API_KEY = trafiklab_key

if __name__ == '__main__':
    #trafiklab = Trafiklab()
    #result_trams = trafiklab.get_trams()
    # result_buses = trafiklab.get_buses()
    #from pprint import pprint
    #pprint(result_trams)
    # pprint(result_buses)
    # spf = StopPointFetcher(granularity='Site')
    # pprint(spf.get_stop_points())
    # print(spf.download_stop_points())
    my_coords=(59.303014, 18.105589)
    sl = StopLookuper2()
    res = sl.find_stop(lat=my_coords[0], long=my_coords[1])
    pprint(res.json())
