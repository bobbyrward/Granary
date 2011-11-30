import wx
import db
import wx.lib.mixins.listctrl as listmix


class HistoryList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Date Downloaded", wx.LIST_FORMAT_RIGHT)

        self.setResizeColumn(0)
        self.SetColumnWidth(0, 128)
        self.SetColumnWidth(1, wx.LIST_AUTOSIZE)

class HistoryWindow(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, "Rss Downloader History", size = (560,768),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        img = wx.Image('16-rss-square.png', wx.BITMAP_TYPE_PNG)
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        self.SetIcon(icon)

        self.list = HistoryList(self, -1, 
                style=wx.LC_REPORT
                     |wx.BORDER_NONE
                     #|wx.LC_VRULES
                     |wx.LC_HRULES
                     |wx.LC_SINGLE_SEL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        torrents = wx.GetApp().db.query_torrents().filter_by(downloaded=True).order_by(
                db.Torrent.first_seen.desc()).all()

        self.list.DeleteAllItems()

        for idx, downloaded in enumerate(torrents):
            self.list.InsertStringItem(idx, downloaded.name)
            self.list.SetStringItem(idx, 1, downloaded.first_seen.strftime('%m/%d/%Y %I:%M %p'))

        self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        #self.list.resizeLastColumn(128)

    def NewTorrentDownloaded(self, torrent):
        self.list.InsertStringItem(0, torrent.name)
        self.list.SetStringItem(0, 1, torrent.first_seen.strftime('%m/%d/%Y %I:%M %p'))
        self.list.SetColumnWidth(1, wx.LIST_AUTOSIZE)

    def OnCloseWindow(self, evt):
        self.Hide()



