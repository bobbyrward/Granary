import logging

import wx


log = logging.getLogger(__name__)


class FeedHistoryStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(1)

    def SetTorrentCount(self, count):
        log.info('Setting torrent count to %d', count)
        self.SetStatusText("%d torrents" % count, 0)
