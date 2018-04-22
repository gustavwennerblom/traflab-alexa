from flask_ask import Ask, question, statement, session
from flask import Flask, render_template
from traflab2 import Trafiklab
from glogger.gLogger import GLogger
import json
from collections import defaultdict
from DBHelper import DBHelper

log = GLogger(name='traflab-alexa-main').get_logger()

app = Flask(__name__)
ask = Ask(app, '/')
db = DBHelper()

log.info("Log enabled")


# Build a dict of site id's to use when querying the main Trafiklab API
SITE_IDS = defaultdict(set)
with open('sl_Site_20180422-2113.json') as f:
    full_map = json.load(f)
    for site in full_map['ResponseData']['Result']:
        SITE_IDS[site['SiteName'].lower()].add(site['SiteId'])
        # SITE_IDS[site['StopPointName']].add((site['StopAreaNumber'],site['StopAreaTypeCode']))
    log.info('Built reference of SITE_IDs ({} entries)'.format(len(SITE_IDS)))


@ask.launch
def launch_skill():
    user_id = session.user.userId
    log.info("Skill launched for userId {}".format(user_id))
    departure_site = db.get_default_site(user_id)
    return question(render_template('welcome', departure_site=departure_site))


@ask.intent('OneShotDepartureIntent')
def one_shot_departure(direction, mode):
    log.info("OneShotDepartureIntent got direction={}, mode={}".format(direction, mode))
    return _make_trafiklab_request(origin=db.get_default_site(session.user.userId), direction=direction, mode=mode)


@ask.intent('DialogDepartureIntent')
def dialog_departure():
    return render_template('not_yet_implemented')   # TODO: Implement dialogue intent resolver


@ask.intent('SupportedOriginsIntent')
def supported_origins():
    log.info('Got into supported origins')
    origins = ', '.join(SITE_IDS.keys())
    list_origins_utterance = render_template('list_origins', origins=origins)
    return question(list_origins_utterance)

@ask.intent('MyAddressIntent')
def check_my_address():
    log.info('Stating device address')
    for key, value in get_device_address().items():
        log.info('Key: {}, Value: {}'.format(key, value))
    return statement(render_template('dev_confirmation', func='check_my_address'))

# TODO: Fix a function for setting a default origin


def _make_trafiklab_request(origin, mode, direction):   # TODO: Handle direction argument
    assert origin in SITE_IDS
    trafiklab = Trafiklab(siteid=SITE_IDS[origin].pop())        # TODO: Handle multiple sites
    if mode == 'tram':
        departures = trafiklab.get_trams()
    elif mode == 'bus':
        departures = trafiklab.get_buses()
    else:
        raise ValueError('Got unsupported mode: "{}"'.format(mode))

    if not departures:   # get_x method has returned empty list
        return statement(render_template('sl_error'))

    departure = departures[0]

    """
    log.info("Returning departure_info with mode={}, display_time={}, destination={}"
             .format(mode, departure.display_time, departure.destination))
    statement_utterance = render_template('departure_info',
                                          mode=mode,
                                          display_time=departure.display_time,
                                          destination=departure.destination)
    """
    # TODO: Handle full list of departures (Below is untested)
    all_departures_text = [render_template('departure_info',
                                           mode=mode,
                                           line_number=departure.line_number,
                                           display_time=departure.display_time,
                                           destination=departure.destination)
                           for departure in departures]
    
    statement_utterance= '...'.join(all_departures_text)
    return statement(statement_utterance)


def get_device_address():   # TODO: Test with a real device
    from flask_ask import context
    import requests
    from urllib.parse import urljoin
    device_id = context.System.device.deviceId
    api_access_token = context.System.apiAccessToken
    api_endpoint = context.System.apiEndpoint
    api_path = '/v1/devices/{deviceId}/settings/address'
    log.info("Identified device as bearing id {}".format(device_id))
    log.info("Token for API access is {}".format(api_access_token))

    headers = dict(Authorization='Bearer {}'.format(api_access_token))
    address_endpoint = urljoin(api_endpoint, api_path)
    result = requests.get(address_endpoint.format(deviceId=device_id), headers=headers)
    address_json = result.json()
    return address_json


if __name__ == '__main__':
    app.run(debug=True)