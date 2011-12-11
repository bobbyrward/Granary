import logging

import wx

from granary import db
from granary.feed_checker import EVT_NEW_TORRENT_SEEN
from granary.download_queue import EVT_TORRENT_DOWNLOADED
from granary.ui.history.list import FeedHistoryList
from granary.ui.history.list import EVT_TORRENT_ACTIVATED
from granary.ui.history.list import EVT_SORT_ORDER_CHANGED
from granary.ui.history.status_bar import FeedHistoryStatusBar
from granary.ui.history.search import HistorySearch
from granary.ui.history.search import EVT_SEARCH_PERFORM
from granary.ui.history.search import EVT_SEARCH_CLEAR


log = logging.getLogger(__name__)


class FeedHistoryWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1,
                "Rss Downloader Feed History",
                size=(700, 768),
                style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetIcon(wx.GetApp().icon)

        self.list = FeedHistoryList(self, -1)
        self.status_bar = FeedHistoryStatusBar(self)
        self.SetStatusBar(self.status_bar)

        self.search = HistorySearch(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search, 0, wx.EXPAND)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        self.query = None
        self.order_by = (db.Torrent.first_seen.desc(), db.Torrent.name.asc(), db.Torrent.downloaded.desc())
        self.terms = []
        self.ResetQuery()

        self.Bind(EVT_TORRENT_ACTIVATED, self.OnTorrentActivated, self.list)
        self.Bind(EVT_SORT_ORDER_CHANGED, self.OnSortOrderChanged, self.list)
        self.Bind(EVT_SEARCH_CLEAR, self.OnClearSearch, self.search)
        self.Bind(EVT_SEARCH_PERFORM, self.OnPerformSearch, self.search)

        wx.GetApp().Bind(EVT_NEW_TORRENT_SEEN, self.OnNewTorrentSeen)
        wx.GetApp().Bind(EVT_TORRENT_DOWNLOADED, self.OnTorrentDownloaded)

    def GetBaseQuery(self):
        return wx.GetApp().db.query_torrents()

    def ResetQuery(self):
        self.query = self.GetBaseQuery()
        self.terms = []
        self.RefreshResults()

    def RefreshResults(self):
        self.status_bar.SetTorrentCount(self.query.count())

        self.list.DeleteAllItems()

        for index, torrent in enumerate(self.query.order_by(*self.order_by).limit(500).all()):
            self.list.InsertTorrent(index, torrent)

        self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)

    def OnClearSearch(self, evt):
        if len(self.terms) == 0:
            # already cleared
            return

        self.ResetQuery()

    def OnPerformSearch(self, evt):
        like_filter = '%%%s%%' % '%'.join(evt.terms)

        log.debug('Search filter: %s', like_filter)

        if self.terms == evt.terms:
            # already using these terms
            return

        self.terms = evt.terms

        self.query = self.GetBaseQuery().filter(db.Torrent.name.like(like_filter))
        self.RefreshResults()

    def OnTorrentActivated(self, evt):
        log.debug('Calling download_torrent for %s', evt.torrent)

        wx.GetApp().download_queue.queue_torrent(evt.torrent)

    def OnSortOrderChanged(self, evt):
        log.debug('Sorting list by %s %s', evt.sort_column, 'desc' if evt.sort_direction == -1 else 'asc')

        column = getattr(db.Torrent, evt.sort_column[0])
        columns = []

        if evt.sort_direction == -1:
            columns.append(column.desc())
        else:
            columns.append(column.desc())

        default_direction_mapping = {
            'downloaded': 'desc',
            'name': 'asc',
            'first_seen': 'desc',
        }

        columns.append(getattr(getattr(db.Torrent, evt.sort_column[1]), default_direction_mapping[evt.sort_column[1]])())
        columns.append(getattr(getattr(db.Torrent, evt.sort_column[2]), default_direction_mapping[evt.sort_column[2]])())

        self.order_by = columns

        self.RefreshResults()

    def OnTorrentDownloaded(self, evt):
        evt.Skip()

        self.list.UpdateTorrentStatus(evt.torrent)

    def OnNewTorrentSeen(self, evt):
        evt.Skip()

        if len(self.terms) != 0:
            for term in self.terms:
                if not evt.torrent.name.lower().contains(term):
                    # torrent doesn't match current search
                    log.debug('New torrent "%s" does not match current terms "%s"', evt.torrent.name, ' '.join(self.terms))
                    return

        log.debug('New torrent "%s" matches current terms "%s"', evt.torrent.name, ' '.join(self.terms))

        #TODO: This is nasty.  Find a way to insert this in the list in the proper spot
        self.RefreshResults()

        #self.list.InsertTorrent(0, evt.torrent)
        #self.list.resizeLastColumn(128)

    def OnCloseWindow(self, evt):
        self.Hide()
