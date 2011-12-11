import logging
import locale

import wx
from wx.lib.newevent import NewCommandEvent
import wx.lib.mixins.listctrl as listmix

from granary import db


(TorrentActivatedEvent, EVT_TORRENT_ACTIVATED) = NewCommandEvent()
(SortOrderChanged, EVT_SORT_ORDER_CHANGED) = NewCommandEvent()


log = logging.getLogger(__name__)


class FeedHistoryList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID):
        wx.ListCtrl.__init__(self, parent, ID, style=wx.LC_REPORT | wx.BORDER_NONE | wx.LC_HRULES | wx.LC_SINGLE_SEL)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        check = wx.GetApp().load_app_image('check.png')

        self.image_list = wx.ImageList(16, 16)
        self.image_list.Add(check.ConvertToBitmap())
        self.sort_up = self.image_list.Add(wx.GetApp().load_app_image('navigate_open.png').ConvertToBitmap())
        self.sort_dn = self.image_list.Add(wx.GetApp().load_app_image('navigate_close.png').ConvertToBitmap())
        self.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        self.item_data = {}
        self.reverse_item_data = {}

        self.sort_column = 2
        self.sort_direction = -1

        info = wx.ListItem()
        info.m_mask = wx.LIST_MASK_TEXT | wx.LIST_MASK_IMAGE | wx.LIST_MASK_FORMAT
        info.m_image = -1
        info.m_format = 0
        info.m_text = ""
        self.InsertColumnInfo(0, info)

        info.m_format = 0
        info.m_text = "Name"
        self.InsertColumnInfo(1, info)

        info.m_format = wx.LIST_FORMAT_RIGHT
        info.m_text = "First Seen"
        self.InsertColumnInfo(2, info)

        self.UpdateHeaderImages(-1)

        self.setResizeColumn(2)

        self.SetColumnWidth(0, 24)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated, self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick, self)

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

        try:
            id = self.reverse_item_data[torrent.name]
        except KeyError:
            return

        index = self.FindItemData(-1, id)

        if index == -1:
            # no match
            return

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

    def OnColumnClick(self, evt):
        old_column = self.sort_column
        self.sort_column = col = evt.GetColumn()

        if old_column == col:
            self.sort_direction = self.sort_direction * -1
        else:
            if col == 2:
                self.sort_direction = -1
            else:
                self.sort_direction = 1

        self.UpdateHeaderImages(old_column)

        sub_event = SortOrderChanged(self.GetId())
        sub_event.SetEventObject(self)

        if self.sort_column == 0:
            sub_event.sort_column = ('downloaded', 'first_seen', 'name')
        elif self.sort_column == 1:
            sub_event.sort_column = ('name', 'first_seen', 'downloaded')
        else:
            sub_event.sort_column = ('first_seen', 'name', 'downloaded')

        sub_event.sort_direction = self.sort_direction

        log.debug("sending EVT_SORT_ORDER_CHANGED event")

        self.GetEventHandler().ProcessEvent(sub_event)

    def UpdateHeaderImages(self, oldCol):
        images = (self.sort_dn, self.sort_up)

        img = images[0 if self.sort_direction == -1 else 1]

        if oldCol != -1:
            self.ClearColumnImage(oldCol)

        self.SetColumnImage(self.sort_column, img)
