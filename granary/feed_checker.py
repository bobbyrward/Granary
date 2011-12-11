import re
import logging
import urllib2
import httplib
import time

import feedparser
import wx
from wx.lib.newevent import NewEvent
from sqlalchemy.orm.exc import NoResultFound
from twisted.internet.task import LoopingCall

from granary import feed
from granary import db
from granary.configmanager import config


NewTorrentSeenEvent, EVT_NEW_TORRENT_SEEN = NewEvent()


log = logging.getLogger(__name__)


def get_rss_feed_entries(url):
    log.debug("Retrieving feed %s", url)

    try:
        rss_content = urllib2.urlopen(url)
    except httplib.BadStatusLine, e:
        log.exception("Error opening feed %s", url)
        return []
    except urllib2.URLError, e:
        log.exception("Error opening feed %s", url)
        return []
    except Exception, e:
        log.exception("Error opening feed %s", url)
        return []
    else:
        feed = feedparser.parse(rss_content.read())
        log.debug("Retrieving %d feed entries", len(feed['entries']))
        return reversed(feed['entries'])


class FeedChecker(object):
    def __init__(self):
        self.db = None
        self.loop = LoopingCall(self.tick)

    def stop(self):
        log.debug('stopping')
        self.loop.stop()

    def run(self):
        log.debug('running')
        self.loop.start(interval=60, now=True)

    def tick(self):
        start_time = time.time()

        try:
            self.db = db.DBSession()

            new_entries = self.find_new_entries()

            if new_entries:
                log.debug('Found %d new entries', len(new_entries))

                matched_entries = self.check_new_entries(new_entries)
                wx.GetApp().download_queue.queue_torrent(*matched_entries)

                elapsed_time = time.time() - start_time

                log.debug('tick elapsed time: %0.2f', elapsed_time)

        except Exception:
            log.exception('Unhandled exception in FeedChecker.tick')

    def find_new_entries(self):
        """Find all new entries in all feeds
        """
        new_entries = []

        for rss_feed_url in config().get_key('FEED_URLS'):
            for entry in feed.get_rss_feed_entries(rss_feed_url):
                try:
                    # find out if it's new
                    self.db.query_torrents().filter_by(name=entry['title']).one()
                except NoResultFound:
                    # it's new
                    db_entry = db.Torrent(entry['title'], entry['link'])

                    # save it to the database
                    if not self.db.save_torrent(db_entry):
                        log.warning("Unable to commit torrent to database: %s", db_entry.name)
                        raise Exception("Unable to commit torrent to database: %s" % db_entry.name)

                    new_entries.append(db_entry)

                    # notify the app that a new torrent was seen
                    evt = NewTorrentSeenEvent()
                    evt.torrent = db_entry
                    wx.PostEvent(wx.GetApp(), evt)
                else:
                    # not new. ignore
                    continue

        return new_entries

    def check_new_entries(self, new_entries):
        """Check all new entries to see if they match any of the regular expressions
        """
        matched_entries = []

        # check all new entries
        for entry in new_entries:

            # check all regular expressions against the entry
            for match_regexp in config().get_key('MATCH_TORRENTS'):

                # If it matches a regular expression,
                if re.match(match_regexp, entry.name, re.IGNORECASE):

                    # add it to the match list
                    matched_entries.append(entry)

                    # and stop checking it
                    continue

        return matched_entries


#TODO: Needs to be updated to work with the new threaded downloader
#    def test_regular_expressions(self):
#        """Test the updated regular expressions on the existing history
#        """
#        query = self.db.query_torrents()
#
#        # get all torrents ordered by date seen
#        torrents = query.order_by(db.Torrent.first_seen.desc()).all()
#
#        # find the matches
#        matched_entries = self.check_new_entries(torrents)
#
#        found_list = []
#
#        # compile a list of torrents that haven't already been downloaded
#        for torrent in matched_entries:
#            if not torrent.downloaded:
#                found_list.append(torrent)
#
#        if not found_list:
#            # no new matches
#            wx.MessageBox('Found no new matches', 'Test results',
#                    wx.OK | wx.ICON_INFORMATION)
#        else:
#            # new matches
#            message = 'Download the %d new matches?:\n\n' % len(found_list)
#            message += '\n'.join((x.name for x in found_list))
#
#            # ask if they should be downloaded
#            result = wx.MessageBox(message, 'Test Results',
#                    wx.YES_NO | wx.ICON_QUESTION)
#
#            if result == wx.YES:
#                # download them all
#                self.download_torrents(found_list)
