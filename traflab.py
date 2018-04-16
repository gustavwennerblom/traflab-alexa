class Traflab():

    def get_full_response(self, url):
        #Returns a dict from the JSON provided by the Trafiklab API, given a compliant REST call
        import requests
        response=requests.get(url)
        return response.json()

    def get_trams(self, url):
        #Returns a dict of tram destinations (keys) and departure times (values, as displayed on boards)
        j=self.get_full_response(url)
        trams=dict()    
        for departure in j["ResponseData"]["Trams"]:
            trams[departure["Destination"]]=departure["DisplayTime"]
        return trams

    def get_buses(self, url):
        #Returns a dics of bus destinations (keys) and departure times (values, as displayed on boards)
        j=get_full_response(url)
        buses=dict()
        for departure in j["ResponseData"]["Buses"]:
            buses[departure["Destination"]]=departure["DisplayTime"]
        return buses

    def __init__(self):
        self.classname="GW's class test for traflab"
        try:
            self.f=open("traflabkey.txt", "r")
            import json
            self.API_KEY=json.loads(self.f.readline())
        except:
            print("Error reading file")
            return("FATAL ERROR")
        finally:
            self.f.close()
        self.SITE_ID_SICKLAKAJ="1550"
        self.URL="http://api.sl.se/api2/realtimedeparturesV4.{0}?key={1}&siteid={2}&timewindow={3}".format("json", self.API_KEY, self.SITE_ID_SICKLAKAJ, "30")


    
