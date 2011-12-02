import os

import wx

from granary.configmanager import CONFIG
from granary.ui import historywin
from granary.ui import feed_history
from granary.ui import taskbar
from granary.ui import optionsdlg


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Rss Downloader", size = (64,64),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        img = wx.GetApp().load_app_image('16-rss-square.png')
        icon = wx.IconFromBitmap(img.ConvertToBitmap() )
        self.SetIcon(icon)

        try:
            self.tbicon = taskbar.RssDownloaderTaskBarIcon(self)
        except:
            self.tbicon = None

        self.history = historywin.HistoryWindow(self)
        self.feed_history = feed_history.FeedHistoryWindow(self)
        self.timer = wx.Timer(self)
        self.timer.Start(1000 * 60)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(wx.EVT_TIMER, self.OnUpdateTimer, self.timer)

    def ShowOptions(self):
        dlg = optionsdlg.OptionsDialog(self)

        if wx.ID_OK == dlg.ShowModal():
            feed_count_pre = len(CONFIG.get_key('FEED_URLS'))
            regexp_count_pre = len(CONFIG.get_key('MATCH_TORRENTS'))
            dlg.CommitChanges()
            CONFIG.save()
            regexp_count_post = len(CONFIG.get_key('MATCH_TORRENTS'))
            feed_count_post = len(CONFIG.get_key('FEED_URLS'))

            if feed_count_pre < feed_count_post:
                # update the history before going further
                wx.GetApp().download_items()

            if regexp_count_pre < regexp_count_post:
                result = wx.MessageBox("Match Regexps have changed.  Would you like to run the updated list against the history and download any matches?", 
                        "Test matches", wx.YES_NO|wx.ICON_QUESTION)

                if result == wx.YES:
                    wx.GetApp().test_matches()

            if CONFIG.get_key('ENABLE_GROWL'):
                wx.GetApp().growler.register()

    def OnUpdateTimer(self, evt):
        #print "Updating"
        wx.GetApp().download_items()
            
    def ShowDownloadHistory(self):
        self.history.Show()
        self.history.Raise()

    def ToggleDownloadHistory(self):
        if self.history.IsShown():
            self.history.Hide()
        else:
            self.ShowFeedHistory()

    def ShowFeedHistory(self):
        self.feed_history.Show()
        self.feed_history.Raise()

    def OnCloseWindow(self, event):
        self.timer.Stop()
        del self.timer

        if self.tbicon is not None:
            self.tbicon.Destroy()
            self.tbicon = None

        self.Destroy()

    def NewTorrentDownloaded(self, found):
        #TODO: Also need to update the feed history to add the downloaded icon to the relevant row

        self.feed_history.UpdateTorrentDownloaded(found)
        self.history.NewTorrentDownloaded(found)

    def NewTorrentSeen(self, seen):
        self.feed_history.NewTorrentSeen(seen)

