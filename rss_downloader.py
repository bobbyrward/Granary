import re
import os
from collections import defaultdict

import wx

import config
import feed
import downloader
import db
import historywin
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
        self.timer = wx.Timer(self)
        self.timer.Start(1000 * 60)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimer, self.timer)

    def OnUpdateTimer(self, evt):
        #print "Updating"
        wx.GetApp().download_items()
            
    def ShowHistory(self):
        self.history.Refresh()
        self.history.Show()

    def OnCloseWindow(self, event):
        self.timer.Stop()
        del self.timer

        if self.tbicon is not None:
            self.tbicon.Destroy()
            self.tbicon = None

        self.Destroy()


class RssDownloaderApp(wx.App):
    def OnInit(self):
        self.feed = feed.Feed(config.FEED_URL)
        self.downloader = downloader.TorrentDownloader()
        self.matches = defaultdict(list)

        self.db = db.Database()
        self.db.connect()

        self.SetAppName("Rss Downloader")
        
        # For debugging
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

        # Force an update at load time
        #self.download_items()

        mainwindow = MainWindow()

        return True

    def download_items(self):
        self.find_matches()
        self.download_matches()

    def check_feed_entry(self, entry):
        """Check a feed entry for a match against MATCH_TORRENTS"""

        for match_regexp in config.MATCH_TORRENTS:
            match = re.match(match_regexp, entry['title'])

            # If it matches a regular expression, 
            if match:
                #print "Match: %s" % entry['title']

                # check if it was already downloaded
                results = self.db.query_torrents().filter_by(name=entry['title']).count()

                if results != 0:
                    #print 'Already Downloaded "%s"' % entry['title']
                    #print 'Results = ', results
                    return False

                # If it matches a regular expression, add it to matches under that regular expression
                self.matches[match_regexp].append(entry)
                return True

        # no match
        return False

    def find_matches(self):
        """Find all entries that match a regular expression in MATCH_TORRENTS"""

        for entry in self.feed.get_entries():
            # check each entry
            self.check_feed_entry(entry)

    def download_torrent(self, entry):
        torrent = self.downloader.download(entry['link'])
        path = os.path.join(config.DOWNLOAD_DIRECTORY, entry['title'] + '.torrent')
        torrent.write_to(path)

        db_torrent = db.Torrent(entry['title'])

        if not self.db.save_torrent(db_torrent):
            print 'ERROR: Unable to commit torrent name %s' % entry['title']

        print 'Downloaded "%s"' % entry['title']

    def download_matches(self):
        """Download all matches entries"""

        for regexp, matches in self.matches.iteritems():
            for entry in matches:
                # Download the torrent
                self.download_torrent(entry)


if __name__ == '__main__':
    app = RssDownloaderApp(False)
    app.MainLoop()


