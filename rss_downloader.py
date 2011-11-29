import re
import os
from collections import defaultdict

import wx
from sqlalchemy.orm.exc import NoResultFound

import config
import feed
import downloader
import db
import historywin
import feed_history
import taskbar


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Rss Downloader", size = (64,64),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        img = wx.Image('16-rss-square.png', wx.BITMAP_TYPE_PNG)
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        self.SetIcon(icon)

        try:
            self.tbicon = taskbar.RssDownloaderTaskBarIcon(self)
        except:
            self.tbicon = None

        self.history = historywin.HistoryWindow(self)
        self.feed_history = feed_history.FeedHistoryWindow(self)
        self.timer = wx.Timer(self)
        self.timer.Start(1000 * 60)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimer, self.timer)

    def OnUpdateTimer(self, evt):
        #print "Updating"
        wx.GetApp().download_items()
            
    def ShowDownloadHistory(self):
        self.history.Refresh()
        self.history.Show()

    def ToggleDownloadHistory(self):
        if self.history.IsShown():
            self.history.Hide()
        else:
            self.ShowFeedHistory()

    def ShowFeedHistory(self):
        self.feed_history.Refresh()
        self.feed_history.Show()

    def OnCloseWindow(self, event):
        self.timer.Stop()
        del self.timer

        if self.tbicon is not None:
            self.tbicon.Destroy()
            self.tbicon = None

        self.Destroy()

    def NewTorrentDownloaded(self, found):
        self.history.NewTorrentDownloaded(found)

    def NewTorrentSeen(self, seen):
        self.feed_history.NewTorrentSeen(seen)


class RssDownloaderApp(wx.App):
    def OnInit(self):
        self.feed = feed.Feed(config.FEED_URL)
        self.downloader = downloader.TorrentDownloader()

        self.db = db.Database()
        self.db.connect()

        self.SetAppName("Rss Downloader")
        
        # For debugging
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

        self.mainwindow = MainWindow()

        # Force an update at load time
        self.download_items()

        return True

    def download_items(self):
        """Download all matches entries"""

        matches = self.find_matches()

        for regexp, matches in matches.iteritems():
            for entry in matches:
                # Download the torrent
                self.download_torrent(entry)

    def check_feed_entry(self, entry, matches):
        """Check a feed entry for a match against MATCH_TORRENTS"""

        for match_regexp in config.MATCH_TORRENTS:
            match = re.match(match_regexp, entry['title'])

            # If it matches a regular expression, 
            if match:
                #print "Match: %s" % entry['title']

                # If it matches a regular expression, add it to matches under that regular expression
                matches[match_regexp].append(entry)
                return True

        # no match
        return False

    def add_entry_to_history(self, entry):
        """Add feed to database for historical purposes

        Returns True if this is the first time the entry was seen
        """

        try:
            found = self.db.query_torrents().filter_by(name=entry['title']).one()
        except NoResultFound:
            return False

        db_entry = db.Torrent(entry['title'], entry['link'])

        if not self.db.save_torrent(db_entry):
            print 'ERROR: Unable to commit feed entry name %s' % entry['title']

        self.mainwindow.NewTorrentSeen(found)

    def find_matches(self):
        """Find all entries that match a regular expression in MATCH_TORRENTS"""

        matches = defaultdict(list)

        for entry in self.feed.get_entries():
            # check each new entry
            if self.add_entry_to_history(entry):
                self.check_feed_entry(entry, matches)

        return matches

    def download_torrent(self, entry):
        torrent = self.downloader.download(entry['link'])
        path = os.path.join(config.DOWNLOAD_DIRECTORY, entry['title'] + '.torrent')
        torrent.write_to(path)

        try:
            found = self.db.query_torrents().filter_by(name=entry['title']).one()
        except NoResultFound:
            print "ERROR: Torrent downloaded but not already in database. (%s)" % entry['title']

        found.downloaded = True 

        if not self.db.save_torrent(found):
            print 'ERROR: Unable to commit torrent name %s' % entry['title']

        print 'Downloaded "%s"' % entry['title']

        self.mainwindow.NewTorrentDownloaded(found)


if __name__ == '__main__':
    app = RssDownloaderApp(False)
    app.MainLoop()


