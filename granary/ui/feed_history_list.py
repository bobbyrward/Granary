import logging

import wx
from wx.lib.newevent import NewCommandEvent
import wx.lib.mixins.listctrl as listmix

from granary import db


(TorrentActivatedEvent, EVT_TORRENT_ACTIVATED) = NewCommandEvent()


log = logging.getLogger('granary.ui.feed_history_list')


class FeedHistoryList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID):
        wx.ListCtrl.__init__(self, parent, ID, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_HRULES | wx.LC_SINGLE_SEL)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        check = wx.GetApp().load_app_image('check.png')

        self.image_list = wx.ImageList(16, 16)
        self.image_list.Add(check.ConvertToBitmap())
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        self.item_data = {}
        self.reverse_item_data = {}

        self.InsertColumn(0, "")
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "First Seen", wx.LIST_FORMAT_RIGHT)

        self.setResizeColumn(2)

        self.SetColumnWidth(0, 24)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self)

    def InsertTorrent(self, index, torrent):
        if torrent.downloaded:
            self.InsertImageItem(index, 0)
        else:
            self.InsertStringItem(index, '')

        id = wx.NewId()
        self.item_data[id] = torrent.name
        self.reverse_item_data[torrent.name] = id
        self.SetItemData(index, id)

        self.SetStringItem(index, 1, torrent.name)
        self.SetStringItem(index, 2, torrent.first_seen.strftime('%m/%d/%Y %I:%M %p'))

    def UpdateTorrentStatus(self, torrent):
        log.debug("Updating download status of %s to %s", torrent.name, torrent.downloaded)

        id = self.reverse_item_data[torrent.name]
        index = self.FindItemData(-1, id)

        if torrent.downloaded:
            self.SetItemImage(index, 0)
        else:
            self.SetStringItem(index, '')

    def OnItemActivated(self, evt):
        log.debug("OnItemActivated item data = %s", evt.GetData())

        try:
            torrent_name = self.item_data[evt.GetData()]
        except KeyError:
            return

        log.debug("found torrent in cache: %s", torrent_name)

        torrent = wx.GetApp().db.get_torrent(torrent_name)

        sub_event = TorrentActivatedEvent(self.GetId())
        sub_event.SetEventObject(self)
        sub_event.torrent = torrent

        log.debug("sending EVT_TORRENT_ACTIVATED event")

        self.GetEventHandler().ProcessEvent(sub_event)
