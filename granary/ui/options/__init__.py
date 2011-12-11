import logging
import wx

from granary.configmanager import config
from granary.ui.listeditor import ListEditorCtrl
from granary.ui.options.downloading import DownloadOptionsPanel
from granary.ui.options.growl import GrowlOptionsPanel


log = logging.getLogger(__name__)


class OptionsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Rss Downloader Options", size=(700, 700))

        notebook = wx.Notebook(self, -1)

        self.integration_panel = DownloadOptionsPanel(notebook)
        notebook.AddPage(self.integration_panel, "Integration Method")

        self.rss_feed_list_editor = ListEditorCtrl(notebook, "Feed URLs", config().get_key("FEED_URLS"), size=(500, 200))
        notebook.AddPage(self.rss_feed_list_editor, "Feed URLs")

        self.match_regexp_list_editor = ListEditorCtrl(notebook, "Match Regexps", config().get_key("MATCH_TORRENTS"))
        notebook.AddPage(self.match_regexp_list_editor, "Match Regexps")

        self.growl_panel = GrowlOptionsPanel(notebook)
        notebook.AddPage(self.growl_panel, "Growl")

        okbutton = wx.Button(self, wx.ID_OK)
        okbutton.SetDefault()

        cancelbutton = wx.Button(self, wx.ID_CANCEL)

        dlgsizer = wx.StdDialogButtonSizer()
        dlgsizer.AddButton(okbutton)
        dlgsizer.AddButton(cancelbutton)
        dlgsizer.Realize()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(dlgsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)

    def CommitChanges(self):
        self.integration_panel.CommitChanges()
        self.growl_panel.CommitChanges()
        config().set_key("FEED_URLS", self.rss_feed_list_editor.GetListItems())
        config().set_key("MATCH_TORRENTS", self.match_regexp_list_editor.GetListItems())
