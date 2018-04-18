from flask_ask import Ask, question, statement
from flask import Flask, render_template
from traflab2 import Trafiklab
import logging
import sys

log = logging.getLogger("main")
logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
log.info("Log online")
# handler = logging.StreamHandler(sys.stdout)

app = Flask(__name__)
ask = Ask(app, '/')

SITE_IDS = {'sickla kaj': '1550'}


@ask.launch
def launch_skill():
    log.info("Skill launched")
    return question(render_template('welcome'))


@ask.intent('OneShotDepartureIntent',
            mapping={'origin': 'Origin', 'direction': 'Direction', 'mode': 'Mode'},
            default={'origin': 'sickla kaj'})
def one_shot_departure(origin, direction, mode):
    log.info("Got origin: {}".format(origin))
    if origin.lower() not in SITE_IDS:
        return supported_origins()
    return _make_trafiklab_request(origin=origin, mode=mode)


@ask.intent('DialogDepartureIntent')
def dialog_departure():
    return render_template('not_yet_implemented')


@ask.intent('SupportedOriginsIntent')
def supported_origins():
    origins = ', '.join(SITE_IDS.keys())
    list_origins_utterance = render_template('list_origins', origins=origins)
    return question(list_origins_utterance)


def _make_trafiklab_request(origin, mode):
    assert origin in SITE_IDS
    trafiklab = Trafiklab(siteid=SITE_IDS[origin])
    departure = trafiklab.get_trams()[0]
    statement_utterance = render_template('departure_info',
                                          mode=mode,
                                          destination=departure.destination,
                                          display_time=departure.display_time)
    return statement(statement_utterance)


if __name__ == '__main__':
    app.run(debug=True)