# -*- coding: utf-8 -*-
import os
import components
from cityNamingScheme import GPath
from unicode.unimash import _  # Polemos
from errors import AbstractError as AbstractError, ArgumentError as ArgumentError
from errors import StateError as StateError, UncodedError as UncodedError
import conf  # Polemos
import cStringIO
import string
import sys
import textwrap
import time
import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin


# Constants
defId = -1
defVal = wx.DefaultValidator
defPos = wx.DefaultPosition
defSize = wx.DefaultSize
wxListAligns = {
    "LEFT": wx.LIST_FORMAT_LEFT,
    "RIGHT": wx.LIST_FORMAT_RIGHT,
    "CENTER": wx.LIST_FORMAT_CENTRE,
}
# Settings
_settings = {}  # --Using applications should override this.
sizes = {}  # --Using applications should override this.


# Basics ---------------------------------------------------------------------


class IdList:
    """Provides sequences of semi-unique ids. Useful for choice menus.

    Sequence ids come in range from baseId up through (baseId + size - 1).
    Named ids will be assigned ids starting at baseId + size.

    Example:
      loadIds = IdList(10000, 90,'SAVE','EDIT','NONE')
    sequence ids are accessed by an iterator: i.e. iter(loadIds), and
    named ids accessed by name. e.g. loadIds.SAVE, loadIds.EDIT, loadIds.NONE
    """

    def __init__(self, baseId, size, *names):
        self.BASE = baseId
        self.MAX = baseId + size - 1
        # --Extra
        nextNameId = baseId + size
        for name in names:
            setattr(self, name, nextNameId)
            nextNameId += 1

    def __iter__(self):
        """Return iterator."""
        for id in xrange(self.BASE, self.MAX + 1):
            yield id


# Colors ----------------------------------------------------------------------


class Colors:
    """Colour collection and wrapper for wx.ColourDatabase.
    Provides dictionary syntax access (colors[key]) and predefined colours."""

    def __init__(self):
        self.data = {}
        self.database = None

    def __setitem__(self, key, value):
        """Add a color to the database."""
        # --Add to pending?
        if not self.database:
            self.data[key] = value
        # --Else add it to the database
        elif type(value) is str:
            self.data[key] = self.database.Find(value)
        else:
            self.data[key] = wx.Colour(*value)

    def __getitem__(self, key):
        """Dictionary syntax: color = colours[key]."""
        if not self.database:
            self.database = wx.TheColourDatabase
            for key, value in self.data.items():
                if type(value) is str:
                    self.data[key] = self.database.Find(value)
                else:
                    self.data[key] = wx.Colour(*value)
        if key in self.data:
            return self.data[key]
        else:
            return self.database.Find(key)


# --Singleton
colors = Colors()

# Images ----------------------------------------------------------------------
images = {}  # --Singleton for collection of images.


class Image:
    """Wrapper for images, allowing access in various formats/classes.
    Allows image to be specified before wx.App is initialized."""

    def __init__(self, file, type=wx.BITMAP_TYPE_ANY):
        """Init."""
        self.file = GPath(file)
        self.type = type
        self.bitmap = None
        self.icon = None
        if not GPath(self.file).exists():
            raise ArgumentError(_("Missing resource file: %s.") % (self.file,))

    def GetBitmap(self):
        """Return bitmap."""
        if not self.bitmap:
            self.bitmap = wx.Bitmap(self.file.s, self.type)
        return self.bitmap

    def GetIcon(self):
        """Return icon."""
        if not self.icon:
            self.icon = wx.EmptyIcon()
            self.icon.CopyFromBitmap(self.GetBitmap())
        return self.icon


class ImageBundle:
    """Wrapper for bundle of images.
    Allows image bundle to be specified before wx.App is initialized."""

    def __init__(self):
        self.images = []
        self.iconBundle = None

    def Add(self, image):
        self.images.append(image)

    def GetIconBundle(self):
        if not self.iconBundle:
            self.iconBundle = wx.IconBundle()
            for image in self.images:
                self.iconBundle.AddIcon(image.GetIcon())
        return self.iconBundle


class ImageList:
    """Wrapper for wx.ImageList.

    Allows ImageList to be specified before wx.App is initialized.
    Provides access to ImageList integers through imageList[key]."""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.data = []
        self.indices = {}
        self.imageList = None

    def Add(self, image, key):
        self.data.append((key, image))

    def GetImageList(self):
        if not self.imageList:
            indices = self.indices
            imageList = self.imageList = wx.ImageList(self.width, self.height)
            for key, image in self.data:
                indices[key] = imageList.Add(image.GetBitmap())
        return self.imageList

    def __getitem__(self, key):
        self.GetImageList()
        return self.indices[key]


# Functions -------------------------------------------------------------------


def fill(text, width=60):
    """Wraps paragraph to width characters."""
    pars = [textwrap.fill(text, width) for text in text.split("\n")]
    return "\n".join(pars)


def ensureDisplayed(frame, x=100, y=100):
    """Ensure that frame is displayed."""
    if wx.Display.GetFromWindow(frame) == -1:
        topLeft = wx.Display(0).GetGeometry().GetTopLeft()
        frame.MoveXY(topLeft.x + x, topLeft.y + y)


def setCheckListItems(gList, names, values):  # Polemos - Installers: break if not read.
    """Convenience method for setting a bunch of wxCheckListBox items. The main advantage
    of this is that it doesn't clear the list unless it needs to. Which is good if you want
    to preserve the scroll position of the list."""
    if not names:
        gList.Clear()
    else:
        for index, (name, value) in enumerate(zip(names, values)):
            if index >= gList.GetCount():
                try:
                    gList.Append(name)
                except:
                    gList.Clear()
                    break
            else:
                try:
                    gList.SetString(index, name)
                except:
                    gList.Clear()
                    break
            gList.Check(index, value)
        for index in xrange(gList.GetCount(), len(names), -1):
            gList.Delete(index - 1)


# Elements --------------------------------------------------------------------


def bell(arg=None):
    """ "Rings the system bell and returns the input argument (useful for return bell(value))."""
    wx.Bell()
    return arg


def tooltip(text, wrap=50):
    """Returns tolltip with wrapped copy of text."""
    text = textwrap.fill(text, wrap)
    return wx.ToolTip(text)


