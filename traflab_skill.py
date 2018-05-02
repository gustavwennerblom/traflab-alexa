from flask_ask import Ask, question, statement, session, delegate
from flask import Flask, render_template
from traflab2 import Trafiklab
from glogger.gLogger import GLogger
import json
import os
from collections import defaultdict, namedtuple
from DBHelper import DBHelper
from pprint import pprint

log = GLogger(handler='stream').get_logger()

app = Flask(__name__)
ask = Ask(app, '/')
db = DBHelper()

log.info("Log enabled")


# Build a dict of site id's to use when querying the main Trafiklab API
SITE_IDS = defaultdict(list)
with open(os.path.join(os.path.dirname(__file__),'sl_Site_20180422-2113.json')) as f:
    full_map = json.load(f)
    for site in full_map['ResponseData']['Result']:
        if not site['SiteName'].lower() in SITE_IDS:
            SITE_IDS[site['SiteName'].lower()].append(site['SiteId'])
            # SITE_IDS[site['StopPointName']].add((site['StopAreaNumber'],site['StopAreaTypeCode']))
    log.info('Built reference of SITE_IDs ({} entries)'.format(len(SITE_IDS)))


@ask.launch
def launch_skill():
    user_id = session.user.userId
    log.info("Skill launched for userId {}".format(user_id))
    departure_site = db.get_default_site(user_id)
    response = render_template('welcome', departure_site=departure_site)
    return question(render_template('welcome', departure_site=departure_site))


@ask.intent('OneShotDepartureIntent')
def one_shot_departure(direction, mode):
    log.info("OneShotDepartureIntent got direction={}, mode={}".format(direction, mode))
    if not dialog_completed():
        return delegate()

    departures = _make_trafiklab_request(origin=db.get_default_site(session.user.userId), direction=direction, mode=mode)

    if not departures:   # empty list returned
        return statement(render_template('sl_error', mode=mode))

    departures_first = []
    departures_next = []

    for departure in departures:
        if departure.destination not in [departure.destination for departure in departures_first]:
            departures_first.append(departure)
        else:
            departures_next.append(departure)

    # store next set of departures in session variables
    session.attributes['mode'] = mode
    session.attributes['next_departures'] = departures_next

    first_departures_statement = render_departure_response(mode, departures_first, follow_up=True)
    log.info('Returning {}'.format(first_departures_statement))
    return question(first_departures_statement)


@ask.intent('AMAZON.YesIntent')
def more_departures_intent():
    next_departures = session.attributes.get('next_departures')
    print('next_departures: ' + str(next_departures))
    if next_departures:
        mode = session.attributes.get('mode')
        Departure = namedtuple('Departure', ['destination', 'display_time', 'line_number'])     #TODO: Check if attrs have a better solution
        next_departures_nt = [Departure(*attributes) for attributes in next_departures]
        return statement(render_departure_response(mode, next_departures_nt, follow_up=False))
    else:
        return statement("I have no further departures to report")


@ask.intent('AMAZON.NoIntent')
def finish_off():
    return statement("OK, have a nice trip!")


@ask.intent('SupportedOriginsIntent')
def supported_origins():
    log.info('Got into supported origins')
    origins = ', '.join(SITE_IDS.keys())
    list_origins_utterance = render_template('list_origins', origins=origins)
    return question(list_origins_utterance)


@ask.intent('AMAZON.StopIntent')
def stop():
    log.info("Stopping on user request (AMAZON.StopIntent")
    return statement('Bye')


@ask.intent('AMAZON.CancelIntent')
def cancel():
    log.info("Cancelling on user request (AMAZON.CancelIntent")
    return statement('')


@ask.intent('MyAddressIntent')
def check_my_address():
    log.info('Stating device address')
    device_address = get_device_address()
    for key, value in get_device_address().items():
        log.info('Key: {}, Value: {}'.format(key, value))
    street = device_address.get('addressLine1')
    postal_code = device_address.get('postalCode')
    city = device_address.get('city')
    return statement(render_template('device_address', street=street, postal_code=postal_code, city=city))


def render_departure_response(mode, departures, follow_up, ssml=True):
    if ssml:
        pause_marker = '<break time="1s"/>'
    else:
        pause_marker = '...'

    first_departures_text = [render_template('departure_info',
                                             mode=mode,
                                             line_number=departure.line_number,
                                             display_time=departure.display_time,
                                             destination=departure.destination)
                             for departure in departures]
    statement_utterance = pause_marker.join(first_departures_text)

    if follow_up:
        statement_utterance += "{} do you want to hear later departures".format(pause_marker)

    statement_utterance = '{0}{1}{2}'.format('<speak>', statement_utterance, '</speak>')

    return statement_utterance


def _make_trafiklab_request(origin, mode, direction):   # TODO: Handle direction argument
    assert origin in SITE_IDS
    trafiklab = Trafiklab(siteid=SITE_IDS[origin][0])        # TODO: Handle multiple sites
    if mode == 'tram':
        departures = trafiklab.get_trams()
    elif mode == 'bus':
        departures = trafiklab.get_buses()
    else:
        raise ValueError('Got unsupported mode: "{}"'.format(mode))

    return departures


def get_device_address():
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


@app.template_filter()
def standardize_time(time):
    assert isinstance(time, str)
    if ' ' in time:
        number, text = time.split(' ')
        if number == '1':
            return "in {} minute".format(number)
        else:
            return "in {} minutes".format(number)

    if 'nu' in time.lower():
        return "now"

    return "at {}".format(time)

def dialog_completed():
    dialog_state = session['dialogState']
    return dialog_state == 'COMPLETED'

if __name__ == '__main__':
    app.run(debug=False)
