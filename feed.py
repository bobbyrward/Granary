import urllib2
import feedparser
import httplib


def get_rss_feed_entries(url):
    try:
        rss_content = urllib2.urlopen(url)
    except httplib.BadStatusLine, e:
        print "%r: args='%s' line'%s'" % (e, e.args, e.line)
        return []
    except urllib2.URLError, e:
        print "%r: %s" % (e, e.args)
        return []
    except Exception, e:
        print "%r: %s" % (e, e.args)
        return []
    else:
        feed = feedparser.parse(rss_content.read())
        return reversed(feed['entries'])


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





