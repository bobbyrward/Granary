import logging

import wx

from granary import db
from granary.feed_checker import EVT_NEW_TORRENT_SEEN
from granary.download_queue import EVT_TORRENT_DOWNLOADED
from granary.ui.feed_history_list import FeedHistoryList
from granary.ui.feed_history_list import EVT_TORRENT_ACTIVATED


log = logging.getLogger('granary.ui.feed_history')


class FeedHistoryWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1,
                "Rss Downloader Feed History",
                size=(700, 768),
                style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetIcon(wx.GetApp().icon)

        self.list = FeedHistoryList(self, -1)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        torrents = wx.GetApp().db.query_torrents().order_by(
                db.Torrent.first_seen.desc()).limit(500).all()

        self.list.DeleteAllItems()

        for index, downloaded in enumerate(torrents):
            self.list.InsertTorrent(index, downloaded)

        self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        self.Bind(EVT_TORRENT_ACTIVATED, self.OnTorrentActivated, self.list)
        wx.GetApp().Bind(EVT_NEW_TORRENT_SEEN, self.OnNewTorrentSeen)
        wx.GetApp().Bind(EVT_TORRENT_DOWNLOADED, self.OnTorrentDownloaded)

    def OnTorrentActivated(self, evt):
        log.debug('Calling download_torrent for %s', evt.torrent)

        wx.GetApp().download_queue.queue_torrent(evt.torrent)

    def OnTorrentDownloaded(self, evt):
        evt.Skip()

        self.list.UpdateTorrentStatus(evt.torrent)

    def OnNewTorrentSeen(self, evt):
        evt.Skip()

        self.list.InsertTorrent(0, evt.torrent)
        self.list.resizeLastColumn(128)

    def OnCloseWindow(self, evt):
        self.Hide()
