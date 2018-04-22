from glogger.gLogger import GLogger


class DBHelper(object):

    def get_default_site(self, user_id):
        if user_id == 'amzn1.ask.account.AHQSD27I4E4GWTS7HVGEYTWOYS22TYUWHBU3OQN5QEJFLIRFX3YVZ6VL5XE5WWXKHHI7UA3ZS4WSGTQAZSO67643SGOCSEBOQZ35UCNDVPEVJKNKOEBERMJKUBUOHLCEII2XNI6DHHJ25TQZDSEDXHVGKGTMCFPOBNKM6ABUH3SNCPXFTEKAHNTN5FI5R5OWKEYOMHGLC22W3BQ':
            return 'sickla kaj'

    def __init__(self):
        self.log = GLogger(name=__name__).get_logger()
        self.log.info("Log initiated (DBHelper")