def bitmapButton(
    parent,
    bitmap,
    pos=defPos,
    size=defSize,
    style=wx.BU_AUTODRAW,
    val=defVal,
    name="button",
    id=defId,
    onClick=None,
    tip=None,
):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.BitmapButton(parent, id, bitmap, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_BUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def button(
    parent,
    label="",
    pos=defPos,
    size=defSize,
    style=0,
    val=defVal,
    name="button",
    id=defId,
    onClick=None,
    tip=None,
):
    """Creates a button, binds click function, then returns bound button."""
    gButton = wx.Button(parent, id, label, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_BUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def toggleButton(
    parent,
    label="",
    pos=defPos,
    size=defSize,
    style=0,
    val=defVal,
    name="button",
    id=defId,
    onClick=None,
    tip=None,
):
    """Creates a toggle button, binds toggle function, then returns bound button."""
    gButton = wx.ToggleButton(parent, id, label, pos, size, style, val, name)
    if onClick:
        gButton.Bind(wx.EVT_TOGGLEBUTTON, onClick)
    if tip:
        gButton.SetToolTip(tooltip(tip))
    return gButton


def checkBox(
    parent,
    label="",
    pos=defPos,
    size=defSize,
    style=0,
    val=defVal,
    name="checkBox",
    id=defId,
    onCheck=None,
    tip=None,
):
    """Creates a checkBox, binds check function, then returns bound button."""
    gCheckBox = wx.CheckBox(parent, id, label, pos, size, style, val, name)
    if onCheck:
        gCheckBox.Bind(wx.EVT_CHECKBOX, onCheck)
    if tip:
        gCheckBox.SetToolTip(tooltip(tip))
    return gCheckBox


def staticText(
    parent,
    label="",
    pos=defPos,
    size=defSize,
    style=0,
    name="staticText",
    id=defId,
):
    """Static text element."""
    return wx.StaticText(parent, id, label, pos, size, style, name)


def spinCtrl(
    parent,
    value="",
    pos=defPos,
    size=defSize,
    style=wx.SP_ARROW_KEYS,
    min=0,
    max=100,
    initial=0,
    name="wxSpinctrl",
    id=defId,
    onSpin=None,
    tip=None,
):
    """Spin control with event and tip setting."""
    gSpinCtrl = wx.SpinCtrl(
        parent, id, value, pos, size, style, min, max, initial, name
    )
    if onSpin:
        gSpinCtrl.Bind(wx.EVT_SPINCTRL, onSpin)
    if tip:
        gSpinCtrl.SetToolTip(tooltip(tip))
    return gSpinCtrl


# Sub-Windows -----------------------------------------------------------------


def leftSash(parent, defaultSize=(100, 100), onSashDrag=None):
    """Creates a left sash window."""
    sash = wx.SashLayoutWindow(parent, style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_VERTICAL)
    sash.SetAlignment(wx.LAYOUT_LEFT)
    sash.SetSashVisible(wx.SASH_RIGHT, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag, id=id, id2=id)
    return sash


def topSash(parent, defaultSize=(100, 100), onSashDrag=None):
    """Creates a top sash window."""
    sash = wx.SashLayoutWindow(parent, style=wx.SW_3D)
    sash.SetDefaultSize(defaultSize)
    sash.SetOrientation(wx.LAYOUT_HORIZONTAL)
    sash.SetAlignment(wx.LAYOUT_TOP)
    sash.SetSashVisible(wx.SASH_BOTTOM, True)
    if onSashDrag:
        id = sash.GetId()
        sash.Bind(wx.EVT_SASH_DRAGGED_RANGE, onSashDrag, id=id, id2=id)
    return sash


# Sizers ----------------------------------------------------------------------

spacer = ((0, 0), 1)  # --Used to space elements apart.


def aSizer(sizer, *elements):
    """Adds elements to a sizer."""
    for element in elements:
        if type(element) is tuple:
            if element[0] is not None:
                sizer.Add(*element)
        elif element is not None:
            sizer.Add(element)
    return sizer


def hSizer(*elements):
    """Horizontal sizer."""
    return aSizer(wx.BoxSizer(wx.HORIZONTAL), *elements)


def vSizer(*elements):
    """Vertical sizer and elements."""
    return aSizer(wx.BoxSizer(wx.VERTICAL), *elements)


def hsbSizer(boxArgs, *elements):
    """Horizontal static box sizer and elements."""
    return aSizer(wx.StaticBoxSizer(wx.StaticBox(*boxArgs), wx.HORIZONTAL), *elements)


def vsbSizer(boxArgs, *elements):
    """Vertical static box sizer and elements."""
    return aSizer(wx.StaticBoxSizer(wx.StaticBox(*boxArgs), wx.VERTICAL), *elements)


# Modal Dialogs ---------------------------------------------------------------


def askDirectory(parent, message=_("Choose a directory."), defaultPath=""):
    """Shows a modal directory dialog and return the resulting path, or None if canceled."""
    dialog = wx.DirDialog(
        parent, message, GPath(defaultPath).s, style=wx.DD_NEW_DIR_BUTTON
    )
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        path = dialog.GetPath()
        dialog.Destroy()
        return path


# ------------------------------------------------------------------------------


def askContinue(parent, message, continueKey, title=_("Warning")):
    """Shows a modal continue query if value of continueKey is false. Returns True to continue.
    Also provides checkbox "Don't show this in future." to set continueKey to true."""
    # --ContinueKey set?
    if _settings.get(continueKey):
        return wx.ID_OK
    # --Generate/show dialog
    dialog = wx.Dialog(
        parent,
        defId,
        title,
        size=(350, 200),
        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
    )
    icon = wx.StaticBitmap(
        dialog,
        defId,
        wx.ArtProvider_GetBitmap(wx.ART_WARNING, wx.ART_MESSAGE_BOX, (32, 32)),
    )
    gCheckBox = checkBox(dialog, _("Don't show this in the future."))
    # --Layout
    sizer = vSizer(
        (
            hSizer(
                (icon, 0, wx.ALL, 6),
                (
                    staticText(dialog, message, style=wx.ST_NO_AUTORESIZE),
                    1,
                    wx.EXPAND | wx.LEFT,
                    6,
                ),
            ),
            1,
            wx.EXPAND | wx.ALL,
            6,
        ),
        (gCheckBox, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6),
        (
            hSizer(  # --Save/Cancel
                spacer,
                button(dialog, id=wx.ID_OK),
                (button(dialog, id=wx.ID_CANCEL), 0, wx.LEFT, 4),
            ),
            0,
            wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM,
            6,
        ),
    )
    dialog.SetSizer(sizer)
    # --Get continue key setting and return
    result = dialog.ShowModal()
    if gCheckBox.GetValue():
        _settings[continueKey] = 1
    return result in (wx.ID_OK, wx.ID_YES)


# ------------------------------------------------------------------------------


def askOpen(
    parent, title="", defaultDir="", defaultFile="", wildcard="", style=wx.FD_OPEN
):
    """Show as file dialog and return selected path(s)."""
    defaultDir, defaultFile = [GPath(x).s for x in (defaultDir, defaultFile)]
    dialog = wx.FileDialog(parent, title, defaultDir, defaultFile, wildcard, style)
    if dialog.ShowModal() != wx.ID_OK:
        result = False
    elif style & wx.MULTIPLE:
        result = map(GPath, dialog.GetPaths())
    else:
        result = GPath(dialog.GetPath())
    dialog.Destroy()
    return result


def askOpenMulti(
    parent,
    title="",
    defaultDir="",
    defaultFile="",
    wildcard="",
    style=wx.FD_OPEN | wx.FD_MULTIPLE,
):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent, title, defaultDir, defaultFile, wildcard, style)


def askSave(
    parent,
    title="",
    defaultDir="",
    defaultFile="",
    wildcard="",
    style=wx.FD_OVERWRITE_PROMPT,
):
    """Show as save dialog and return selected path(s)."""
    return askOpen(parent, title, defaultDir, defaultFile, wildcard, wx.FD_SAVE | style)


# ------------------------------------------------------------------------------


def askText(parent, message, title="", default=""):
    """Shows a text entry dialog and returns result or None if canceled."""
    dialog = wx.TextEntryDialog(parent, message, title, default)
    if dialog.ShowModal() != wx.ID_OK:
        dialog.Destroy()
        return None
    else:
        value = dialog.GetValue()
        dialog.Destroy()
        return value


# Message Dialogs -------------------------------------------------------------


def askStyled(parent, message, title, style):
    """Shows a modal MessageDialog.
    Use ErrorMessage, WarningMessage or InfoMessage."""
    dialog = wx.MessageDialog(parent, message, title, style)
    result = dialog.ShowModal()
    dialog.Destroy()
    return result in (wx.ID_OK, wx.ID_YES)


def askOk(parent, message, title=""):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK | wx.CANCEL)


