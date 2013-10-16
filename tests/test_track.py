import time
import track
import unittest

class TrackTestCase(unittest.TestCase):
    def test_version(self):
    #def purchase(self, profile_id, currency, gross_amount, net_amount, payment_provider, product):
        t = track.Track('EU')
        t.purchase(1, 'USD', 10, 10, 'PayPal', 'Gold')
        time.sleep(0.1)
