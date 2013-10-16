from __future__ import absolute_import

import time

from .compat import _urlparse, HTTPError
from .transport import HTTPTransport

class ClientState(object):
    ONLINE = 1
    ERROR = 0

    def __init__(self):
        self.status = self.ONLINE
        self.last_check = None
        self.retry_number = 0

    def should_try(self):
        if self.status == self.ONLINE:
            return True

        interval = min(self.retry_number, 6) ** 2

        if time.time() - self.last_check > interval:
            return True

        return False

    def set_fail(self):
        self.status = self.ERROR
        self.retry_number += 1
        self.last_check = time.time()

    def set_success(self):
        self.status = self.ONLINE
        self.last_check = None
        self.retry_number = 0

    def did_fail(self):
        return self.status == self.ERROR

class Track(object):
    def __init__(self, region, uri_base=None):
        self.region = region
        self.uri_base = uri_base or 'http://localhost:6062/api/1.0/track/'
        self.max_retries = 3
        self.timeout = 1.0
        self.state = ClientState()

        # TODO: Read dynamic
        self._transport = HTTPTransport(timeout=self.timeout)

    def purchase(self, profile_id, currency, gross_amount, net_amount, payment_provider, product):
        data = {
            'Region': self.region,
            'ProfileID': profile_id,
            'Currency': currency,
            'GrossAmount': gross_amount,
            'NetAmount': net_amount,
            'PaymentProvider': payment_provider,
            'Product': product}
        self.send_remote('purchase/', data)

    def session(self, session_id, remote_ip, session_type, profile_id=None, message=None):
        data = {
            'Region': self.region,
            'SessionID': session_id,
            'SessionType': session_type
        }

        if profile_id:
            data['ProfileID'] = profile_id

        if message:
            data['Message'] = message

        self.send_remote('session/', data)

    def user(self, profile_id, referrer=None, message=None):
        data = {
            'Region': self.region,
            'ProfileID': profile_id,
        }

        if referrer:
            data['Referrer'] = referrer

        if message:
            data['Message'] = message

        self.send_remote('user/', data)

    def item(self, profile_id, item_name, item_type, is_ugc, price_gold=0, price_silver=0):
        data = {
            'Region': self.region,
            'ProfileID': profile_id,
            'ItemName': item_name,
            'ItemType': item_type,
            'IsUGC': is_ugc,
            'PriceGold': price_gold,
            'PriceSilver': price_silver,
        }
        self.send_remote('item/', data)

    def _successful_send(self):
        self.state.set_success()

    def _failed_send(self, e, url, data):
        if isinstance(e, HTTPError):
            body = e.read()
            print body
        #    self.error_logger.error(
        #    'Unable to reach Sentry log server: %s (url: %s, body: %s)',
        #    e, url, body, exc_info=True,
        #    extra={'data': {'body': body[:200], 'remote_url': url}})
        #else:
        #    self.error_logger.error(
        #    'Unable to reach Sentry log server: %s (url: %s)', e, url,
        #    exc_info=True, extra={'data': {'remote_url': url}})

        #message = self._get_log_message(data)
        #self.error_logger.error('Failed to submit message: %r', message)
        print e
        self.state.set_fail()

    def send_remote(self, endpoint, data, headers={}):
        if not self.state.should_try():
            print 'should not try'
            #message = self._get_log_message(data)
            #self.error_logger.error(message)
            return

        uri = _urlparse.urljoin(self.uri, endpoint)

        def failed_send(e):
            self._failed_send(e, uri, data)

        try:
            if self._transport.async:
                self._transport.async_send(uri, data, headers, self._successful_send, failed_send)
            else:
                self._transport.send(uri, data, headers)
                self._successful_send()
        except Exception as e:
            failed_send(e)
