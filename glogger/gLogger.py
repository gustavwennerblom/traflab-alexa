import logging
from logging.handlers import TimedRotatingFileHandler
import sys
import os


class GLogger(object):
    script_directory = os.path.dirname(os.path.realpath(__file__))
    log_directory=''
    filename='gLogger.log'

    def __init__(self, name=__name__, handler='stream'):
        self.log = logging.getLogger(name)
        self.log.setLevel(logging.DEBUG)

        if handler == 'timed_rotating_file':
            ch = TimedRotatingFileHandler(filename=os.path.join(self.script_directory, self.log_directory,
                                          self.filename), when='d', interval=1, backupCount=7)
        elif handler == 'file':
            ch = logging.FileHandler(filename=os.path.join(self.script_directory, self.log_directory, self.filename))
        else:
            ch = logging.StreamHandler(stream=sys.stderr)

        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(ch)

    def get_logger(self):
        return self.log

