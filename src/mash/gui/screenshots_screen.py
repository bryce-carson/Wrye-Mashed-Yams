class ScreensPanel(gui.NotebookPanel):
    """Screenshots tab."""

    def __init__(self, parent):
        """Init."""
        wx.Panel.__init__(self, parent, -1)
        # --Left
        sashPos = conf.settings.get("mash.screens.sashPos", 120)
        left = self.left = leftSash(
            self, defaultSize=(sashPos, 100), onSashDrag=self.OnSashDrag
        )
        right = self.right = wx.Panel(self, style=wx.NO_BORDER)
        # --Contents
        singletons.screensList = ScreensList(left)
        singletons.screensList.SetSizeHints(100, 100)
        singletons.screensList.picture = balt.Picture(right, 1024, 768)
        # --Layout
        right.SetSizer(hSizer((singletons.screensList.picture, 1, wx.GROW)))
        wx.LayoutAlgorithm().LayoutWindow(self, right)
        # --Event
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetStatusCount(self):  # Polemos: just a preference "typo" fix
        """Sets status bar count field."""
        text = _("Screenshots: %d") % (len(singletons.screensList.data.data),)
        singletons.statusBar.SetStatusField(text, 2)

    def OnSashDrag(self, event):
        """Handle sash moved."""
        wMin, wMax = 80, self.GetSizeTuple()[0] - 80
        sashPos = max(wMin, min(wMax, event.GetDragRect().width))
        self.left.SetDefaultSize((sashPos, 10))
        wx.LayoutAlgorithm().LayoutWindow(self, self.right)
        singletons.screensList.picture.Refresh()
        conf.settings["mash.screens.sashPos"] = sashPos

    def OnSize(self, event=None):
        wx.LayoutAlgorithm().LayoutWindow(self, self.right)

    def OnShow(self):
        """Panel is shown. Update self.data."""
        if mosh.screensData.refresh():
            singletons.screensList.RefreshUI()
        self.SetStatusCount()
