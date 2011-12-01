import wx
import wx.lib.scrolledpanel as scrolled


class ListEditorCtrl(wx.Panel):
    def __init__(self, parent, caption, list_items, id=-1, pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        wx.Panel.__init__(self, parent, -1, pos, size, style)

        self.list_items = []
        self.has_changes = False

        #TODO: Is this the right image for this?
        self.remove_image = wx.Image('cross.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        self.scrolled_list = scrolled.ScrolledPanel(self, -1, style=wx.SUNKEN_BORDER)
        self.scrolled_sizer = wx.GridBagSizer(2, 2)
        self.scrolled_sizer.SetEmptyCellSize((0,0))

        for item in list_items:
            self._add_item_to_list(item)

        self.scrolled_sizer.AddGrowableCol(1)

        self.scrolled_list.SetSizer(self.scrolled_sizer)
        self.scrolled_list.SetAutoLayout(1)
        self.scrolled_list.SetupScrolling()

        panel = wx.Panel(self)
        self.add_text = wx.TextCtrl(panel, -1)
        self.add_button = wx.Button(panel, -1, "Add", style=wx.BU_EXACTFIT)

        inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        inner_sizer.Add(self.add_text, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 2)
        inner_sizer.Add(self.add_button, 0, wx.TOP|wx.BOTTOM, 2)
        panel.SetSizer(inner_sizer)

        self.add_text.SetFocus()

        box_sizer = wx.BoxSizer(wx.VERTICAL)
        box_sizer.Add(self.scrolled_list, 1, wx.EXPAND|wx.TOP|wx.LEFT|wx.RIGHT, 10)
        box_sizer.Add(panel, 0, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.TOP, 10)

        self.SetSizer(box_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnAddButtonClicked, self.add_button)

    def OnAddButtonClicked(self, evt):
        self._add_item_to_list(self.add_text.Value)
        self.add_text.Clear()
        self.scrolled_sizer.Layout()
        self.scrolled_list.SetupScrolling()

        self.has_changes = True
        print 'Changed list'
        
        #TODO: Should auto scroll to the bottom of the list
        #bottom = self.scrolled_list.GetScrollRange(wx.VERTICAL)
        #self.scrolled_list.SetScrollPos(wx.VERTICAL, bottom, False)

    def _add_item_to_list(self, item_text):
        self.list_items.append(item_text)

        static_text = wx.StaticText(self.scrolled_list, -1, item_text, style=wx.BORDER_NONE)
        remove_button = wx.BitmapButton(self.scrolled_list, -1, self.remove_image, (0, 0), (20, 20))
        remove_button.SetToolTipString("Remove")

        idx = (len(self.list_items) - 1) * 2 

        self.Bind(wx.EVT_BUTTON, self.OnRemoveRow, remove_button)

        self.scrolled_sizer.Add(remove_button, (idx, 0), (1, 1), wx.ALL, 2)
        self.scrolled_sizer.Add(static_text, (idx, 1), (1, 1), wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 2)

        line = wx.StaticLine(self.scrolled_list, -1, style=wx.LI_HORIZONTAL)
        self.scrolled_sizer.Add(line, (idx+1, 0), (1, 2), wx.EXPAND|wx.ALL, 0)

    def OnRemoveRow(self, evt):
        idx = self.scrolled_sizer.GetItemPosition(evt.GetEventObject())[0]
        
        del self.list_items[idx / 2]

        button = self.scrolled_sizer.FindItemAtPosition((idx, 0)).GetWindow()
        text = self.scrolled_sizer.FindItemAtPosition((idx, 1)).GetWindow()
        line = self.scrolled_sizer.FindItemAtPosition((idx+1, 0)).GetWindow()

        if button is None:
            return

        self.scrolled_sizer.Detach(button)
        self.scrolled_sizer.Detach(text)
        self.scrolled_sizer.Detach(line)

        button.Destroy()
        text.Destroy()
        line.Destroy()

        for move_idx in range(idx+2, self.scrolled_sizer.GetRows(), 2):
            button = self.scrolled_sizer.FindItemAtPosition((move_idx, 0)).GetWindow()
            text = self.scrolled_sizer.FindItemAtPosition((move_idx, 1)).GetWindow()
            line = self.scrolled_sizer.FindItemAtPosition((move_idx+1, 0)).GetWindow()

            self.scrolled_sizer.SetItemPosition(button, (move_idx-2, 0))
            self.scrolled_sizer.SetItemPosition(text, (move_idx-2, 1))
            self.scrolled_sizer.SetItemPosition(line, (move_idx-1, 0))

        self.scrolled_sizer.Layout()
        self.has_changes = True

    def GetListItems(self):
        # List should be kept up to date automatically
        return self.list_items






