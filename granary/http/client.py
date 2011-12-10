from cookielib import CookieJar

from twisted.web.client import Agent, CookieAgent, ContentDecoderAgent, GzipDecoder
from twisted.internet import reactor
from twisted.internet.protocol import Protocol
from twisted.web.client import ResponseDone
from twisted.web.http import PotentialDataLoss


class HttpClient(object):
    def __init__(self):
        self.cookies = CookieJar()
        self.agent = Agent(reactor)
        self.agent = CookieAgent(self.agent, self.cookies)
        self.agent = ContentDecoderAgent(self.agent, [('gzip', GzipDecoder)])

    def post(self, url, body_producer, headers=None):
        return self.agent.request('POST', url, headers, body_producer)

    def get(self, url, headers=None):
        return self.agent.request('GET', url, headers)


class SimpleContentProtocol(Protocol):
    def __init__(self, finished, parse_function=None):
        self.finished = finished
        self.body = []
        self.parse_function = parse_function

    def dataReceived(self, bytes):
        self.body.extend(bytes)

    def connectionLost(self, reason):
        assert reason.check(ResponseDone, PotentialDataLoss)

        content = ''.join(self.body)

        if self.parse_function:
            content = self.parse_function(content)

        self.finished.callback(content)
