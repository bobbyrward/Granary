import wx


class RssDownloaderTaskBarIcon(wx.TaskBarIcon):
    TBMENU_FEED_HISTORY = wx.NewId()
    TBMENU_SHOW_OPTIONS = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame

        # Set the image
        icon = self.MakeIcon(wx.GetApp().load_app_image('16-rss-square.png'))

        self.SetIcon(icon, "Rss Downloader")
        self.imgidx = 1

        # bind some events
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarToggleFeedHistory)
        self.Bind(wx.EVT_MENU, self.OnTaskBarShowFeedHistory, id=self.TBMENU_FEED_HISTORY)
        self.Bind(wx.EVT_MENU, self.OnTaskBarShowOptions, id=self.TBMENU_SHOW_OPTIONS)
        self.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=self.TBMENU_CLOSE)

    def CreatePopupMenu(self):
        """
        This method is called by the base class when it needs to popup
        the menu for the default EVT_RIGHT_DOWN event.  Just create
        the menu how you want it and return it from this function,
        the base class takes care of the rest.
        """
        menu = wx.Menu()
        menu.Append(self.TBMENU_FEED_HISTORY, "Show &History")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_SHOW_OPTIONS, "&Options")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "E&xit")
        return menu

    def MakeIcon(self, img):
        """
        The various platforms have different requirements for the
        icon size...
        """
        if "wxMSW" in wx.PlatformInfo:
            img = img.Scale(16, 16)
        elif "wxGTK" in wx.PlatformInfo:
            img = img.Scale(22, 22)
        # wxMac can be any size upto 128x128, so leave the source img alone....
        icon = wx.IconFromBitmap(img.ConvertToBitmap())
        return icon

    def OnTaskBarClose(self, evt):
        wx.CallAfter(self.frame.Close)

    def OnTaskBarShowFeedHistory(self, evt):
        wx.CallAfter(self.frame.ShowFeedHistory)

    def OnTaskBarToggleFeedHistory(self, evt):
        wx.CallAfter(self.frame.ToggleFeedistory)

    def OnTaskBarShowOptions(self, evt):
        wx.CallAfter(self.frame.ShowOptions)
