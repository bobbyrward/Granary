import re
import sys
import os
from collections import defaultdict

import wx
from sqlalchemy.orm.exc import NoResultFound

from configmanager import CONFIG
import feed
import downloader
import db
import historywin
import feed_history
import taskbar
import optionsdlg


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

    def ShowOptions(self):
        dlg = optionsdlg.OptionsDialog(self)

        if wx.ID_OK == dlg.ShowModal():
            dlg.CommitChanges()
            CONFIG.save()

    def OnUpdateTimer(self, evt):
        #print "Updating"
        wx.GetApp().download_items()
            
    def ShowDownloadHistory(self):
        self.history.Show()
        self.history.Raise()

    def ToggleDownloadHistory(self):
        if self.history.IsShown():
            self.history.Hide()
        else:
            self.ShowFeedHistory()

    def ShowFeedHistory(self):
        self.feed_history.Show()
        self.feed_history.Raise()

    def OnCloseWindow(self, event):
        self.timer.Stop()
        del self.timer

        if self.tbicon is not None:
            self.tbicon.Destroy()
            self.tbicon = None

        self.Destroy()

    def NewTorrentDownloaded(self, found):
        #TODO: Also need to update the feed history to add the downloaded icon to the relevant row

        self.feed_history.UpdateTorrentDownloaded(found)
        self.history.NewTorrentDownloaded(found)

    def NewTorrentSeen(self, seen):
        self.feed_history.NewTorrentSeen(seen)


class RssDownloaderApp(wx.App):
    def OnInit(self):
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
                self.download_torrent_entry(entry)

    def check_feed_entry(self, entry, matches):
        """Check a feed entry for a match against MATCH_TORRENTS"""

        for match_regexp in CONFIG.get_key('MATCH_TORRENTS'):
            match = re.match(match_regexp, entry['title'])

            # If it matches a regular expression, 
            if match:
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
            db_entry = db.Torrent(entry['title'], entry['link'])

            if not self.db.save_torrent(db_entry):
                print 'ERROR: Unable to commit feed entry name %s' % entry['title']
                sys.exit(1)

            self.mainwindow.NewTorrentSeen(db_entry)
            
            return True
        else:
            return False


    def find_matches(self):
        """Find all entries that match a regular expression in MATCH_TORRENTS"""

        matches = defaultdict(list)

        for rss_feed_url in CONFIG.get_key('FEED_URLS'):
            for entry in feed.get_rss_feed_entries(rss_feed_url):
                # check each new entry
                if self.add_entry_to_history(entry):
                    print "NEW!: %s" % entry['title']
                    self.check_feed_entry(entry, matches)

        return matches

    def download_torrent(self, title, link):
        try:
            found = self.db.query_torrents().filter_by(name=title).one()
        except NoResultFound:
            print "ERROR: Torrent downloaded but not already in database. (%s)" % title
            sys.exit(1)

        self.download_db_torrent(found)

    def download_db_torrent(self, torrent):
        if torrent.downloaded:
            # already downloaded
            return

        if not downloader.add_torrent_to_client(torrent.name, torrent.download_link):
            print 'ERROR: Unable to commit torrent name %s' % torrent.name
            sys.exit(1)

        torrent.downloaded = True 

        self.db.save_torrent(torrent)

        print 'Downloaded "%s"' % torrent.name

        self.mainwindow.NewTorrentDownloaded(torrent)

    def download_torrent_entry(self, entry):
        self.download_torrent(entry['title'], entry['link'])

    def test_matches(self):
        torrents = wx.GetApp().db.query_torrents().order_by(db.Torrent.first_seen.desc()).all()
        downloaded_count = wx.GetApp().db.query_torrents().filter_by(downloaded=True).count()

        matches = defaultdict(list)
        found_list = []

        for torrent in torrents:
            entry = {'title': torrent.name, 'link': torrent.download_link}
            self.check_feed_entry(entry, matches)

        for key, entry_list in matches.iteritems():
            for entry in entry_list:
                try:
                    found = self.db.query_torrents().filter_by(name=entry['title']).one()
                except NoResultFound:
                    continue
                else:
                    if found.downloaded == False:
                        found_list.append(found)
                        print found.name

        if not found_list:
            wx.MessageBox('Found no new matches', 'Test results', wx.OK|wx.ICON_INFORMATION)
            return

        message = 'Download the %d new matches?:\n\n' % len(found_list)
        message += '\n'.join((x.name for x in found_list))
    
        result = wx.MessageBox(message, 'Test Results', wx.YES_NO|wx.ICON_QUESTION)
        
        if result == wx.YES:
            for found in found_list:
                # Download the torrent
                self.download_db_torrent(found)



if __name__ == '__main__':
    app = RssDownloaderApp(False)
    app.MainLoop()
    CONFIG.save()


