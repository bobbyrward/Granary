import urllib2
import feedparser
import httplib
import traceback


def get_rss_feed_entries(url):
    try:
        rss_content = urllib2.urlopen(url)
    except httplib.BadStatusLine, e:
        #traceback.print_exc()
        return []
    except urllib2.URLError, e:
        #traceback.print_exc()
        return []
    except Exception, e:
        #traceback.print_exc()
        return []
    else:
        feed = feedparser.parse(rss_content.read())
        return reversed(feed['entries'])
