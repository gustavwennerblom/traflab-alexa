import json
import urllib2
import requests
import pprint

API_KEY="" #REMOVED - TAKE FROM FILE IN SOURCE DIR
SITE_ID_SICKLAKAJ="1550"
SITE_ID_SICKLAUDDE="9820"
#URL="http://api.sl.se/api2/realtimedeparturesV4.json?key=<DIN API NYCKEL>&siteid=<SITEID>&timewindow=<TIMEWINDOW>"
URL="http://api.sl.se/api2/realtimedeparturesV4.{0}?key={1}&siteid={2}&timewindow={3}".format("json", API_KEY, SITE_ID_SICKLAKAJ, "30")


def get_full_response(url):
    #Returns a dict from the JSON provided by the Trafiklab API, given a compliant REST call
    #response=urllib2.urlopen(url)
    #return response.read()
    response=requests.get(url)
    return response.json()

def get_trams(url):
    #Returns a dict of tram destinations (keys) and departure times (values, as displayed on boards)
    j=(get_full_response(url))
    trams=dict()
    for departure in j["ResponseData"]["Trams"]:
        #r.append(departure["Destination"] + ":   " + departure["DisplayTime"])
        trams[departure["Destination"]]=departure["DisplayTime"]
    return trams

def get_buses(url):
    #Returns a dics of bus destinations (keys) and departure times (values, as displayed on boards)
    j=get_full_response(url)
    buses=dict()
    for departure in j["ResponseData"]["Buses"]:
        buses[departure["Destination"]]=departure["DisplayTime"]
    return buses

print("Tvarbana______________________")
print(get_trams(URL))
#print(get_buses(URL))
print("---")
print ("Bussar_________________________")
print(get_buses(URL))
#print(j["ExecutionTime"])
pp=pprint.PrettyPrinter(indent=4)
pp.pprint(get_full_response(URL))
