import logging
import wx

from granary.configmanager import config


log = logging.getLogger(__name__)


class GrowlOptionsPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

        self.enable_growl = wx.CheckBox(self, -1, "Enable Growl Support")
        self.enable_growl.SetValue(config().get_key('ENABLE_GROWL'))

        self.enable_download_notifications = wx.CheckBox(self, -1, "Enable Download Notifications")
        self.enable_download_notifications.SetValue(config().get_key('ENABLE_GROWL_DOWNLOAD_NOTIFICATION'))

        self.enable_new_torrent_notifications = wx.CheckBox(self, -1, "Enable New Torrent Notifications")
        self.enable_new_torrent_notifications.SetValue(config().get_key('ENABLE_GROWL_NEW_TORRENT_NOTIFICATION'))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.enable_growl, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.enable_download_notifications, 0, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self.enable_new_torrent_notifications, 0, wx.EXPAND | wx.ALL, 5)

        self.OnEnableGrowlChanged(None)

        self.Bind(wx.EVT_CHECKBOX, self.OnEnableGrowlChanged, self.enable_growl)
        self.SetSizer(sizer)

    def OnEnableGrowlChanged(self, evt):
        self.enable_download_notifications.Enabled = self.enable_growl.GetValue()
        self.enable_new_torrent_notifications.Enabled = self.enable_growl.GetValue()

    def CommitChanges(self):
        config().set_key('ENABLE_GROWL', self.enable_growl.GetValue())
        config().set_key('ENABLE_GROWL_DOWNLOAD_NOTIFICATION', self.enable_download_notifications.GetValue())
        config().set_key('ENABLE_GROWL_NEW_TORRENT_NOTIFICATION', self.enable_new_torrent_notifications.GetValue())
