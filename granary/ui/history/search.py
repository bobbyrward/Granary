import logging

import wx
from wx.lib.newevent import NewCommandEvent

from granary.configmanager import config


log = logging.getLogger(__name__)


(ClearSearchEvent, EVT_SEARCH_CLEAR) = NewCommandEvent()
(PerformSearchEvent, EVT_SEARCH_PERFORM) = NewCommandEvent()


SEARCH_HISTORY_MAX_LEN = 10


def _get_search_history():
    return config().get_key('SEARCH_HISTORY')


def _add_search_to_history(history_item):
    history = _get_search_history()

    if history_item in history:
        # already in history.  just move it to the top
        history.remove(history_item)
    elif len(history) >= SEARCH_HISTORY_MAX_LEN:
        # truncate history
        history.pop(0)

    history.append(history_item)

    config().set_key('SEARCH_HISTORY', history)


class HistorySearch(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)

        self.search = wx.SearchCtrl(self, size=(300, -1), style=wx.TE_PROCESS_ENTER)
        self.search.ShowSearchButton(True)
        self.search.ShowCancelButton(True)

        self.RefreshHistoryMenu()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.search, 0, wx.ALL | wx.ALIGN_RIGHT, 5)

        self.SetSizer(sizer)

        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDoSearch, self.search)

    def RefreshHistoryMenu(self):
        self.search.SetMenu(self.CreateHistoryMenu())

    def OnCancel(self, evt):
        log.debug("OnCancel")

        self.search.Clear()

        sub_event = ClearSearchEvent(self.GetId())
        sub_event.SetEventObject(self)

        log.debug("Sending EVT_SEARCH_CLEAR event")

        self.GetEventHandler().ProcessEvent(sub_event)

    def _SendSearchEvent(self):
        search_string = self.search.GetValue()

        if search_string == '':
            self.OnCancel(None)
            return

        _add_search_to_history(search_string)

        self.RefreshHistoryMenu()

        sub_event = PerformSearchEvent(self.GetId())
        sub_event.SetEventObject(self)
        sub_event.terms = search_string.lower().split(' ')

        log.debug("Sending EVT_SEARCH_PERFORM event: %s", search_string)

        self.GetEventHandler().ProcessEvent(sub_event)

    def OnMenuSearch(self, evt, search_string):
        log.debug("OnMenuSearch: %s", search_string)
        self.search.SetValue(search_string)
        self._SendSearchEvent()

    def OnSearch(self, evt):
        log.debug("OnSearch: %s", evt.GetString())
        self._SendSearchEvent()

    def OnDoSearch(self, evt):
        log.debug("OnDoSearch: %s", self.search.GetValue())
        self._SendSearchEvent()

    def CreateHistoryMenu(self):
        menu = wx.Menu()

        for item in reversed(_get_search_history()):
            menu_item = menu.Append(-1, item)

            def callback(evt, s=item):
                self.OnMenuSearch(evt, s)

            self.Bind(wx.EVT_MENU, callback, menu_item)

        return menu
