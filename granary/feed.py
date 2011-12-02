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
