class Utils_Delete(Link):  # Added D.C.-G. for Utils panel.
    """Create a new utility."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("Delete"))
        menu.AppendItem(menuItem)
        menuItem.Enable(True)

    def Execute(self, event):
        """Handle menu selection."""
        self.window.DeleteItem()


# ------------------------------------------------------------------------------


class Utils_Modify(Link):  # Added D.C.-G. for Utils panel.
    """Create a new utility."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("Modify"))
        menu.AppendItem(menuItem)
        menuItem.Enable(True)

    def Execute(self, event):
        """Handle menu selection."""
        self.window.ModifyItem()


# ------------------------------------------------------------------------------


class Utils_New(Link):  # Added D.C.-G. for Utils panel.
    """Create a new utility."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("New"))
        menu.AppendItem(menuItem)
        menuItem.Enable(True)

    def Execute(self, event):
        """Handle menu selection."""
        self.window.NewItem()
