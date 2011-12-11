import logging

import wx
from wx.lib.newevent import NewCommandEvent


log = logging.getLogger(__name__)


(ClearSearchEvent, EVT_SEARCH_CLEAR) = NewCommandEvent()
(PerformSearchEvent, EVT_SEARCH_PERFORM) = NewCommandEvent()


class HistorySearch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        self.search = wx.SearchCtrl(self, size=(300, -1), style=wx.TE_PROCESS_ENTER)
        self.search.ShowSearchButton(True)
        self.search.ShowCancelButton(True)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)

    def OnCancel(self, evt):
        log.debug("OnCancel: %s", evt.GetString())

        self.search.Clear()

        sub_event = ClearSearchEvent(self.GetId())
        sub_event.SetEventObject(self)

        log.debug("Sending EVT_SEARCH_CLEAR event")

        self.GetEventHandler().ProcessEvent(sub_event)

    def OnSearch(self, evt):
        log.debug("OnSearch: %s", evt.GetString())

        sub_event = PerformSearchEvent(self.GetId())
        sub_event.SetEventObject(self)
        sub_event.terms = self.search.GetValue().lower().split(' ')

        log.debug("Sending EVT_SEARCH_PERFORM event: %s", self.search.GetValue())

        self.GetEventHandler().ProcessEvent(sub_event)

    def OnDoSearch(self, evt):
        log.debug("OnDoSearch: %s", self.search.GetValue())

        sub_event = PerformSearchEvent(self.GetId())
        sub_event.SetEventObject(self)
        sub_event.terms = self.search.GetValue().lower().split(' ')

        log.debug("Sending EVT_SEARCH_PERFORM event: %s", self.search.GetValue())

        self.GetEventHandler().ProcessEvent(sub_event)
