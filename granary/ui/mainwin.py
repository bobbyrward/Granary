import os

import wx

from granary.configmanager import config
from granary.ui import historywin
from granary.ui import feed_history
from granary.ui import taskbar
from granary.ui import optionsdlg


class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Rss Downloader", size=(64, 64),
                  style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.SetIcon(wx.GetApp().icon)

        try:
            self.tbicon = taskbar.RssDownloaderTaskBarIcon(self)
        except:
            self.tbicon = None

        self.feed_history = feed_history.FeedHistoryWindow(self)

        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def ShowOptions(self):
        dlg = optionsdlg.OptionsDialog(self)

        if wx.ID_OK == dlg.ShowModal():
            feed_count_pre = len(config().get_key('FEED_URLS'))
            regexp_count_pre = len(config().get_key('MATCH_TORRENTS'))

            dlg.CommitChanges()
            config().save()

            regexp_count_post = len(config().get_key('MATCH_TORRENTS'))
            feed_count_post = len(config().get_key('FEED_URLS'))

            if feed_count_pre < feed_count_post:
                # update the history before going further
                #TODO: This needs to be made with the new threaded downloader
                #wx.GetApp().downloader.tick()
                pass

            if regexp_count_pre < regexp_count_post:
                result = wx.MessageBox(
                        "Match Regexps have changed.  " +
                        "Would you like to run the updated list " +
                        "against the history and download any matches?",
                        "Test matches", wx.YES_NO | wx.ICON_QUESTION)

                if result == wx.YES:
                    pass
                    #TODO: This needs to be made with the new threaded downloader
                    #wx.GetApp().downloader.test_regular_expressions()

    def ToggleFeedistory(self):
        if self.feed_history.IsShown():
            self.feed_history.Hide()
        else:
            self.ShowFeedHistory()

    def ShowFeedHistory(self):
        self.feed_history.Show()
        self.feed_history.Raise()

    def OnCloseWindow(self, event):
        if self.tbicon is not None:
            self.tbicon.Destroy()
            self.tbicon = None

        self.Destroy()
