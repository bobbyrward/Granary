import re

import wx
from sqlalchemy.orm.exc import NoResultFound

from granary import downloader
from granary import feed
from granary import db
from granary.configmanager import config


class FeedDownloader(object):
    def tick(self):
        new_entries = self.find_new_entries()
        matched_entries = self.check_new_entries(new_entries)
        self.download_torrents(matched_entries)

    def find_new_entries(self):
        """Find all new entries in all feeds
        """
        new_entries = []

        for rss_feed_url in config().get_key('FEED_URLS'):
            for entry in feed.get_rss_feed_entries(rss_feed_url):
                try:
                    # find out if it's new
                    wx.GetApp().db.query_torrents().filter_by(name=entry['title']).one()
                except NoResultFound:
                    # it's new
                    db_entry = db.Torrent(entry['title'], entry['link'])

                    # save it to the database
                    if not wx.GetApp().db.save_torrent(db_entry):
                        raise Exception("Unable to commit torrent to database: %s" % db_entry.name)

                    new_entries.append(db_entry)

                    # notify the app that a new torrent was seen
                    wx.GetApp().OnNewTorrentSeen(db_entry)
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

    def download_torrents(self, matched_entries):
        """Download all the new entries
        """
        for torrent in matched_entries:
            download_torrent(torrent)

    def download_torrent(self, torrent):
        """Add the torrent to the client and update the app
        """
        # double check it wasn't already downloaded
        if torrent.downloaded:
            # already downloaded
            return

        # add it to the torrent client to download
        add_success = downloader.add_torrent_to_client(torrent)

        # check if it worked
        if not add_success:
            raise Exception('Unable to commit torrent: %s' % torrent.name)

        # udpate the database to indicate it was downloaded
        wx.GetApp().db.set_torrent_downloaded(torrent)

        # notify the app that a torrent was downloaded
        wx.GetApp().OnTorrentDownloaded(torrent)

    def test_regular_expressions(self):
        """Test the updated regular expressions on the existing history
        """
        query = wx.GetApp().db.query_torrents()

        # get all torrents ordered by date seen
        torrents = query.order_by(db.Torrent.first_seen.desc()).all()

        # find the matches
        matched_entries = check_new_entries(torrents)

        found_list = []

        # compile a list of torrents that haven't already been downloaded
        for torrent in matched_entries:
            if not torrent.downloaded:
                found_list.append(torrent)

        if not found_list:
            # no new matches
            wx.MessageBox('Found no new matches', 'Test results',
                    wx.OK | wx.ICON_INFORMATION)
        else:
            # new matches
            message = 'Download the %d new matches?:\n\n' % len(found_list)
            message += '\n'.join((x.name for x in found_list))

            # ask if they should be downloaded
            result = wx.MessageBox(message, 'Test Results',
                    wx.YES_NO | wx.ICON_QUESTION)

            if result == wx.YES:
                # download them all 
                download_torrents(found_list)



