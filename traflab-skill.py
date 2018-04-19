from flask_ask import Ask, question, statement
from flask import Flask, render_template
from traflab2 import Trafiklab
from glogger.gLogger import GLogger

log = GLogger(name='traflab-alexa-main').get_logger()

app = Flask(__name__)
ask = Ask(app, '/')

SITE_IDS = {'sickla kaj': '1550'}       # TODO: Move out to separate file

log.info("Log enabled")


@ask.launch
def launch_skill():
    log.info("Skill launched")
    return question(render_template('welcome'))


# TODO: Find a more graceful way of handling default. Possibly a combo of https://www.trafiklab.se/api/sl-platsuppslag/dokumentation and https://developer.amazon.com/docs/custom-skills/device-address-api.html#getAddress
@ask.intent('OneShotDepartureIntent',
            default={'origin': 'sickla kaj'})
def one_shot_departure(origin, direction, mode):
    log.info("OneShotDepartureIntent got origin={}, direction={}, mode={}".format(origin, direction, mode))
    if origin.lower() not in SITE_IDS:
        return supported_origins()
    return _make_trafiklab_request(origin=origin, direction=direction, mode=mode)


@ask.intent('DialogDepartureIntent')
def dialog_departure():
    return render_template('not_yet_implemented')   # TODO: Implement dialogue intent resolver


@ask.intent('SupportedOriginsIntent')
def supported_origins():
    log.info('Got into supported endpoints')
    origins = ', '.join(SITE_IDS.keys())
    list_origins_utterance = render_template('list_origins', origins=origins)
    return question(list_origins_utterance)

# TODO: Fix a function for setting a default origin


def _make_trafiklab_request(origin, mode, direction):   # TODO: Handle direction argument
    assert origin in SITE_IDS
    trafiklab = Trafiklab(siteid=SITE_IDS[origin])
    departure = trafiklab.get_trams()[0]
    log.info("Returning departure_info with mode={}, display_time={}, destination={}"
             .format(mode, departure.display_time, departure.destination))
    statement_utterance = render_template('departure_info',
                                          mode=mode,
                                          display_time=departure.display_time,
                                          destination=departure.destination)
    return statement(statement_utterance)


if __name__ == '__main__':
    app.run(debug=True)