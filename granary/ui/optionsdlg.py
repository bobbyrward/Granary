import wx
import  wx.lib.filebrowsebutton as filebrowse

from granary.configmanager import config
from granary.downloader import TORRENT_INTEGRATION_METHODS
from granary.ui.listeditor import ListEditorCtrl


class IntegrationOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.integration_methods = sorted(TORRENT_INTEGRATION_METHODS.keys())

        labels = [TORRENT_INTEGRATION_METHODS[x] for x in self.integration_methods]

        self.integration_box = wx.RadioBox(self, -1, 'Integration Method', choices=labels, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.integration_box.SetStringSelection(TORRENT_INTEGRATION_METHODS[config().get_key('TORRENT_INTEGRATION_METHOD')])
        self.Bind(wx.EVT_RADIOBOX, self.OnIntegrationMethodChanged, self.integration_box)

        watch_box = wx.StaticBox(self, -1, "Torrent Watch Directory")
        watch_box_sizer = wx.StaticBoxSizer(watch_box, wx.VERTICAL)

        self.download_directory = filebrowse.DirBrowseButton(self, -1, 
                labelText='',
                toolTip="Select the directory to download torrents to",
                changeCallback=self.OnDownloadDirectoryChanged,
                startDirectory=config().get_key("DOWNLOAD_DIRECTORY"),
                newDirectory=True,
                )
    
        self.download_directory.SetValue(config().get_key("DOWNLOAD_DIRECTORY"))

        watch_box_sizer.Add(self.download_directory, 0, wx.EXPAND|wx.ALL, 5)

        deluge_web_ui_box = wx.StaticBox(self, -1, "Deluge WebUI Options")
        deluge_web_ui_box_sizer = wx.StaticBoxSizer(deluge_web_ui_box, wx.VERTICAL)

        self.webui_url = wx.TextCtrl(self, -1, value=config().get_key('DELUGE_WEB_UI_URL'))
        self.webui_password = wx.TextCtrl(self, -1, value=config().get_key('DELUGE_WEB_UI_PASSWORD'))

        webui_sizer = wx.GridBagSizer(5, 5)
        webui_sizer.Add(wx.StaticText(self, -1, "WebUI Url"), (0, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL)
        webui_sizer.Add(self.webui_url, (0, 1), (1, 1), wx.EXPAND)
        webui_sizer.Add(wx.StaticText(self, -1, "WebUI Password"), (1, 0), (1, 1), wx.ALIGN_CENTER_VERTICAL)
        webui_sizer.Add(self.webui_password, (1, 1), (1, 1), wx.EXPAND)
        webui_sizer.AddGrowableCol(1)
    
        deluge_web_ui_box_sizer.Add(webui_sizer, 0, wx.EXPAND|wx.ALL, 5)

        self.OnIntegrationMethodChanged(None, self.integration_box.GetSelection())

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.integration_box, 0, wx.EXPAND|wx.ALL, 10)
        sizer.Add(watch_box_sizer, 0, wx.EXPAND|wx.ALL, 10)
        sizer.Add(deluge_web_ui_box_sizer, 0, wx.EXPAND|wx.ALL, 10)
        self.SetSizer(sizer)

    def OnIntegrationMethodChanged(self, evt=None, index=-1):
        if evt is not None:
            index = evt.GetInt()

        print 'Selected %s' % self.integration_methods[index]
        method = self.integration_methods[index]

        self.download_directory.Enabled = method == 'WATCH_FOLDER'
        self.webui_url.Enabled          = method == 'DELUGE_WEB_UI'
        self.webui_password.Enabled     = method == 'DELUGE_WEB_UI'

    def OnDownloadDirectoryChanged(self, evt):
        print 'DirBrowseButton: %s\n' % evt.GetString()

    def CommitChanges(self):
        config().set_key('TORRENT_INTEGRATION_METHOD', self.integration_methods[self.integration_box.GetSelection()])
        config().set_key('DOWNLOAD_DIRECTORY', self.download_directory.GetValue())
        config().set_key('DELUGE_WEB_UI_URL', self.webui_url.GetValue())
        config().set_key('DELUGE_WEB_UI_PASSWORD', self.webui_password.GetValue())


class GrowlOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.enable_growl = wx.CheckBox(self, -1, "Enable Growl Support")
        self.enable_growl.SetValue(config().get_key('ENABLE_GROWL'))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.enable_growl, 0, wx.EXPAND|wx.ALL, 5)

        self.SetSizer(sizer)

    def CommitChanges(self):
        config().set_key('ENABLE_GROWL', self.enable_growl.GetValue())


class OptionsDialog(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Rss Downloader Options", size=(700, 700))

        notebook = wx.Notebook(self, -1)

        self.integration_panel = IntegrationOptionsPanel(notebook)
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
        sizer.Add(notebook, 1, wx.EXPAND|wx.ALL, 5)
        sizer.Add(dlgsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)

    def CommitChanges(self):
        self.integration_panel.CommitChanges()
        self.growl_panel.CommitChanges()
        config().set_key("FEED_URLS", self.rss_feed_list_editor.GetListItems())
        config().set_key("MATCH_TORRENTS", self.match_regexp_list_editor.GetListItems())


if __name__ == '__main__':
    app = wx.App(redirect=False)
    main = OptionsDialog(None)
    result = main.ShowModal()

    if result == wx.ID_OK:
        main.CommitChanges()
        config().save()

