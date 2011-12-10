"""A (not so) simple torrent rss feed watcher
"""
import logging


log = logging.getLogger('granary')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
handler.setFormatter(formatter)

log.addHandler(handler)


import re
import sys
import os
from collections import defaultdict

from twisted.internet import wxreactor
wxreactor.install()

from twisted.internet import reactor
import wx

from granary import db
from granary.configmanager import ConfigManager, config
from granary.ui import mainwin
from granary.integration import growler
from granary.feed_checker import FeedChecker
from granary.feed_checker import EVT_NEW_TORRENT_SEEN
from granary.download_queue import DownloadQueue
from granary.download_queue import EVT_TORRENT_DOWNLOADED


class RssDownloaderApp(wx.App):
    def OnInit(self):
        self.SetAppName("rss_downloader")

        # For debugging
        self.SetAssertMode(wx.PYAPP_ASSERT_DIALOG)

        # initialize config before anything else
        self.Config = ConfigManager()

        reactor.registerWxApp(self)

        self.Bind(EVT_NEW_TORRENT_SEEN, self.OnNewTorrentSeen)
        self.Bind(EVT_TORRENT_DOWNLOADED, self.OnTorrentDownloaded)

        self.growler = growler.Growler()

        self.db_engine = db.Database()
        self.db_engine.connect()
        self.db_engine.init()

        self.db = db.DBSession()

        self.icon = wx.IconFromBitmap(self.load_app_image('16-rss-square.png').ConvertToBitmap())

        self.feed_checker = FeedChecker()
        self.download_queue = DownloadQueue()

        self.download_queue.run()
        self.feed_checker.run()

        self.mainwindow = mainwin.MainWindow()

        self.mainwindow.Bind(wx.EVT_CLOSE, self.Shutdown)

        return True

    def Shutdown(self, evt):
        evt.Skip()

        log.debug('Shutting down')
        self.feed_checker.stop()
        self.download_queue.stop()
        reactor.stop()

    def OnNewTorrentSeen(self, evt):
        evt.Skip()

        # send the growl notification if enabled
        if config().get_key('ENABLE_GROWL') and config().get_key('ENABLE_GROWL_NEW_TORRENT_NOTIFICATION'):
            self.growler.send_new_torrent_notification(evt.torrent)

        #self.mainwindow.tbicon.ShowBalloon(
        #        "New torrent",
        #        "%s seen" % evt.torrent.name,
        #        1 * 1000,
        #        wx.ICON_INFORMATION)

        # I like knowing when it sees new torrents.
        # NOTE: should find a better way to do this and eliminate output where I can
        log.info('NEW: %s', evt.torrent.name)

    def OnTorrentDownloaded(self, evt):
        evt.Skip()

        # send the growl notification if enabled
        if config().get_key('ENABLE_GROWL') and config().get_key('ENABLE_GROWL_DOWNLOAD_NOTIFICATION'):
            self.growler.send_download_notification(evt.torrent)

        self.mainwindow.tbicon.ShowBalloon(
                "New torrent downloaded",
                "%s was downloaded" % evt.torrent.name,
                1 * 1000,
                wx.ICON_INFORMATION)

        log.info('Downloaded "%s"', evt.torrent.name)

    def load_app_image(self, filename):
        log.debug('loading app image: %s', filename)

        path = os.path.join(config().get_app_path(), 'res', filename)

        if not os.path.exists(path):
            log.error('load_app_image: %s does not exist', filename)

        assert os.path.exists(path)

        return wx.Image(path, wx.BITMAP_TYPE_PNG)


if __name__ == '__main__':
    app = RssDownloaderApp(False)
    reactor.run()
    config().save()
    log.debug('Exiting')
