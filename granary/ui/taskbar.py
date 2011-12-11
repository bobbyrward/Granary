import logging

import wx


log = logging.getLogger(__name__)


try:
    import win32gui
    HAS_WIN32GUI = True
    log.info('Found pywin32.  Using native balloon tips')
except Exception:
    HAS_WIN32GUI = False
    log.info('pywin32 not found')


class RssDownloaderTaskBarIcon(wx.TaskBarIcon):
    TBMENU_FEED_HISTORY = wx.NewId()
    TBMENU_SHOW_OPTIONS = wx.NewId()
    TBMENU_CLOSE = wx.NewId()

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.icon = None
        self.tooltip = ""

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
        menu = wx.Menu()
        menu.Append(self.TBMENU_FEED_HISTORY, "Show &History")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_SHOW_OPTIONS, "&Options")
        menu.AppendSeparator()
        menu.Append(self.TBMENU_CLOSE, "E&xit")
        return menu

    def OnTaskBarClose(self, evt):
        wx.CallAfter(wx.GetApp().DoExit)

    def OnTaskBarShowFeedHistory(self, evt):
        wx.CallAfter(self.frame.ShowFeedHistory)

    def OnTaskBarToggleFeedHistory(self, evt):
        wx.CallAfter(self.frame.ToggleFeedistory)

    def OnTaskBarShowOptions(self, evt):
        wx.CallAfter(self.frame.ShowOptions)

    def ShowBalloon(self, title, text, msec=10, flags=0):
        """
        Show Balloon tooltip
         @param title - Title for balloon tooltip
         @param msg   - Balloon tooltip text
         @param msec  - Timeout for balloon tooltip, in milliseconds
         @param flags -  one of wx.ICON_INFORMATION, wx.ICON_WARNING, wx.ICON_ERROR
        """
        if HAS_WIN32GUI and self.IsIconInstalled():
            try:
                log.info('Showing balloon tip: %s', text)
                self._SetBalloonTip(self.icon.GetHandle(), title, text, msec, flags)
            except Exception:
                log.exception('Error showing balloon tip')

    def _SetBalloonTip(self, hicon, title, msg, msec, flags):
        # translate flags
        infoFlags = 0

        if flags & wx.ICON_INFORMATION:
            infoFlags |= win32gui.NIIF_INFO
        elif flags & wx.ICON_WARNING:
            infoFlags |= win32gui.NIIF_WARNING
        elif flags & wx.ICON_ERROR:
            infoFlags |= win32gui.NIIF_ERROR

        # Show balloon
        lpdata = (self._GetIconHandle(),   # hWnd
                  99,                       # ID
                  win32gui.NIF_MESSAGE | win32gui.NIF_INFO | win32gui.NIF_ICON,  # flags: Combination of NIF_* flags
                  0,                        # CallbackMessage: Message id to be pass to hWnd when processing messages
                  hicon,                    # hIcon: Handle to the icon to be displayed
                  '',                       # Tip: Tooltip text
                  msg,                      # Info: Balloon tooltip text
                  msec,                     # Timeout: Timeout for balloon tooltip, in milliseconds
                  title,                    # InfoTitle: Title for balloon tooltip
                  infoFlags                 # InfoFlags: Combination of NIIF_* flags
                  )

        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, lpdata)

        self.SetIcon(self.icon, self.tooltip)   # Hack: because we have no access to the real CallbackMessage value

    def _GetIconHandle(self):
        """
        Find the icon window.
        This is ugly but for now there is no way to find this window directly from wx
        """
        if not hasattr(self, "_chwnd"):
            try:
                for handle in wx.GetTopLevelWindows():
                    if handle.GetWindowStyle():
                        continue
                    handle = handle.GetHandle()
                    if len(win32gui.GetWindowText(handle)) == 0:
                        self._chwnd = handle
                        break
                if not hasattr(self, "_chwnd"):
                    raise Exception
            except:
                raise Exception("Icon window not found")
        return self._chwnd

    def SetIcon(self, icon, tooltip=""):
        self.icon = icon
        self.tooltip = tooltip
        wx.TaskBarIcon.SetIcon(self, icon, tooltip)

    def RemoveIcon(self, icon, tooltip=""):
        self.icon = None
        self.tooltip = ""
        wx.TaskBarIcon.RemoveIcon(self)

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
