import urllib2
import feedparser


class Feed(object):
    """Simple feed retrieval class using feedparser
    """

    def __init__(self, url):
        self.url = url
        self.parsed_feed = None

        self.refresh()

    def refresh(self):
        """Refresh the rss feed entries"""

        response = urllib2.urlopen(self.url)
        self.parsed_feed = feedparser.parse(response.read())

    def get_entries(self):
        """Return the rss feed entries"""

        if not self.parsed_feed:
            return None

        return self.parsed_feed['entries']