def askYes(parent, message, title="", default=True):
    """Shows a modal warning message."""
    style = wx.YES_NO | wx.ICON_EXCLAMATION | ((wx.NO_DEFAULT, wx.YES_DEFAULT)[default])
    return askStyled(parent, message, title, style)


def askWarning(parent, message, title=_("Warning")):
    """Shows a modal warning message."""
    return askStyled(parent, message, title, wx.OK | wx.CANCEL | wx.ICON_EXCLAMATION)


def showOk(parent, message, title=""):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK)


def showError(parent, message, title=_("Error")):
    """Shows a modal error message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_HAND)


def showWarning(parent, message, title=_("Warning")):
    """Shows a modal warning message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_EXCLAMATION)


def showInfo(parent, message, title=_("Information")):
    """Shows a modal information message."""
    return askStyled(parent, message, title, wx.OK | wx.ICON_INFORMATION)


def showList(parent, header, items, maxItems=0, title=""):
    """Formats a list of items into a message for use in a Message."""
    numItems = len(items)
    if maxItems <= 0:
        maxItems = numItems
    message = string.Template(header).substitute(count=numItems)
    message += "\n* " + "\n* ".join(items[: min(numItems, maxItems)])
    if numItems > maxItems:
        message += _("\n(And %d others.)") % (numItems - maxItems,)
    return askStyled(parent, message, title, wx.OK)


# ------------------------------------------------------------------------------


def showLogClose(evt=None):
    """Handle log message closing."""
    window = evt.GetEventObject()
    if not window.IsIconized() and not window.IsMaximized():
        _settings["balt.LogMessage.pos"] = window.GetPositionTuple()
        _settings["balt.LogMessage.size"] = window.GetSizeTuple()
    window.Destroy()


