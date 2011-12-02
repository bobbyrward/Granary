import re
import sys
import os
from collections import defaultdict

import wx

from granary import db
from granary.configmanager import ConfigManager, config
from granary.ui import mainwin
from granary.integration import growler
from granary.feeddownloader import FeedDownloader


class RssDownloaderApp(wx.App):
    def OnInit(self):
        self.SetAppName("rss_downloader")

        # For debugging
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

        # initialize config before anything else
        self.Config = ConfigManager()

        self.growler = growler.Growler()
        self.db = db.Database()
        self.db.connect()

        self.icon = wx.IconFromBitmap(self.load_app_image('16-rss-square.png').ConvertToBitmap())

        self.downloader = FeedDownloader()

        self.mainwindow = mainwin.MainWindow()

        # Force an update at load time
        self.downloader.tick()

        return True

    def OnNewTorrentSeen(self, torrent):
        # I like knowing when it sees new torrents.
        # NOTE: should find a better way to do this and eliminate output where I can
        print 'NEW: %s' % torrent.name

        self.mainwindow.NewTorrentSeen(torrent)

    def OnTorrentDownloaded(self, torrent):
        # send the growl notification if enabled
        if config().get_key('ENABLE_GROWL'):
            self.growler.send_download_notification(torrent)

        #print 'Downloaded "%s"' % torrent.name

        # let the main window know about the torrent
        self.mainwindow.NewTorrentDownloaded(torrent)

    def load_app_image(self, filename):
        path = os.path.join(config().get_app_path(), 'res', filename)

        assert os.path.exists(path)

        return wx.Image(path, wx.BITMAP_TYPE_PNG)


if __name__ == '__main__':
    app = RssDownloaderApp(False)
    app.MainLoop()
    config().save()
