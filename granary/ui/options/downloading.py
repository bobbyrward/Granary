import logging
import wx
import  wx.lib.filebrowsebutton as filebrowse

from granary.downloader import TORRENT_INTEGRATION_METHODS
from granary.configmanager import config


log = logging.getLogger(__name__)


class DownloadOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.integration_methods = sorted(TORRENT_INTEGRATION_METHODS.keys())

        labels = [
                TORRENT_INTEGRATION_METHODS[x]
                        for x in self.integration_methods]

        self.integration_box = wx.RadioBox(self, -1, 'Integration Method', choices=labels, majorDimension=1, style=wx.RA_SPECIFY_ROWS)
        self.integration_box.SetStringSelection(TORRENT_INTEGRATION_METHODS[config().get_key('TORRENT_INTEGRATION_METHOD')])
        self.Bind(wx.EVT_RADIOBOX, self.OnIntegrationMethodChanged, self.integration_box)

        watch_box = wx.StaticBox(self, -1, "Torrent Watch Directory")
        watch_box_sizer = wx.StaticBoxSizer(watch_box, wx.VERTICAL)

        self.download_directory = filebrowse.DirBrowseButton(self, -1,
                labelText='',
                toolTip="Select the directory to download torrents to",
                startDirectory=config().get_key("DOWNLOAD_DIRECTORY"),
                newDirectory=True,
                )

        self.download_directory.SetValue(config().get_key("DOWNLOAD_DIRECTORY"))

        watch_box_sizer.Add(self.download_directory, 0, wx.EXPAND | wx.ALL, 5)

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

        deluge_web_ui_box_sizer.Add(webui_sizer, 0, wx.EXPAND | wx.ALL, 5)

        self.OnIntegrationMethodChanged(None, self.integration_box.GetSelection())

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.integration_box, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(watch_box_sizer, 0, wx.EXPAND | wx.ALL, 10)
        sizer.Add(deluge_web_ui_box_sizer, 0, wx.EXPAND | wx.ALL, 10)
        self.SetSizer(sizer)

    def OnIntegrationMethodChanged(self, evt=None, index=-1):
        if evt is not None:
            index = evt.GetInt()

        method = self.integration_methods[index]

        self.download_directory.Enabled = method == 'WATCH_FOLDER'
        self.webui_url.Enabled = method == 'DELUGE_WEB_UI'
        self.webui_password.Enabled = method == 'DELUGE_WEB_UI'

    def CommitChanges(self):
        config().set_key('TORRENT_INTEGRATION_METHOD', self.integration_methods[self.integration_box.GetSelection()])
        config().set_key('DOWNLOAD_DIRECTORY', self.download_directory.GetValue())
        config().set_key('DELUGE_WEB_UI_URL', self.webui_url.GetValue())
        config().set_key('DELUGE_WEB_UI_PASSWORD', self.webui_password.GetValue())



