import feedparser
from nose.twistedtools import reactor, deferred
from twisted.internet.defer import Deferred

from granary.http.client import HttpClient, SimpleContentProtocol


def setup():
    pass


def teardown():
    pass


@deferred()
def test_feed_request():
    client = HttpClient()

    d = client.get('http://hasthelhcdestroyedtheearth.com/rss.xml')

    def parse_feed(feed):
        assert 'bozo_exception' not in feed
        assert feed['feed']['title'] == 'Has the Large Hadron Collider destroyed the earth yet?'
        assert feed['feed']['language'] == 'en-us'
        assert feed['entries'][0]['title'] == 'NO.'
        assert feed['entries'][0]['description'] == 'NO.'

    def on_get_success(result):
        assert result.code == 200

        finished = Deferred()
        finished.addCallback(parse_feed)

        reader = SimpleContentProtocol(finished, feedparser.parse)
        result.deliverBody(reader)

        return finished

    d.addCallback(on_get_success)

    return d
