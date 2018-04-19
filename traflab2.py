from credentials import trafiklab_key
import requests
from collections import namedtuple


class Trafiklab(object):
    SITE_ID_SICKLAKAJ="1550"
    BASE_URL = "http://api.sl.se/api2/realtimedeparturesV4.{schema}?key={key}&siteid={siteid}&timewindow={timewindow}"

    def get_full_response(self, url):
        #Returns a dict from the JSON provided by the Trafiklab API, given a compliant REST call
        import requests
        response=requests.get(url)
        return response.json()

    def get_trams(self):
        # Returns a namedtuple of tram destinations and departure times (values, as displayed on boards)
        response = requests.get(self.endpoint).json()
        trams = []
        Departure = namedtuple('Departure', ['destination', 'display_time'])
        for dept in response["ResponseData"]["Trams"]:
            trams.append(Departure(dept["Destination"], dept["DisplayTime"]))
        return trams

    def get_buses(self):
        # Returns a namedtuple of bus destinations and departure times (values, as displayed on boards)
        response = requests.get(self.endpoint).json()
        buses = []
        Departure = namedtuple('Departure', ['destination', 'display_time'])
        for dept in response["ResponseData"]["Buses"]:
            buses.append(Departure(dept["Destination"], dept["DisplayTime"]))
        return buses

    def set_endpoint(self, schema, key, site_id, time_window):
        self.endpoint = self.BASE_URL.format(schema=schema, key=key, siteid=site_id, timewindow=time_window)
        return endpoint

    def __init__(self, schema='json', siteid=None, timewindow='30'):
        self.API_KEY = trafiklab_key.key
        if not siteid:
            self.home_station = self.SITE_ID_SICKLAKAJ
        else:
            self.home_station = siteid
        self.endpoint = self.BASE_URL.format(schema=schema,
                                             key=self.API_KEY,
                                             siteid=self.home_station,
                                             timewindow=timewindow)


if __name__ == '__main__':
    trafiklab = Trafiklab()
    result_trams = trafiklab.get_trams()
    result_buses = trafiklab.get_buses()
    from pprint import pprint
    pprint(result_trams)
    pprint(result_buses)
