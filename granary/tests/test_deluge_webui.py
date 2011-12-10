import json
import pprint
from nose.twistedtools import reactor, deferred
from twisted.internet.defer import Deferred, succeed
from twisted.web.iweb import IBodyProducer
from zope.interface import implements

from granary.http.client import HttpClient, SimpleContentProtocol


class DelugeWebUIBodyProducer(object):
    implements(IBodyProducer)

    def __init__(self, method, params, id=0):
        self.json = json.dumps({
            'method': method,
            'params': params,
            'id': id,
        })

        self.length = len(self.json)

    def startProducing(self, consumer):
        consumer.write(self.json)
        return succeed(None)

    def pauseProducing(self):
        pass

    def stopProducing(self):
        pass


def setup():
    pass


def teardown():
    pass


@deferred()
def test_login():
    client = HttpClient()

    raw_args = {
        'method': 'auth.login',
        'params': ['deluge'],
        'id': 0,
    }

    d = client.post('http://localhost:8112/json', DelugeWebUIBodyProducer('auth.login', ['deluge']))

    def parse_response(response):
        pprint.pprint(response)

    def on_post_success(result):
        assert result.code == 200

        finished = Deferred()
        finished.addCallback(parse_response)

        pprint.pprint(list(result.headers.getAllRawHeaders()))

        reader = SimpleContentProtocol(finished, json.loads)
        result.deliverBody(reader)

        return finished

    d.addCallback(on_post_success)

    return d
