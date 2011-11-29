import wx
import db
import wx.lib.mixins.listctrl as listmix


class FeedHistoryList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, "")
        self.InsertColumn(1, "Name")
        self.InsertColumn(2, "First Seen", wx.LIST_FORMAT_RIGHT)

        self.setResizeColumn(2)

        self.SetColumnWidth(0, 24)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        self.SetColumnWidth(2, wx.LIST_AUTOSIZE)

class FeedHistoryWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Rss Downloader Feed History", size = (700,768),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        img = wx.Image('16-rss-square.png', wx.BITMAP_TYPE_PNG)
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        self.SetIcon(icon)

        self.list = FeedHistoryList(self, -1, 
                style=wx.LC_REPORT
                     |wx.BORDER_NONE
                     #|wx.LC_VRULES
                     |wx.LC_HRULES
                     |wx.LC_SINGLE_SEL)

        self.image_list = wx.ImageList(16, 16)

        check = wx.Image('check.png', wx.BITMAP_TYPE_PNG)
        self.image_list.Add(check.ConvertToBitmap())

        self.list.SetImageList(self.image_list, wx.IMAGE_LIST_SMALL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        torrents = wx.GetApp().db.query_torrents().order_by(
                db.Torrent.downloaded.desc()).limit(500).all()

        self.list.DeleteAllItems()

        for idx, downloaded in enumerate(torrents):
            if downloaded.downloaded:
                self.list.InsertImageItem(idx, 0)
            else:
                self.list.InsertStringItem(idx, '')

            self.list.SetStringItem(idx, 1, downloaded.name)
            self.list.SetStringItem(idx, 2, downloaded.first_seen.strftime('%m/%d/%Y %I:%M %p'))

        self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
        #self.list.resizeLastColumn(128)

    def NewTorrentSeen(self, torrent):
        if torrent.downloaded:
            self.list.InsertImageItem(0, 0)
        else:
            self.list.InsertStringItem(0, '')

        self.list.SetStringItem(0, 1, torrent.name)
        self.list.SetStringItem(0, 2, torrent.first_seen.strftime('%m/%d/%Y %I:%M %p'))

        self.list.resizeLastColumn(128)

    def OnCloseWindow(self, evt):
        self.Hide()