def showLog(
    parent, logText, title="", style=0, asDialog=True, fixedFont=False, icons=None
):
    """Display text in a log window"""
    # --Sizing
    pos = _settings.get("balt.LogMessage.pos", defPos)
    size = _settings.get("balt.LogMessage.size", (400, 400))
    # --Dialog or Frame
    if asDialog:
        window = wx.Dialog(
            parent,
            defId,
            title,
            pos=pos,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
    else:
        window = wx.Frame(
            parent,
            defId,
            title,
            pos=pos,
            size=size,
            style=(
                wx.RESIZE_BORDER
                | wx.CAPTION
                | wx.SYSTEM_MENU
                | wx.CLOSE_BOX
                | wx.CLIP_CHILDREN
            ),
        )
        if icons:
            window.SetIcons(icons)
    window.SetSizeHints(200, 200)
    window.Bind(wx.EVT_CLOSE, showLogClose)
    window.SetBackgroundColour(
        wx.NullColour
    )  # --Bug workaround to ensure that default colour is being used.
    # --Text
    textCtrl = wx.TextCtrl(
        window,
        defId,
        logText,
        style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2 | wx.SUNKEN_BORDER,
    )
    if fixedFont:
        fixedFont = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
        fixedFont.SetPointSize(8)
        fixedStyle = wx.TextAttr()
        # fixedStyle.SetFlags(0x4|0x80)
        fixedStyle.SetFont(fixedFont)
        textCtrl.SetStyle(0, textCtrl.GetLastPosition(), fixedStyle)
    # --Buttons
    gOkButton = button(window, id=wx.ID_OK, onClick=lambda event: window.Close())
    gOkButton.SetDefault()
    # --Layout
    window.SetSizer(
        vSizer(
            (textCtrl, 1, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 2),
            (gOkButton, 0, wx.ALIGN_RIGHT | wx.ALL, 4),
        )
    )
    # --Show
    if asDialog:
        window.ShowModal()
        window.Destroy()
    else:
        window.Show()


# ------------------------------------------------------------------------------


def showWryeLog(parent, logText, title="", style=0, asDialog=True, icons=None):
    """Convert logText from wtxt to html and display. Optionally, logText can be path to an html file."""
    import wx.lib.iewin

    # --Sizing
    pos = _settings.get("balt.WryeLog.pos", defPos)
    size = _settings.get("balt.WryeLog.size", (400, 400))
    # --Dialog or Frame
    if asDialog:
        window = wx.Dialog(
            parent,
            defId,
            title,
            pos=pos,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
    else:
        window = wx.Frame(
            parent,
            defId,
            title,
            pos=pos,
            size=size,
            style=(
                wx.RESIZE_BORDER
                | wx.CAPTION
                | wx.SYSTEM_MENU
                | wx.CLOSE_BOX
                | wx.CLIP_CHILDREN
            ),
        )
        if icons:
            window.SetIcons(icons)
    window.SetSizeHints(200, 200)
    window.Bind(wx.EVT_CLOSE, showLogClose)
    # --Text
    textCtrl = wx.lib.iewin.IEHtmlWindow(
        window, defId, style=wx.NO_FULL_REPAINT_ON_RESIZE
    )  #  iewin
    if not isinstance(logText, bolt.Path):
        logPath = _settings.get(
            "balt.WryeLog.temp", bolt.Path.getcwd().join("WryeLogTemp.html")
        )
        cssDir = _settings.get("balt.WryeLog.cssDir", GPath(""))
        ins = cStringIO.StringIO(logText + "\n{{CSS:wtxt_sand_small.css}}")
        out = logPath.open("w")
        bolt.WryeText.genHtml(ins, out, cssDir)
        out.close()
        logText = logPath
    textCtrl.Navigate(logText.s, 0x2)  # --0x2: Clear History
    # --Buttons
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_BACK, wx.ART_HELP_BROWSER, (16, 16))
    gBackButton = bitmapButton(window, bitmap, onClick=lambda evt: textCtrl.GoBack())
    bitmap = wx.ArtProvider_GetBitmap(wx.ART_GO_FORWARD, wx.ART_HELP_BROWSER, (16, 16))
    gForwardButton = bitmapButton(
        window, bitmap, onClick=lambda evt: textCtrl.GoForward()
    )
    gOkButton = button(window, id=wx.ID_OK, onClick=lambda event: window.Close())
    gOkButton.SetDefault()
    # --Layout
    window.SetSizer(
        vSizer(
            (textCtrl, 1, wx.EXPAND | wx.ALL ^ wx.BOTTOM, 2),
            (
                hSizer(
                    gBackButton,
                    gForwardButton,
                    spacer,
                    gOkButton,
                ),
                0,
                wx.ALL | wx.EXPAND,
                4,
            ),
        )
    )
    # --Show
    if asDialog:
        window.ShowModal()
        _settings["balt.WryeLog.pos"] = window.GetPositionTuple()
        _settings["balt.WryeLog.size"] = window.GetSizeTuple()
        window.Destroy()
    else:
        window.Show()


# Other Windows ---------------------------------------------------------------


class ListEditorData:
    """Data capsule for ListEditor. [Abstract]"""

    def __init__(self, parent):
        """Initialize."""
        self.parent = parent  # --Parent window.
        self.showAction = False
        self.showAdd = False
        self.showEdit = False
        self.showRename = False
        self.showRemove = False
        self.showSave = False
        self.showCancel = False
        self.caption = None
        # --Editable?
        self.showInfo = False
        self.infoWeight = 1  # --Controls width of info pane
        self.infoReadOnly = True  # --Controls whether info pane is editable

    # --List
    def action(self, item):
        """Called when action button is used.."""
        pass

    def select(self, item):
        """Called when an item is selected."""
        pass

    def getItemList(self):
        """Returns item list in correct order."""
        raise AbstractError
        return []

    def add(self):
        """Peforms add operation. Return new item on success."""
        raise AbstractError
        return None

    def edit(self, item=None):
        """Edits specified item. Return true on success."""
        raise AbstractError
        return False

    def rename(self, oldItem, newItem):
        """Renames oldItem to newItem. Return true on success."""
        raise AbstractError
        return False

    def remove(self, item):
        """Removes item. Return true on success."""
        raise AbstractError
        return False

    def close(self):
        """Called when dialog window closes."""
        pass

    # --Info box
    def getInfo(self, item):
        """Returns string info on specified item."""
        return ""

    def setInfo(self, item, text):
        """Sets string info on specified item."""
        raise AbstractError

    # --Checklist
    def getChecks(self):
        """Returns checked state of items as array of True/False values matching Item list."""
        raise AbstractError
        return []

    def check(self, item):
        """Checks items. Return true on success."""
        raise AbstractError
        return False

    def uncheck(self, item):
        """Unchecks item. Return true on success."""
        raise AbstractError
        return False

    # --Save/Cancel
    def save(self):
        """Handles save button."""
        pass

    def cancel(self):
        """Handles cancel button."""
        pass


# ------------------------------------------------------------------------------
class ListEditor(wx.Dialog):
    """Dialog for editing lists."""

    def __init__(self, parent, id, title, data, type="list"):
        """Init."""
        # --Data
        self.data = data  # --Should be subclass of ListEditorData
        self.items = data.getItemList()
        # --GUI
        wx.Dialog.__init__(
            self, parent, id, title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        )
        wx.EVT_CLOSE(self, self.OnCloseWindow)
        # --Caption
        if data.caption:
            captionText = staticText(self, data.caption)
        else:
            captionText = None
        # --List Box
        if type == "checklist":
            self.list = wx.CheckListBox(
                self, -1, choices=self.items, style=wx.LB_SINGLE
            )
            for index, checked in enumerate(self.data.getChecks()):
                self.list.Check(index, checked)
            self.Bind(wx.EVT_CHECKLISTBOX, self.DoCheck, self.list)
        else:
            self.list = wx.ListBox(self, -1, choices=self.items, style=wx.LB_SINGLE)
        self.list.SetSizeHints(125, 150)
        self.list.Bind(wx.EVT_LISTBOX, self.OnSelect)
        # --Infobox
        if data.showInfo:
            self.gInfoBox = wx.TextCtrl(
                self,
                -1,
                " ",
                size=(130, -1),
                style=(self.data.infoReadOnly * wx.TE_READONLY)
                | wx.TE_MULTILINE
                | wx.SUNKEN_BORDER,
            )
            if not self.data.infoReadOnly:
                self.gInfoBox.Bind(wx.EVT_TEXT, self.OnInfoEdit)
        else:
            self.gInfoBox = None
        # --Buttons
        buttonSet = (
            (data.showAction, _("Action"), self.DoAction),
            (data.showAdd, _("Add"), self.DoAdd),
            (data.showEdit, _("Edit"), self.DoEdit),
            (data.showRename, _("Rename"), self.DoRename),
            (data.showRemove, _("Remove"), self.DoRemove),
            (data.showSave, _("Save"), self.DoSave),
            (data.showCancel, _("Cancel"), self.DoCancel),
        )
        if sum(bool(x[0]) for x in buttonSet):
            buttons = vSizer()
            for flag, defLabel, func in buttonSet:
                if not flag:
                    continue
                label = (flag == True and defLabel) or flag
                buttons.Add(button(self, label, onClick=func), 0, wx.LEFT | wx.TOP, 4)
        else:
            buttons = None
        # --Layout
        sizer = vSizer(
            (captionText, 0, wx.LEFT | wx.TOP, 4),
            (
                hSizer(
                    (self.list, 1, wx.EXPAND | wx.TOP, 4),
                    (self.gInfoBox, self.data.infoWeight, wx.EXPAND | wx.TOP, 4),
                    (buttons, 0, wx.EXPAND),
                ),
                1,
                wx.EXPAND,
            ),
        )
        # --Done
        className = data.__class__.__name__
        if className in sizes:
            self.SetSizer(sizer)
            self.SetSize(sizes[className])
        else:
            self.SetSizerAndFit(sizer)

    def GetSelected(self):
        return self.list.GetNextItem(-1, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

    # --Checklist commands
    def DoCheck(self, event):
        """Handles check/uncheck of listbox item."""
        index = event.GetSelection()
        item = self.items[index]
        if self.list.IsChecked(index):
            self.data.check(item)
        else:
            self.data.uncheck(item)

    # --List Commands
    def DoAction(self, event):
        """Acts on the selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        itemDex = selections[0]
        item = self.items[itemDex]
        self.data.action(item)

    def DoAdd(self, event):
        """Adds a new item."""
        newItem = self.data.add()
        if newItem and newItem not in self.items:
            self.items = self.data.getItemList()
            index = self.items.index(newItem)
            self.list.InsertItems([newItem], index)

    def DoEdit(self, event):
        """Edits the selected item."""
        raise UncodedError

    def DoRename(self, event):
        """Renames selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        # --Rename it
        itemDex = selections[0]
        curName = self.list.GetString(itemDex)
        # --Dialog
        newName = askText(self, _("Rename to:"), _("Rename"), curName)
        if not newName or newName == curName:
            return
        elif newName in self.items:
            showError(self, _("Name must be unique."))
        elif self.data.rename(curName, newName):
            self.items[itemDex] = newName
            self.list.SetString(itemDex, newName)

    def DoRemove(self, event):
        """Removes selected item."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        # --Data
        itemDex = selections[0]
        item = self.items[itemDex]
        if not self.data.remove(item):
            return
        # --GUI
        del self.items[itemDex]
        self.list.Delete(itemDex)
        if self.gInfoBox:
            self.gInfoBox.DiscardEdits()
            self.gInfoBox.SetValue("")

    # --Show Info
    def OnSelect(self, event):
        """Handle show info (item select) event."""
        index = event.GetSelection()
        item = self.items[index]
        self.data.select(item)
        if self.gInfoBox:
            self.gInfoBox.DiscardEdits()
            self.gInfoBox.SetValue(self.data.getInfo(item))

    def OnInfoEdit(self, event):
        """Info box text has been edited."""
        selections = self.list.GetSelections()
        if not selections:
            return bell()
        item = self.items[selections[0]]
        if self.gInfoBox.IsModified():
            self.data.setInfo(item, self.gInfoBox.GetValue())

    # --Save/Cancel
    def DoSave(self, event):
        """Handle save button."""
        self.data.save()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.EndModal(wx.ID_OK)

    def DoCancel(self, event):
        """Handle save button."""
        self.data.cancel()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.EndModal(wx.ID_CANCEL)

    # --Window Closing
    def OnCloseWindow(self, event):
        """Handle window close event.
        Remember window size, position, etc."""
        self.data.close()
        sizes[self.data.__class__.__name__] = self.GetSizeTuple()
        self.Destroy()


# ------------------------------------------------------------------------------


class Picture(wx.Window):
    """Picture panel."""

    def __init__(self, parent, width, height, scaling=1, style=0):
        """Initialize."""
        wx.Window.__init__(self, parent, defId, size=(width, height), style=style)
        self.scaling = scaling
        self.bitmap = None
        self.scaled = None
        self.oldSize = (0, 0)
        self.SetSizeHints(width, height, width, height)
        # --Events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def SetBitmap(self, bitmap):
        """Set bitmap."""
        self.bitmap = bitmap
        self.Rescale()
        self.Refresh()

    def Rescale(self):
        """Updates scaled version of bitmap."""
        picWidth, picHeight = self.oldSize = self.GetSizeTuple()
        bitmap = self.scaled = self.bitmap
        if not bitmap:
            return
        imgWidth, imgHeight = bitmap.GetWidth(), bitmap.GetHeight()
        if self.scaling == 2 or (
            self.scaling == 1 and (imgWidth > picWidth or imgHeight > picHeight)
        ):
            image = bitmap.ConvertToImage()
            factor = min(1.0 * picWidth / imgWidth, 1.0 * picHeight / imgHeight)
            newWidth, newHeight = int(factor * imgWidth), int(factor * imgHeight)
            self.scaled = image.Scale(newWidth, newHeight).ConvertToBitmap()

    def OnPaint(self, event=None):
        """Draw bitmap or clear drawing area."""
        dc = wx.PaintDC(self)
        dc.SetBackground(wx.WHITE_BRUSH)
        if self.scaled:
            if self.GetSizeTuple() != self.oldSize:
                self.Rescale()
            panelWidth, panelHeight = self.GetSizeTuple()
            xPos = max(0, (panelWidth - self.scaled.GetWidth()) / 2)
            yPos = max(0, (panelHeight - self.scaled.GetHeight()) / 2)
            dc.Clear()
            dc.DrawBitmap(self.scaled, xPos, yPos, False)
        else:
            dc.Clear()

    def OnSize(self, event):
        self.Refresh()


# ------------------------------------------------------------------------------


class Progress(bolt.Progress):
    """Progress as progress dialog."""

    def __init__(
        self,
        title=_("Progress"),
        message=" " * 60,
        parent=None,
        style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE,
    ):
        """Init."""
        if sys.version[:3] != "2.4":
            style |= wx.PD_SMOOTH
        self.dialog = wx.ProgressDialog(title, message, 100, parent, style)
        bolt.Progress.__init__(self)
        self.message = message
        self.isDestroyed = False
        self.prevMessage = ""
        self.prevState = -1
        self.prevTime = 0

    def doProgress(self, state, message):  # Polemos: bug fix.
        if not self.dialog:
            raise StateError(_("Dialog already destroyed."))
        elif (
            state == 0
            or state == 1
            or (message != self.prevMessage)
            or (state - self.prevState) > 0.05
            or (time.time() - self.prevTime) > 0.5
        ):
            if message != self.prevMessage:
                self.dialog.Update(int(state * 100), message)
            else:
                self.dialog.Update(int(state * 100))
            wx.Yield()
            self.prevMessage = message
            self.prevState = state
            self.prevTime = time.time()

    def Destroy(self):
        if self.dialog:
            self.dialog.Destroy()
            self.dialog = None


# ------------------------------------------------------------------------------


class Tank(wx.Panel):  # Polemos: Edits
    """'Tank' format table. Takes the form of a wxListCtrl in Report mode,
    with multiple columns and (optionally) column an item menus."""

    class ListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
        """List control extended with the wxPython auto-width mixin class."""

        def __init__(self, parent, id, pos=defPos, size=defSize, style=0):
            """Init."""
            wx.ListCtrl.__init__(self, parent, id, pos, size, style=style)
            ListCtrlAutoWidthMixin.__init__(self)

    mainMenu = None
    itemMenu = None
    prev_item = None

    def __init__(
        self,
        parent,
        data,
        icons=None,
        mainMenu=None,
        itemMenu=None,
        details=None,
        id=-1,
        style=(wx.LC_REPORT | wx.LC_SINGLE_SEL),
    ):
        """Init."""
        wx.Panel.__init__(self, parent, id, style=wx.WANTS_CHARS)
        # --Data
        if icons is None:
            icons = {}
        self.data = data
        self.icons = icons  # --Default to balt image collection.
        self.mainMenu = mainMenu or self.__class__.mainMenu
        self.itemMenu = itemMenu or self.__class__.itemMenu
        self.details = details
        # --Item/Id mapping
        self.nextItemId = 1
        self.item_itemId = {}
        self.itemId_item = {}
        # --Layout
        sizer = vSizer()
        self.SetSizer(sizer)
        self.SetSizeHints(50, 50)
        # --ListCtrl
        self.gList = gList = Tank.ListCtrl(self, -1, style=style)
        if self.icons:
            gList.SetImageList(icons.GetImageList(), wx.IMAGE_LIST_SMALL)
        # --State info
        self.mouseItem = None
        self.mouseTexts = {}
        self.mouseTextPrev = ""
        # --Columns
        self.UpdateColumns()
        # --Items
        self.sortDirty = False
        self.UpdateItems()
        # --Events
        self.Bind(wx.EVT_SIZE, self.OnSize)
        # --Events: Items
        gList.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        gList.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.DoItemMenu)
        gList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        gList.Bind(wx.EVT_LIST_BEGIN_LABEL_EDIT, self.OnStartLabelEdit)
        # --Events: Columns
        gList.Bind(wx.EVT_LIST_COL_CLICK, self.OnColumnClick)
        gList.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.DoColumnMenu)
        gList.Bind(wx.EVT_LIST_COL_END_DRAG, self.OnColumnResize)
        # --Mouse movement
        gList.Bind(wx.EVT_MOTION, self.OnMouse)
        gList.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouse)
        gList.Bind(wx.EVT_SCROLLWIN, self.OnScroll)
        # --ScrollPos
        gList.ScrollLines(data.getParam("vScrollPos", 0))
        data.setParam("vScrollPos", gList.GetScrollPos(wx.VERTICAL))
        # --Hack: Default text item background color
        self.defaultTextBackground = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)

    def GetItem(self, index):
        """Returns item for specified list index."""
        return self.itemId_item[self.gList.GetItemData(index)]

    def GetId(self, item):
        """Returns id for specified item, creating id if necessary."""
        id = self.item_itemId.get(item)
        if id:
            return id
        # --Else get a new item id.
        id = self.nextItemId
        self.nextItemId += 1
        self.item_itemId[item] = id
        self.itemId_item[id] = item
        return id

    def GetIndex(self, item):
        """Returns index for specified item."""
        return self.gList.FindItemData(-1, self.GetId(item))

    def UpdateIds(self):
        """Updates item/id mappings to account for removed items."""
        removed = set(self.item_itemId.keys()) - set(self.data.keys())
        for item in removed:
            itemId = self.item_itemId[item]
            del self.item_itemId[item]
            del self.itemId_item[itemId]

    def UpdateColumns(self):
        """Create/name columns in ListCtrl."""
        data = self.data
        columns = data.getParam("columns", data.tankColumns[:])
        col_name = data.getParam("colNames", {})
        col_width = data.getParam("colWidths", {})
        col_align = data.getParam("colAligns", {})
        for index, column in enumerate(columns):
            name = col_name.get(column, _(column))
            width = col_width.get(column, 30)
            align = wxListAligns[col_align.get(column, "LEFT")]
            if conf.settings["mash.large.fonts"]:
                import gui.interface

                self.gList.SetFont(wx.Font(*gui.interface.internalStyle["big.font"]))
            self.gList.InsertColumn(index, name, align)
            self.gList.SetColumnWidth(index, width)

    def UpdateItem(self, index, item=None, selected=tuple()):
        """Populate Item for specified item."""
        import gui.interface

        if index < 0:
            return
        data, gList = self.data, self.gList
        item = item or self.GetItem(index)
        for iColumn, column in enumerate(data.getColumns(item)):
            gList.SetStringItem(index, iColumn, column)
        gItem = gList.GetItem(index)
        iconKey, textKey, backKey = data.getGuiKeys(item)
        if iconKey and self.icons:
            gItem.SetImage(self.icons[iconKey])
        if textKey:  # Polemos: Theme engine
            if (
                textKey == "BLACK"
                and gui.interface.style["lists.font.color"] is not None
            ):
                gItem.SetTextColour(gui.interface.style["lists.font.color"])
            else:
                gItem.SetTextColour(colors[textKey])
        else:
            if gui.interface.style["lists.font.color"] is None:
                gItem.SetTextColour(gList.GetTextColour())
            else:
                gItem.SetTextColour(gui.interface.style["lists.font.color"])
        if backKey:
            gItem.SetBackgroundColour(colors[backKey])
        else:
            gItem.SetBackgroundColour(self.defaultTextBackground)
        gItem.SetState((0, wx.LIST_STATE_SELECTED)[item in selected])
        gItem.SetData(self.GetId(item))
        gList.SetItem(gItem)

    def UpdateItems(self, selected="SAME"):
        """Update all items."""
        gList = self.gList
        items = set(self.data.keys())
        index = 0
        # --Items to select afterwards. (Defaults to current selection.)
        if selected == "SAME":
            selected = set(self.GetSelected())
        # --Update existing items.
        while index < gList.GetItemCount():
            item = self.GetItem(index)
            if item not in items:
                gList.DeleteItem(index)
            else:
                self.UpdateItem(index, item, selected)
                items.remove(item)
                index += 1
        # --Add remaining new items
        for item in items:
            gList.InsertStringItem(index, "")
            self.UpdateItem(index, item, selected)
            index += 1
        # --Cleanup
        self.UpdateIds()
        self.SortItems()
        self.mouseTexts.clear()

    def SortItems(self, column=None, reverse="CURRENT"):
        """Sort items. Real work is done by data object, and that completed
        sort is then "cloned" list through an intermediate cmp function.

        column: column to sort. Defaults to current sort column.

        reverse:
        * True: Reverse order
        * False: Normal order
        * 'CURRENT': Same as current order for column.
        * 'INVERT': Invert if column is same as current sort column.
        """
        # --Parse column and reverse arguments.
        data = self.data
        if self.sortDirty:
            self.sortDirty = False
            (column, reverse) = (None, "CURRENT")
        curColumn = data.defaultParam("colSort", data.tankColumns[0])
        column = column or curColumn
        curReverse = data.defaultParam("colReverse", {}).get(column, False)
        if reverse == "INVERT" and column == curColumn:
            reverse = not curReverse
        elif reverse in ("INVERT", "CURRENT"):
            reverse = curReverse
        data.updateParam("colReverse")[column] = reverse
        self.isReversed = reverse  # Polemos: Get reverse flag.
        data.setParam("colSort", column)
        # --Sort
        items = self.data.getSorted(column, reverse)
        sortDict = dict((self.item_itemId[y], x) for x, y in enumerate(items))
        self.gList.SortItems(lambda x, y: cmp(sortDict[x], sortDict[y]))
        # --Done
        self.mouseTexts.clear()

    def RefreshData(self):
        """Refreshes underlying data."""
        self.data.refresh()

    def RefreshReport(self):
        """(Optionally) Shows a report of changes after a data refresh."""
        report = self.data.getRefreshReport()
        if report:
            showInfo(self, report, self.data.title)

    def RefreshUI(self, items="ALL", details="SAME"):
        """Refreshes UI for specified file."""
        selected = self.GetSelected()
        if details == "SAME":
            details = self.GetDetailsItem()
        elif details:
            selected = tuple(details)
        if items == "ALL":
            self.UpdateItems(selected=selected)
        elif items in self.data:
            self.UpdateItem(self.GetIndex(items), items, selected=selected)
        else:  # --Iterable
            for index in xrange(self.gList.GetItemCount()):
                if self.GetItem(index) in set(items):
                    self.UpdateItem(index, None, selected=selected)
        self.RefreshDetails(details)

    def GetDetailsItem(self):  # --Details view (if it exists)
        """Returns item currently being shown in details view."""
        if self.details:
            return self.details.GetDetailsItem()
        return None

    def RefreshDetails(self, item=None):
        """Refreshes detail view associated with data from item."""
        if self.details:
            return self.details.RefreshDetails(item)
        item = item or self.GetDetailsItem()
        if item not in self.data:
            item = None

    def GetSelected(self):
        """Return list of items selected (highlighted) in the interface."""
        gList = self.gList
        return [
            self.GetItem(x)
            for x in xrange(gList.GetItemCount())
            if gList.GetItemState(x, wx.LIST_STATE_SELECTED)
        ]

    def ClearSelected(self):
        """Unselect all items."""
        gList = self.gList
        for index in xrange(gList.GetItemCount()):
            if gList.GetItemState(index, wx.LIST_STATE_SELECTED):
                gList.SetItemState(index, 0, wx.LIST_STATE_SELECTED)

    def OnMouse(self, event):  # Polemos: Added a small effect.
        """Check mouse motion to detect right click event."""
        if event.Moving():
            (mouseItem, mouseHitFlag) = self.gList.HitTest(event.GetPosition())
            if mouseItem == -1:
                pass
            elif mouseItem != self.mouseItem:
                self.mouseItem = mouseItem
                self.lastItemColor = (
                    mouseItem,
                    self.gList.GetItemTextColour(mouseItem),
                )
                self.MouseEffect(mouseItem)
        elif event.Leaving() and self.mouseItem is not None or self.mouseItem != -1:
            try:
                if conf.settings["interface.lists.color"]:
                    self.gList.SetItemTextColour(
                        self.lastItemColor[0], self.lastItemColor[1]
                    )
            except:
                pass
            self.mouseItem = None
            self.MouseEffect(None)
        event.Skip()

    def MouseEffect(self, item):  # Polemos: Added a small effect.
        """Handle mouse over item by showing tip or similar."""
        if conf.settings["interface.lists.color"]:
            import gui.interface

            try:
                self.gList.SetItemTextColour(item, gui.interface.style["mouse.hover"])
                self.gList.SetItemTextColour(self.prev_item[0], self.prev_item[1])
            except:
                pass
            try:
                self.prev_item = self.lastItemColor
            except:
                pass  # Happens

    def OnItemSelected(self, event):  # Polemos: a small hook for the main menu.
        """Item Selected: Refresh details."""
        self.RefreshDetails(self.GetItem(event.m_itemIndex))

    def OnStartLabelEdit(self, event):
        """We don't support renaming labels, so don't let anyone start"""
        event.Veto()

    def OnSize(self, event):
        """Panel size was changed. Change gList size to match."""
        size = self.GetClientSizeTuple()
        self.gList.SetSize(size)

    def OnScroll(self, event):
        """Event: List was scrolled. Save so can be accessed later."""
        if event.GetOrientation() == wx.VERTICAL:
            self.data.setParam("vScrollPos", event.GetPosition())
        event.Skip()

    def OnColumnResize(self, event):
        """Column resized. Save column size info."""
        iColumn = event.GetColumn()
        column = self.data.getParam("columns")[iColumn]
        self.data.updateParam("colWidths")[column] = self.gList.GetColumnWidth(iColumn)

    def OnLeftDown(self, event):
        """Left mouse button was pressed."""
        event.Skip()

    def OnColumnClick(self, event):
        """Column header was left clicked on. Sort on that column."""
        columns = self.data.getParam("columns")
        self.SortItems(columns[event.GetColumn()], "INVERT")

    def DoColumnMenu(self, event):
        """Show column menu."""
        if not self.mainMenu:
            return
        iColumn = event.GetColumn()
        menu = wx.Menu()
        for item in self.mainMenu:
            item.AppendToMenu(menu, self, iColumn)
        self.PopupMenu(menu)
        menu.Destroy()

    def DoItemMenu(self, event):
        """Show item menu."""
        if not self.itemMenu:
            return
        selected = self.GetSelected()
        if not selected:
            return
        menu = wx.Menu()
        for item in self.itemMenu:
            item.AppendToMenu(menu, self, selected)
        self.PopupMenu(menu)
        menu.Destroy()

    def DeleteSelected(self):  # --Standard data commands
        """Deletes selected items."""
        items = self.GetSelected()
        if not items:
            return
        message = gettext.gettext(
            "Delete these items? This operation cannot be undone."
        )
        message += "\n* " + "\n* ".join([self.data.getName(x) for x in items])
        if not askYes(self, message, _("Delete Items")):
            return
        for item in items:
            del self.data[item]
        self.RefreshUI()
        self.data.setChanged()


# Links -----------------------------------------------------------------------


class Links(list):
    """List of menu or button links."""

    class LinksPoint:
        """Point in a link list. For inserting, removing, appending items."""

        def __init__(self, list, index):
            self._list = list
            self._index = index

        def remove(self):
            del self._list[self._index]

        def replace(self, item):
            self._list[self._index] = item

        def insert(self, item):
            self._list.insert(self._index, item)
            self._index += 1

        def append(self, item):
            self._list.insert(self._index + 1, item)
            self._index += 1

    def getClassPoint(self, classObj):  # --Access functions:
        """Returns index"""
        for index, item in enumerate(self):
            if isinstance(item, classObj):
                return Links.LinksPoint(self, index)
        else:
            return None


# ------------------------------------------------------------------------------


class Link:
    """Link is a command to be encapsulated in a graphic element (menu item, button, etc.)"""

    def __init__(self):
        """Init."""
        self.id = None

    def AppendToMenu(self, menu, window, data):
        """Append self to menu as menu item."""
        if isinstance(window, Tank):
            self.gTank = window
            self.selected = window.GetSelected()
            self.data = window.data
            self.title = window.data.title
        else:
            self.window = window
            self.data = data
        # --Generate self.id if necessary (i.e. usually)
        if not self.id:
            self.id = wx.NewId()
        wx.EVT_MENU(window, self.id, self.Execute)

    def Execute(self, event):
        """Event: link execution."""
        raise AbstractError


# ------------------------------------------------------------------------------


class SeparatorLink(Link):
    """Link that acts as a separator item in menus."""

    def AppendToMenu(self, menu, window, data):
        """Add separator to menu."""
        menu.AppendSeparator()


# ------------------------------------------------------------------------------


class MenuLink(Link):
    """Defines a submenu. Generally used for submenus of large menus."""

    def __init__(self, name, oneDatumOnly=False):
        """Initialize. Submenu items should append to self.links."""
        Link.__init__(self)
        self.name = name
        self.links = Links()
        self.oneDatumOnly = oneDatumOnly

    def AppendToMenu(self, menu, window, data):
        """Add self as submenu (along with submenu items) to menu."""
        subMenu = wx.Menu()
        for link in self.links:
            link.AppendToMenu(subMenu, window, data)
        menu.AppendMenu(-1, self.name, subMenu)
        if self.oneDatumOnly and len(data) != 1:
            id = menu.FindItem(self.name)
            menu.Enable(id, False)


# Tanks Links -----------------------------------------------------------------


class Tanks_Open(Link):
    """Opens data directory in explorer."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("Open..."))
        menu.AppendItem(menuItem)

    def Execute(self, event):
        """Handle selection."""
        dir = self.data.dir
        dir.makedirs()
        dir.start()


# Tank Links ------------------------------------------------------------------


class Tank_Delete(Link):
    """Deletes selected file from tank."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menu.AppendItem(wx.MenuItem(menu, self.id, _("Delete")))

    def Execute(self, event):
        try:
            wx.BeginBusyCursor()
            self.gTank.DeleteSelected()
        finally:
            wx.EndBusyCursor()


# ------------------------------------------------------------------------------


class Tank_Open(Link):
    """Open selected file(s)."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("Open..."))
        menu.AppendItem(menuItem)
        menuItem.Enable(bool(self.selected))

    def Execute(self, event):
        """Handle selection."""
        dir = self.data.dir
        for file in self.selected:
            dir.join(file).start()


# ------------------------------------------------------------------------------


class Tank_Duplicate(Link):  # Polemos fixes
    """Create a duplicate of a tank item, assuming that tank item is a file, and using a SaveAs dialog."""

    def AppendToMenu(self, menu, window, data):
        Link.AppendToMenu(self, menu, window, data)
        menuItem = wx.MenuItem(menu, self.id, _("Duplicate..."))
        menu.AppendItem(menuItem)
        menuItem.Enable(len(self.selected) == 1)

    def Execute(self, event):
        srcDir = self.data.dir
        srcName = self.selected[0]
        (root, ext) = srcName.rootExt
        (destDir, destName, wildcard) = (srcDir, root + " Copy" + ext, "*" + ext)
        destPath = askSave(self.gTank, _("Duplicate as:"), destDir, destName, wildcard)
        if not destPath:
            return
        destDir, destName = destPath.headTail
        if (destDir == srcDir) and (destName == srcName):
            showError(self.window, _("Files cannot be duplicated to themselves!"))
            return
        self.data.copy(srcName, destName, destDir)
        if destDir == srcDir:
            self.gTank.RefreshUI()
