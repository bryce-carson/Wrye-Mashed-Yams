import os, re, string, sys, types
import cemetary.singletons

## TODO: what are the differences? How are f-strings handled?
from gettext import gettext as _

# from internationalization.unimash import _  # Polemos

## NOTE: what the fuck is "ETXT"? At some point the change log says ""etxtToHtml command now included.""
# ETXT
etxtHeader = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2//EN">
<HTML>
<HEAD>
<META HTTP-EQUIV="CONTENT-TYPE" CONTENT="text/html; charset=iso-8859-1">
<TITLE>%s</TITLE>
<STYLE>
H2 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #c6c63c; font-family: "Arial", serif; font-size: 12pt; page-break-before: auto; page-break-after: auto }
H3 { margin-top: 0in; margin-bottom: 0in; border-top: 1px solid #000000; border-bottom: 1px solid #000000; border-left: none; border-right: none; padding: 0.02in 0in; background: #e6e64c; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
H4 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-size: 10pt; font-style: normal; page-break-before: auto; page-break-after: auto }
H5 { margin-top: 0in; margin-bottom: 0in; font-family: "Arial", serif; font-style: italic; page-break-before: auto; page-break-after: auto }
P { margin-top: 0.01in; margin-bottom: 0.01in; font-family: "Arial", serif; font-size: 10pt; page-break-before: auto; page-break-after: auto }
P.list-1 { margin-left: 0.15in; text-indent: -0.15in }
P.list-2 { margin-left: 0.3in; text-indent: -0.15in }
P.list-3 { margin-left: 0.45in; text-indent: -0.15in }
P.list-4 { margin-left: 0.6in; text-indent: -0.15in }
P.list-5 { margin-left: 0.75in; text-indent: -0.15in }
P.list-6 { margin-left: 1.00in; text-indent: -0.15in }
.date0 { background-color: #FFAAAA }
.date1 { background-color: #ffc0b3 }
.date2 { background-color: #ffd5bb }
.date3 { background-color: #ffeac4 }
</STYLE>
</HEAD>
<BODY BGCOLOR='#ffffcc'>
"""


# Testing
def init(initLevel):
    """Initializes mosh environment to specified level.
    initLevels:
        0: Settings
        1: mwInit File
        2: modInfos
        3: saveInfos"""
    # --Settings
    mosh.initSettings()
    mwDir = mosh.settings["mwDir"]
    # --MwIniFile (initLevel >= 1)
    if initLevel < 1:
        return
    mosh.mwIniFile = mosh.MWIniFile(mwDir)
    mosh.mwIniFile.refresh()
    # --ModInfos (initLevel >= 2)
    if initLevel < 2:
        return
    mosh.modInfos = mosh.ModInfos(os.path.join(mwDir, "Data Files"))
    mosh.modInfos.refresh()
    # --SaveInfos (initLevel >= 3)
    if initLevel < 3:
        return
    mosh.saveInfos = mosh.SaveInfos(os.path.join(mwDir, "Saves"))
    mosh.saveInfos.refresh()


def tes3Hedr_testWrite(fileName):
    """Does a read write test on TES3 records."""
    init(3)
    if fileName in mosh.modInfos:
        fileInfo = mosh.modInfos[fileName]
    else:
        fileInfo = mosh.saveInfos[fileName]
    # --Mark as changed
    oldData = fileInfo.tes3.hedr.data
    fileInfo.tes3.hedr.changed = True


def lcvNightSort():  # Edit Plus Text Editors
    """TextMunch: Sort LCV evening/night schedule cells, ignoring sleep state setting."""
    lines = sys.stdin.readlines()
    for line in lines:
        line = re.sub("@ night", "@ evening", line)
        line = re.sub(r"[\*\+] \.", "^ .", line)
        # Old Python 2 code.
        # print line,
        print(f"{line} ")
    # for line in lines: print line,
    for line in lines:
        print("{line} ")


# Main
if __name__ == "__main__":
    callables.main()
# -*- coding: utf-8 -*-

# Wrye Mash Polemos fork GPL License and Copyright Notice ==============================
#
# This file is part of Wrye Mash Polemos fork.
#
# Wrye Mash, Polemos fork Copyright (C) 2017-2021 Polemos
# * based on code by Yacoby copyright (C) 2011-2016 Wrye Mash Fork Python version
# * based on code by Melchor copyright (C) 2009-2011 Wrye Mash WMSA
# * based on code by Wrye copyright (C) 2005-2009 Wrye Mash
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
#
#  Copyright on the original code 2005-2009 Wrye
#  Copyright on any non trivial modifications or substantial additions 2009-2011 Melchor
#  Copyright on any non trivial modifications or substantial additions 2011-2016 Yacoby
#  Copyright on any non trivial modifications or substantial additions 2017-2020 Polemos
#
# ======================================================================================

# Original Wrye Mash License and Copyright Notice ======================================
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# ========================================================================================

# Modified by D.C.-G. < 16:35 2010-06-11 > for UtilsPanel extension.
# Modified by Polemos :) in 2,000,000 places, 2018~.


import locale
import time, traceback
from threading import Thread as Thread  # Polemos
from subprocess import PIPE, check_call  # Polemos
from sfix import Popen  # Polemos
import io, ushlex, scandir  # Polemos
from unimash import uniChk, encChk, _  # Polemos
import array, cPickle, cStringIO, copy, math, os, re, shutil, string
import struct, sys, stat, bolt
from bolt import LString, GPath, DataDict, SubProgress
import compat, mush

# Exceptions
from merrors import mError as MoshError, Tes3Error as Tes3Error
from merrors import (
    AbstractError as AbstractError,
    ArgumentError as ArgumentError,
    StateError as StateError,
)
from merrors import UncodedError as UncodedError, ConfError as ConfError
from merrors import (
    Tes3ReadError as Tes3ReadError,
    Tes3RefError as Tes3RefError,
    Tes3SizeError as Tes3SizeError,
)
from merrors import (
    MaxLoadedError as MaxLoadedError,
    SortKeyError as SortKeyError,
    Tes3UnknownSubRecord as Tes3UnknownSubRecord,
)


# Singletons, Constants
MashDir = os.path.dirname(sys.argv[0])  # Polemos
DETACHED_PROCESS = 0x00000008  # Polemos
# --File Singletons
mwIniFile = None  # --MWIniFile singleton
modInfos = None  # --ModInfos singleton
saveInfos = None  # --SaveInfos singleton
# --Settings
dirs = {}
settings = None
# --Default settings
settingDefaults = {
    "mosh.modInfos.resetMTimes": 0,
    "mosh.modInfos.objectMaps": r"Mash\ObjectMaps.pkl",
    "mosh.fileInfo.backupDir": r"Mash\Backups",
    "mosh.fileInfo.hiddenDir": r"Mash\Hidden",
    "mosh.fileInfo.snapshotDir": r"Mash\Snapshots",
}


def formatInteger(value):
    """Convert integer to string formatted to locale."""
    return locale.format("%d", int(value), 1)


def formatDate(value):  # Polemos
    """Convert time to string formatted to locale's default date/time."""
    form = "%x, %H:%M:%S"
    try:
        return time.strftime(form, time.localtime(value))
    except:  # Needed when installers are outside Unix Epoch
        return time.strftime(form, time.localtime(0))


def megethos(num):  # Polemos
    """Convert byte sizes to KBs, MBs or GBs."""
    digits = len(str(num))
    if digits <= 3:
        return "%dB" % (num)
    elif 4 <= digits <= 6:
        return "%dKB" % (num / 1024)
    elif 7 <= digits <= 9:
        return "%dMB" % (num / 1024**2)
    elif digits >= 10:
        return "%dGB" % (num / 1024**3)


# Data Dictionaries -----------------------------------------------------------


class Settings:  # Polemos: Added revert to backup configuration.
    """Settings dictionary. Changes are saved to pickle file."""

    def __init__(self, path="settings.pkl"):
        """Initialize. Read settings from pickle file."""
        self.path = path.encode("utf-8")
        self.changed = []
        self.deleted = []
        self.data = {}
        # Check if the settings file is missing and if there is an available backup to restore.
        if not os.path.exists(self.path) and os.path.exists(self.path + ".bak"):
            shutil.copyfile(
                os.path.join(MashDir, self.path + ".bak"),
                os.path.join(MashDir, self.path),
            )
        # --Load
        if os.path.exists(self.path):
            inData = compat.uncpickle(self.path.encode("utf-8"))
            self.data.update(inData)

    def loadDefaults(self, defaults):
        """Add default settings to dictionary. Will not replace values that are already set."""
        for key in defaults.keys():
            if key not in self.data:
                self.data[key] = defaults[key]

    def save(self):
        """Save to pickle file. Only key/values marked as changed are saved."""
        # --Data file exists?
        filePath = self.path.encode("utf-8")
        if os.path.exists(filePath):
            outData = compat.uncpickle(filePath)
            # --Delete some data?
            for key in self.deleted:
                if key in outData:
                    del outData[key]
        else:
            outData = {}
        # --Write touched data
        for key in self.changed:
            outData[key] = self.data[key]
        # --Pickle it
        tempPath = ("%s.tmp" % filePath).encode("utf-8")
        cPickle.dump(outData, open(tempPath.encode("utf-8"), "wb"), -1)
        renameFile(tempPath.encode("utf-8"), filePath.encode("utf-8"), True)

    def setChanged(self, key):
        """Marks given key as having been changed. Use if value is a dictionary, list or other object."""
        if key not in self.data:
            raise ArgumentError(_("No settings data for %s" % key))
        if key not in self.changed:
            self.changed.append(key)

    def getChanged(self, key, default=None):
        """Gets and marks as changed."""
        if default is not None and key not in self.data:
            self.data[key] = default
        self.setChanged(key)
        return self.data.get(key)

    # --Dictionary Emulation
    def has_key(self, key):
        """Dictionary emulation."""
        return self.data.has_key(key)

    def get(self, key, default=None):
        """Dictionary emulation."""
        return self.data.get(key.encode("utf-8"), default)

    def setdefault(self, key, default):
        """Dictionary emulation."""
        return self.data.setdefault(key.encode("utf-8"), default)

    def __contains__(self, key):
        """Dictionary emulation."""
        return self.data.has_key(key.encode("utf-8"))

    def __getitem__(self, key):
        """Dictionary emulation."""
        return self.data[key.encode("utf-8")]

    def __setitem__(self, key, value):
        """Dictionary emulation. Marks key as changed."""
        if key in self.deleted:
            self.deleted.remove(key)
        if key not in self.changed:
            self.changed.append(key)
        self.data[key] = value

    def __delitem__(self, key):
        """Dictionary emulation. Marks key as deleted."""
        if key in self.changed:
            self.changed.remove(key)
        if key not in self.deleted:
            self.deleted.append(key)
        del self.data[key]


class TableColumn:
    """Table accessor that presents table column as a dictionary."""

    def __init__(self, table, column):
        self.table = table
        self.column = column

    # --Dictionary Emulation
    def keys(self):
        """Dictionary emulation."""
        table = self.table
        column = self.column
        return [key for key in table.data.keys() if (column in table.data[key])]

    def has_key(self, key):
        """Dictionary emulation."""
        return self.__contains__(key)

    def clear(self):
        """Dictionary emulation."""
        self.table.delColumn(self.column)

    def get(self, key, default=None):
        """Dictionary emulation."""
        return self.table.getItem(key, self.column, default)

    def __contains__(self, key):
        """Dictionary emulation."""
        tableData = self.table.data
        return tableData.has_key(key) and tableData[key].has_key(self.column)

    def __getitem__(self, key):
        """Dictionary emulation."""
        return self.table.data[key][self.column]

    def __setitem__(self, key, value):
        """Dictionary emulation. Marks key as changed."""
        self.table.setItem(key, self.column, value)

    def __delitem__(self, key):
        """Dictionary emulation. Marks key as deleted."""
        self.table.delItem(key, self.column)


class Table:
    """Simple data table of rows and columns, saved in a pickle file."""

    def __init__(self, path):
        """Intialize and read data from file, if available."""
        self.path = path
        self.data = {}
        self.hasChanged = False
        # --Load
        if os.path.exists(self.path):
            inData = compat.uncpickle(self.path)
            self.data.update(inData)

    def save(
        self,
    ):  # Polemos: Unicode fix. Strange one. Was it mine? Questions, questions, questions... (a)
        """Saves to pickle file."""
        if self.hasChanged:
            filePath = self.path  # .encode('utf-8')
            tempPath = "%s.tmp" % filePath
            fileDir = os.path.split(filePath)[0]
            if not os.path.exists(fileDir):
                os.makedirs(fileDir)
            cPickle.dump(self.data, open(tempPath, "wb"), -1)
            renameFile(tempPath, filePath, True)
            self.hasChanged = False

    def getItem(self, row, column, default=None):
        """Get item from row, column. Return default if row, column doesn't exist."""
        data = self.data
        if row in data and column in data[row]:
            return data[row][column]
        else:
            return default

    def getColumn(self, column):
        """Returns a data accessor for column."""
        return TableColumn(self, column)

    def setItem(self, row, column, value):
        """Set value for row, column."""
        data = self.data
        if row not in data:
            data[row] = {}
        data[row][column] = value
        self.hasChanged = True

    def delItem(self, row, column):
        """Deletes item in row, column."""
        data = self.data
        if row in data and column in data[row]:
            del data[row][column]
            self.hasChanged = True

    def delRow(self, row):
        """Deletes row."""
        data = self.data
        if row in data:
            del data[row]
            self.hasChanged = True

    def delColumn(self, column):
        """Deletes column of data."""
        data = self.data
        for rowData in data.values():
            if column in rowData:
                del rowData[column]
                self.hasChanged = True

    def moveRow(self, oldRow, newRow):
        """Renames a row of data."""
        data = self.data
        if oldRow in data:
            data[newRow] = data[oldRow]
            del data[oldRow]
            self.hasChanged = True

    def copyRow(self, oldRow, newRow):
        """Copies a row of data."""
        data = self.data
        if oldRow in data:
            data[newRow] = data[oldRow].copy()
            self.hasChanged = True


# ------------------------------------------------------------------------------


class PickleDict(bolt.PickleDict):
    """Dictionary saved in a pickle file. Supports older mash pickle file formats."""

    def __init__(self, path, oldPath=None, readOnly=False):
        """Initialize."""
        bolt.PickleDict.__init__(self, path, readOnly)
        self.oldPath = oldPath or GPath("")

    def exists(self):
        """See if pickle file exists."""
        return bolt.PickleDict.exists(self) or self.oldPath.exists()

    def load(self):
        """Loads vdata and data from file or backup file.

        If file does not exist, or is corrupt, then reads from backup file. If
        backup file also does not exist or is corrupt, then no data is read. If
        no data is read, then self.data is cleared.

        If file exists and has a vdata header, then that will be recorded in
        self.vdata. Otherwise, self.vdata will be empty.

        Returns:
        0: No data read (files don't exist and/or are corrupt)
        1: Data read from file
        2: Data read from backup file
        """
        result = bolt.PickleDict.load(self)
        if not result and self.oldPath.exists():
            self.data.update(compat.uncpickle(self.oldPath.parsePath()))
            result = 1
        # --Done
        return result

    def save(self):
        """Save to pickle file."""
        saved = bolt.PickleDict.save(self)
        if saved:
            self.oldPath.remove()
            self.oldPath.backup.remove()
        return saved


# Util Functions --------------------------------------------------------------


# Common re's, Unix new lines
reUnixNewLine = re.compile(r"(?<!\r)\n")
reSaveFile = re.compile("\.ess$", re.I)
reModExt = re.compile(r"\.es[mp](.ghost)?$", re.I)

# --Version number in tes3.hedr
reVersion = re.compile(r"^(Version:?) *([-0-9\.]*\+?) *\r?$", re.M)

# --Misc
reExGroup = re.compile("(.*?),")


def cstrip(inString):
    """Convert c-string (null-terminated string) to python string."""
    zeroDex = inString.find("\x00")
    if zeroDex == -1:
        return inString
    else:
        return inString[:zeroDex]


def dictFromLines(lines, sep=None):
    """Generate a dictionary from a string with lines, stripping comments and skipping empty strings."""
    reComment = re.compile("#.*")
    temp = [reComment.sub("", x).strip() for x in lines.split("\n")]
    if sep is None or type(sep) == type(""):
        temp = dict([x.split(sep, 1) for x in temp if x])
    else:  # --Assume re object.
        temp = dict([sep.split(x, 1) for x in temp if x])
    return temp


def getMatch(reMatch, group=0):
    """Returns the match or an empty string."""
    if reMatch:
        return reMatch.group(group)
    else:
        return ""


y2038Resets = []


def getmtime(path):
    """Returns mtime for path. But if mtime is outside of epoch, then resets mtime to an in-epoch date and uses that."""
    import random

    mtime = os.path.getmtime(path)
    # --Y2038 bug? (os.path.getmtime() can't handle years over unix epoch)
    if mtime <= 0:
        # --Kludge mtime to a random time within 10 days of 1/1/2037
        mtime = time.mktime((2037, 1, 1, 0, 0, 0, 3, 1, 0))
        mtime += random.randint(0, 10 * 24 * 60 * 60)  # --10 days in seconds
        os.utime(path, (time.time(), mtime))
        y2038Resets.append(os.path.basename(path))
    return mtime


def iff(bool, trueValue, falseValue):
    """Return true or false value depending on a boolean test."""
    if bool:
        return trueValue
    else:
        return falseValue


def invertDict(indict):
    """Invert a dictionary."""
    return {y: x for x, y in indict.items()}


def listFromLines(lines):
    """Generate a list from a string with lines, stripping comments and skipping empty strings."""
    reComment = re.compile("#.*")
    temp = [reComment.sub("", x).strip() for x in lines.split("\n")]
    temp = [x for x in temp if x]
    return temp


def listSubtract(alist, blist):
    """Return a copy of first list minus items in second list."""
    result = []
    for item in alist:
        if item not in blist:
            result.append(item)
    return result


def renameFile(oldPath, newPath, makeBack=False):
    """Moves file from oldPath to newPath. If newPath already exists then it
    will either be moved to newPath.bak or deleted depending on makeBack."""
    if os.path.exists(newPath):
        if makeBack:
            backPath = "%s.bak" % newPath
            if os.path.exists(backPath):
                os.remove(backPath)
            os.rename(newPath, backPath)
        else:
            os.remove(newPath)
    os.rename(oldPath, newPath)


def rgbString(red, green, blue):
    """Converts red, green blue ints to rgb string."""
    return chr(red) + chr(green) + chr(blue)


def rgbTuple(rgb):
    """Converts red, green, blue string to tuple."""
    return struct.unpack("BBB", rgb)


def winNewLines(inString):
    """Converts unix newlines to windows newlines."""
    return reUnixNewLine.sub("\r\n", inString)


# IO Wrappers -----------------------------------------------------------------
# TES3 Abstract ---------------------------------------------------------------
# TES3 Data --------------------------------------------------------------------
# File System -----------------------------------------------------------------
class MWIniFile:  # Polemos: OpenMW/TES3mp support
    """Morrowind.ini/OpenMW.cfg file."""

    def __init__(self, dr):
        """Init."""
        self.dir = dr
        self.openmw = settings["openmw"]
        if not self.openmw:  # Morrowind
            # MWSE max plugins compatibility
            self.maxPlugins = 1023 if settings["mash.extend.plugins"] else 255
        elif self.openmw:  # OpenMW/TES3mp
            self.maxPlugins = None
        self.encod = settings["profile.encoding"]
        if not self.openmw:  # Morrowind
            self.path = os.path.join(self.dir, "Morrowind.ini")
        elif self.openmw:  # OpenMW/TES3mp
            self.path = os.path.join(self.dir, "openmw.cfg")
        self.datafiles_po = []
        self.confLoadLines = []
        self.DataMods = []
        self.DataModsDirs = []
        self.ConfCache = []
        self.activeFileExts = set()
        self.openmwPathDict = {}
        self.PluginSection = ""
        self.ArchiveSection = ""
        self.loadFiles = []
        self.bsaFiles = []
        self.loadFilesBad = []
        self.loadFilesExtra = []
        self.loadFilesDups = False
        self.mtime = 0
        self.size = 0
        self.doubleTime = {}
        self.exOverLoaded = set()
        self.loadOrder = tuple()
        self.filesRisk = []
        self.skip = True

    def criticalMsg(self, msg, dtype="", modal=True):
        """Show critical messages to user."""
        import gui.dialog as gui

        gui.ErrorMessage(None, msg, dtype=dtype, modal=modal)

    def getSetting(self, section, key, default=None):
        """Gets a single setting from the file."""
        section, key = map(bolt.LString, (section, key))
        settings = self.getSettings()
        if section in settings:
            return settings[section].get(key, default)
        else:
            return default

    def getSettings(self):
        """Gets settings for self."""
        reComment = re.compile(";.*")
        reSection = re.compile(r"^\[\s*(.+?)\s*\]$")
        reSetting = re.compile(r"(.+?)\s*=(.*)")
        # --Read ini file
        iniFile = GPath(self.path).codecs_open("r")
        settings = {}
        sectionSettings = None
        for line in iniFile:
            stripped = reComment.sub("", line).strip()
            maSection = reSection.match(stripped)
            maSetting = reSetting.match(stripped)
            if maSection:
                sectionSettings = settings[LString(maSection.group(1))] = {}
            elif maSetting:
                if sectionSettings is None:
                    sectionSettings = settings.setdefault(LString("General"), {})
                    self.isCorrupted = True
                sectionSettings[LString(maSetting.group(1))] = maSetting.group(
                    2
                ).strip()
        iniFile.close()
        return settings

    def saveSetting(self, section, key, value):
        """Changes a single setting in the file."""
        settings = {section: {key: value}}
        self.saveSettings(settings)

    def saveSettings(self, settings):
        """Applies dictionary of settings to ini file. Values in settings dictionary can be
        either actual values or full key=value line ending in newline char."""
        settings = {
            LString(x): {LString(u): v for u, v in y.iteritems()}
            for x, y in settings.iteritems()
        }
        reComment = re.compile(";.*")
        reSection = re.compile(r"^\[\s*(.+?)\s*\]$")
        reSetting = re.compile(r"(.+?)\s*=")
        # --Read init, write temp
        path = GPath(self.path)
        iniFile = path.codecs_open("r")
        tmpFile = path.temp.codecs_open("w")
        section = sectionSettings = None
        for line in iniFile:
            stripped = reComment.sub("", line).strip()
            maSection = reSection.match(stripped)
            maSetting = reSetting.match(stripped)
            if maSection:
                section = LString(maSection.group(1))
                sectionSettings = settings.get(section, {})
            elif maSetting and LString(maSetting.group(1)) in sectionSettings:
                key = LString(maSetting.group(1))
                value = sectionSettings[key]
                if type(value) is str and value[-1] == "\n":
                    line = value
                else:
                    line = "%s=%s\n" % (key, value)
            tmpFile.write(line)
        tmpFile.close()
        iniFile.close()
        # --Done
        path.untemp()

    def applyMit(self, mitPath):  # Polemos fixes
        """Read MIT file and apply its settings to morrowind.ini. Note: Will ONLY apply settings that already exist."""
        reComment = re.compile(";.*")
        reSection = re.compile(r"^\[\s*(.+?)\s*\]$")
        reSetting = re.compile(r"(.+?)\s*=")
        # --Read MIT file
        with io.open(mitPath, "r", encoding=self.encod, errors="replace") as mitFile:
            sectionSettings = None
            settings = {}
            for line in mitFile:
                stripped = reComment.sub("", line).strip()
                maSection = reSection.match(stripped)
                maSetting = reSetting.match(stripped)
                if maSection:
                    sectionSettings = settings[maSection.group(1)] = {}
                elif maSetting:
                    sectionSettings[maSetting.group(1).lower()] = line
        # --Discard Games Files (Loaded mods list) from settings
        for section in settings.keys():
            if section.lower() in ("game files", "archives", "mit"):
                del settings[section]
        # --Apply it
        tmpPath = "%s.tmp" % self.path
        with io.open(self.path, "r", encoding=self.encod, errors="replace") as iniFile:
            with io.open(
                tmpPath, "w", encoding=self.encod, errors="replace"
            ) as tmpFile:
                section = None
                sectionSettings = {}
                for line in iniFile:
                    stripped = reComment.sub("", line).strip()
                    maSection = reSection.match(stripped)
                    maSetting = reSetting.match(stripped)
                    if maSection:
                        section = maSection.group(1)
                        sectionSettings = settings.get(section, {})
                    elif maSetting and maSetting.group(1).lower() in sectionSettings:
                        line = sectionSettings[maSetting.group(1).lower()]
                    tmpFile.write(line)
        # --Done
        renameFile(tmpPath, self.path, True)
        self.mtime = getmtime(self.path)

    def itmDeDup(self, itms):  # Polemos
        """Item de-duplication."""
        the_set = set()
        the_set_add = the_set.add
        tmp = [x for x in itms if x]
        return [x for x in tmp if not (x in the_set or the_set_add(x))]

    def checkActiveState(self, DataDir):  # Polemos
        """True if DataDir is in load list (OpenMW/TES3mp)."""
        return DataDir in self.sanitizeDatamods(self.openmw_datamods()[:], False)

    def unloadDatamod(self, DataDir):  # Polemos
        """Remove DataDir from OpenMW."""
        DataDirF = ['data="%s"' % x.rstrip() for x in DataDir]
        [self.DataMods.remove(x) for x in DataDirF if x in self.DataMods]
        self.SaveDatamods(self.DataMods)

    def loadDatamod(self, DataDir, DataOrder):  # Polemos
        """Add DataDir to OpenMW."""
        [self.DataMods.append('data="%s"' % x) for x in DataDir]
        DataOrderF = ['data="%s"' % x for x in DataOrder]
        datamodsListExport = [x for x in DataOrderF if x in self.DataMods]
        self.SaveDatamods(datamodsListExport)

    def updateDatamods(self, DataOrder):  # Polemos
        """Update DataDirs order (active or not - OpenMW)."""
        DataOrderF = ['data="%s"' % x[1] for x in DataOrder]
        datamodsListExport = [x for x in DataOrderF if x in self.DataMods]
        self.DataMods = datamodsListExport
        self.SaveDatamods(datamodsListExport)

    def filterDataMod(self, data):  # Polemos
        """Returns DataMod path from openmw.cfg config entry."""
        if not data:
            return data
        if type(data) is list:
            return [x.split('"')[1] for x in data]
        else:
            return type(data)([x.split('"')[1] for x in data][0])

    def sanitizeDatamods(self, data, repack=True):  # Polemos
        """Sanitize DataDirs entries (openmw.cfg)."""
        filterPaths = self.filterDataMod(data)
        filterDups = self.itmDeDup(filterPaths)
        filterMissing = [x for x in filterDups if os.path.isdir(x)]
        return (
            ['data="%s"' % x.rstrip() for x in filterMissing]
            if repack
            else [x.rstrip() for x in filterMissing]
        )

    def SaveDatamods(self, rawdata):  # Polemos
        """Export DataDirs to openmw.cfg."""
        data = self.sanitizeDatamods(rawdata)
        reLoadFile = re.compile(r"data=(.*)$", re.UNICODE)
        datamodsMark = True
        DataMods_empty = True
        conf_tmp = []
        # Check for no entries
        for line in self.confLoadLines[:]:
            maLoadFile = reLoadFile.match(line)
            if maLoadFile:
                DataMods_empty = False
                if datamodsMark:
                    datamodsMark = False
                    conf_tmp.extend(data)
            else:
                conf_tmp.append(line.rstrip())
        # If no entries
        if DataMods_empty:
            if conf_tmp[-1] == "PluginMark" and data:
                del conf_tmp[-1]
                conf_tmp.extend(data)
                conf_tmp.append("PluginMark")
            else:
                conf_tmp.extend(data)
        # No DataMods dirs yet
        if conf_tmp and not self.DataMods:
            self.safeSave(
                "\n".join(
                    [
                        x
                        for x in conf_tmp
                        if not any(
                            ["PluginMark" in x, "ArchiveMark" in x, "data=" in x]
                        )
                    ]
                )
            )
        # self.StructureChk(datafiles_po) todo: check for cfg abnormalities...
        else:
            self.confLoadLines = conf_tmp
            self.DataModsDirs = self.filterDataMod(data)
            self.safeSave()

    def StructureChk(self, cfg):  # Polemos: Not enabled. todo: enable openmw.cfg check
        """Last check before saving OpenMW cfg file."""
        chkpoints = ""
        archive = False
        data = False
        content = False
        for x in cfg:
            if not archive:
                if x.startswith("fallback-archive="):
                    chkpoints = "%s1" % chkpoints
                    archive = True
            if not data:
                if x.startswith('data="'):
                    chkpoints = "%s2" % chkpoints
                    data = True
            if not content:
                if x.startswith("content="):
                    chkpoints = "%s3" % chkpoints
                    content = True
        if not chkpoints == "123":
            return False
        else:
            return True

    def FullRefresh(self):
        """For OpenMW/TES3mp."""
        folders = [x for x in self.openmw_data_files() if not os.path.isdir(x)]
        self.unloadDatamod(folders)

    def openmw_datamods(self):  # Polemos
        """Gets data entries from OpenMW.cfg file."""
        reLoadFile = re.compile(r"data=(.*)$", re.UNICODE)
        del self.DataMods[:]
        del self.ConfCache[:]
        for line in self.open_conf_file():
            maLoadFile = reLoadFile.match(line)
            if maLoadFile:
                line = line.rstrip().replace("&&", "&")
                self.DataMods.append(line)
            self.ConfCache.append(line)
        if not self.DataMods:
            return []
        return self.DataMods

    def openmw_data_files(self):  # Polemos
        """Return data file directories (OpenMW)."""
        if self.hasChanged():
            self.DataModsDirs = self.sanitizeDatamods(self.openmw_datamods()[:], False)
        return self.DataModsDirs

    def open_conf_file(self):  # Polemos
        """Return Morrowind.ini or OpenMW.cfg file."""
        try:
            with io.open(
                self.path, "r", encoding=self.encod, errors="strict"
            ) as conf_file:
                return conf_file.readlines()
        except ValueError:  # Override errors when changing encodings.
            with io.open(
                self.path, "r", encoding=self.encod, errors="ignore"
            ) as conf_file:
                return conf_file.readlines()

    def loadConf(self):  # Polemos
        """Redirect to read data from either morrowind.ini or OpenMW.cfg."""
        if not self.openmw:  # Morrowind
            self.load_Morrowind_INI()
        elif self.openmw:  # OpenMW/TES3mp
            self.load_OpenMW_cfg()

    def flush_conf(self, full=True):  # Polemos.
        """Flush old data."""
        if full:
            self.PluginSection = ""
            self.ArchiveSection = ""
            del self.confLoadLines[:]
            del self.loadFiles[:]
            del self.bsaFiles[:]
        self.loadFilesDups = False
        del self.loadFilesBad[:]
        del self.loadFilesExtra[:]

    def getExt(self, itmPath):
        """Return itm extension."""
        ext = os.path.splitext(itmPath)[-1].lower()
        self.activeFileExts.add(ext)
        return ext

    def chkCase(self, itms):  # Polemos
        """Check for duplicates and remove them if they are not in path. Fix case if unique."""
        if not any([itms is not None, not itms]):
            return itms  # Unforeseen events
        if not self.openmw:  # Morrowind
            origin = os.path.join(self.dir, "Data Files")
            inItms = {x.lower() for x in itms}
            if len(inItms) < len(itms):
                itmsR = [
                    x
                    for x in os.listdir(origin)
                    if [e for e in self.activeFileExts if x.lower().endswith(e)]
                ]
                self.loadFilesDups = True
                return list({x for x in itms if x in itmsR})
        elif self.openmw:  # OpenMW self.openmwPathDict
            inItms = {x.lower() for x in itms}
            if len(inItms) < len(itms):
                itmsR = [
                    x
                    for x in self.openmwPathDict
                    if x
                    in [
                        fileBasedLogger
                        for fileBasedLogger in os.listdir(
                            os.path.dirname(self.openmwPathDict[x])
                        )
                        if x.lower() == fileBasedLogger.lower()
                    ]
                ]
                self.loadFilesDups = True
                return list({x for x in itms if x in itmsR})
        return itms  # All OK

    def getSrcFilePathInfo(self, itm):  # Polemos
        """Acquire mod/plugin path info."""
        if not self.openmw:  # Morrowind
            modDir = [os.path.join(self.dir, "Data Files")]
        elif self.openmw:  # OpenMW
            modDir = self.DataModsDirs[:]
        for dr in modDir:
            itmPath = os.path.join(dr, itm)
            if os.path.isfile(itmPath):
                return itmPath
        return False

    def load_Morrowind_INI(self):  # Polemos.
        """Read Plugin and Archive data from morrowind.ini"""
        reLoadPluginSection = re.compile(r"^\[Game Files\](.*)", re.UNICODE)
        reLoadPluginFiles = re.compile(r"GameFile[0-9]+=(.*)$", re.UNICODE)
        reLoadArchiveSection = re.compile(r"^\[Archives\](.*)", re.UNICODE)
        reLoadArchiveFiles = re.compile(r"Archive [0-9]+=(.*)$", re.UNICODE)
        self.mtime = getmtime(self.path)
        self.size = os.path.getsize(self.path)
        self.flush_conf()
        PluginSection, ArchiveSection = False, False

        try:
            for line in self.open_conf_file():
                maLoadPluginSection = reLoadPluginSection.match(line)
                maLoadArchiveSection = reLoadArchiveSection.match(line)
                maLoadPluginFiles = reLoadPluginFiles.match(line)
                maLoadArchiveFiles = reLoadArchiveFiles.match(line)

                if maLoadArchiveSection:
                    ArchiveSection = True
                    self.ArchiveSection = line.rstrip()

                if maLoadPluginSection:
                    PluginSection = True
                    self.PluginSection = line.rstrip()

                if maLoadArchiveFiles:
                    archive = maLoadArchiveFiles.group(1).rstrip()
                    loadArchivePath, loadArchiveExt = self.getSrcFilePathInfo(
                        archive
                    ), self.getExt(archive)
                    if loadArchivePath and re.match("^\.bsa$", loadArchiveExt):
                        self.bsaFiles.append(archive)
                    else:
                        self.loadFilesBad.append(archive)

                if maLoadPluginFiles:
                    plugin = maLoadPluginFiles.group(1).rstrip()
                    loadPluginPath, loadPluginExt = self.getSrcFilePathInfo(
                        plugin
                    ), self.getExt(plugin)
                    if len(self.loadFiles) == self.maxPlugins:
                        self.loadFilesExtra.append(plugin)
                    elif loadPluginPath and re.match("^\.es[pm]$", loadPluginExt):
                        self.loadFiles.append(plugin)
                    else:
                        self.loadFilesBad.append(plugin)

                if not maLoadArchiveFiles and not maLoadPluginFiles:
                    self.confLoadLines.append(line.rstrip())
                if not line:
                    if not PluginSection:
                        raise Tes3Error(
                            "Morrowind.ini",
                            _("Morrowind.ini: [Game Files] section not found."),
                        )
                    if not ArchiveSection:
                        raise Tes3Error(
                            "Morrowind.ini",
                            _("Morrowind.ini: [Archives] section not found."),
                        )

            self.bsaFiles = self.chkCase(self.bsaFiles)
            self.loadFiles = self.chkCase(self.loadFiles)
        except (
            Exception
        ) as err:  # Last resort to avoid conf file corruption Todo: err expand
            self.flush_conf()
            traceback.print_exc()

    def load_OpenMW_cfg(self):  # Polemos
        """Read plugin data from openmw.cfg"""
        self.datafiles_po = self.openmw_data_files()
        reLoadArchiveFiles = re.compile(r"fallback-archive=(.*)$", re.UNICODE)
        reLoadPluginFiles = re.compile(r"content=(.*)$", re.UNICODE)
        self.mtime = getmtime(self.path)
        self.size = os.path.getsize(self.path)
        self.flush_conf()
        conf_tmp = []
        ArchivesMark = None
        PluginsMark = None
        Archives_empty = True
        Plugins_empty = True
        no_sound_mark = False

        try:
            for line in self.ConfCache[:]:  # Check for no entries
                maLoadArchiveFiles = reLoadArchiveFiles.match(line)
                maLoadPluginFiles = reLoadPluginFiles.match(line)
                if maLoadArchiveFiles:
                    Archives_empty = False
                if "no-sound=" in line:
                    no_sound_mark = True
                if maLoadPluginFiles:
                    Plugins_empty = False
                conf_tmp.append(line.rstrip())

            for line in conf_tmp:  # Parse OpenMW.cfg
                maLoadArchiveFiles = reLoadArchiveFiles.match(line)
                maLoadPluginFiles = reLoadPluginFiles.match(line)

                if maLoadArchiveFiles:  # Archives
                    if ArchivesMark is None:
                        ArchivesMark = True
                    archiveFile = maLoadArchiveFiles.group(1)
                    self.getExt(archiveFile)
                    archivePath = self.getSrcFilePathInfo(archiveFile)
                    if archivePath:
                        self.bsaFiles.append(archiveFile)
                        self.openmwPathDict[archiveFile] = archivePath
                    else:
                        self.loadFilesBad.append(archiveFile)

                if maLoadPluginFiles:  # Plugins
                    if PluginsMark is None:
                        PluginsMark = True
                    PluginFile = maLoadPluginFiles.group(1)
                    self.getExt(PluginFile)
                    PluginPath = self.getSrcFilePathInfo(PluginFile)
                    if PluginPath:
                        self.loadFiles.append(PluginFile)
                        self.openmwPathDict[PluginFile] = PluginPath
                    else:
                        self.loadFilesBad.append(PluginFile)

                if Archives_empty:  # If no Archive entries
                    if "no-sound=" in line:
                        self.confLoadLines.append(line)
                        line = "ArchiveMark"

                if ArchivesMark:  # Mark Archives pos in conf
                    ArchivesMark = False
                    self.confLoadLines.append("ArchiveMark")

                if PluginsMark:  # Mark Plugins pos in conf
                    PluginsMark = False
                    self.confLoadLines.append("PluginMark")

                if not maLoadArchiveFiles and not maLoadPluginFiles:
                    self.confLoadLines.append(line)

            if Plugins_empty:
                self.confLoadLines.append("PluginMark")  # If no Plugin entries
            if not no_sound_mark:
                self.confLoadLines.insert(0, "ArchiveMark")
            self.bsaFiles = self.chkCase(self.bsaFiles)
            self.loadFiles = self.chkCase(self.loadFiles)
        except (
            Exception
        ) as err:  # Last resort to avoid conf file corruption Todo: err expand
            self.flush_conf()
            traceback.print_exc()

    def get_active_bsa(self):  # Polemos
        """Called to return BSA entries from conf files."""
        if self.hasChanged():
            self.loadConf()
        return self.bsaFiles

    def data_files_factory(self, filenames):  # Polemos: OpenMW/TES3mp
        """Constructs the data file paths for OpenMW"""
        paths = self.DataModsDirs
        order_po = []
        real = os.path.realpath
        exists = os.path.exists
        join = os.path.join
        # Polemos: Having the folders first in the loop, counts for the DataMods folder order override.
        # Also, when searching for mods in a DataMods folder we cannot Break to speed things up. If we
        # do, we risk to omit DataMods with multiple plugins...
        for mod_dir in paths:
            for filename in filenames:
                fpath = real(join(mod_dir, filename))
                if exists(fpath):
                    order_po.append(fpath)
        return order_po

    def openmw_plugin_factory(self):  # Polemos: OpenMW/TES3mp
        """Prepare plugin file entries for insertion to OpenMW.cfg."""
        plugins_order_paths = self.data_files_factory(self.loadFiles)
        plugins_order_paths.sort(key=lambda x: os.path.getmtime(x))
        esm_order_active = [
            x
            for x in plugins_order_paths
            if x.lower().endswith(".esm") or x.lower().endswith(".omwgame")
        ]
        esp_order_active = [
            x
            for x in plugins_order_paths
            if x.lower().endswith(".esp") or x.lower().endswith(".omwaddon")
        ]
        plugins_order = esm_order_active + esp_order_active
        plugins_order_names_tmp = [os.path.basename(x) for x in plugins_order]
        plugins_order_fin = self.itmDeDup(plugins_order_names_tmp)
        return plugins_order_fin

    def openmw_archive_factory(self):  # Polemos: OpenMW/TES3mp
        """Prepare archive file entries for insertion to OpenMW.cfg."""
        archives_order = self.data_files_factory(self.bsaFiles)
        archives_order.sort(key=lambda x: os.path.getmtime(x))
        archives_order = [os.path.basename(x) for x in archives_order]
        archives_order = self.itmDeDup(archives_order)
        return [x for x in archives_order if x.lower().endswith(".bsa")]

    def saveS(self, simpleData):  # Polemos
        """Simple no rules storage."""
        with io.open(self.path, "w", encoding=self.encod, errors="strict") as conf_File:
            conf_File.write(simpleData)
        self.mtime = getmtime(self.path)

    def save(
        self,
    ):  # Polemos fixes, optimizations, OpenMW/TES3mp support, BSA support, speed up massive lists.
        """Prepare data to write to morrowind.ini or openmw.cfg file."""
        if not self.confLoadLines:
            self.flush_conf()
            msg = _(  # We need this dialog to be modeless to avoid file datetime corruption.
                "Unable to parse or modify %s. No changes can be made."
                "\n\nPlease try selecting a different encoding from the settings menu and restart Wrye Mash."
            ) % (
                "morrowind.ini" if not self.openmw else "openmw.cfg"
            )
            self.criticalMsg(msg, "error", False)
            raise StateError(msg)
        writeCache, failed = [], {}

        if self.hasChanged():  # Has the config file changed?
            if not self.openmw:
                error_ini_po = _("Morrowind.ini has changed externally! Aborting...")
            elif self.openmw:
                error_ini_po = _("Openmw.cfg has changed externally! Aborting...")
            raise StateError(error_ini_po)

        with io.open(self.path, "w", encoding=self.encod, errors="strict") as conf_File:
            if not self.openmw:  # Morrowind
                # Check for irregular file namings.
                if not settings["query.file.risk"]:
                    self.filesRisk = self.fileNamChk(self.loadFiles + self.bsaFiles)
                # Create output entries.
                for line in self.confLoadLines:
                    if line == self.ArchiveSection:
                        writeCache.append("%s" % self.ArchiveSection)
                        for aNum in xrange(len(self.bsaFiles)):
                            Archive = self.bsaFiles[aNum]
                            writeCache.append("Archive %d=%s" % (aNum, Archive))
                    elif line == self.PluginSection:
                        writeCache.append("%s" % self.PluginSection)
                        for pNum in xrange(len(self.loadFiles)):
                            Plugin = self.loadFiles[pNum]
                            writeCache.append("GameFile%d=%s" % (pNum, Plugin))
                    else:
                        writeCache.append("%s" % line)

            elif self.openmw:  # OpenMW/TES3mp
                # Call file factories.
                archives_order = self.openmw_archive_factory()
                plugins_order = self.openmw_plugin_factory()
                # Check for irregular file namings.
                if not settings["query.file.risk"]:
                    self.filesRisk = self.fileNamChk(archives_order + plugins_order)
                # Create output entries.
                for line in self.confLoadLines:
                    if "data=" in line:
                        line = line.replace("&", "&&")
                    if line == "ArchiveMark":
                        for Archive in archives_order:
                            writeCache.append("fallback-archive=%s" % Archive)
                    elif line == "PluginMark":
                        for Plugin in plugins_order:
                            writeCache.append("content=%s" % Plugin)
                    else:
                        writeCache.append("%s" % line)

            try:  # Try to join all and save once.
                tmpwriteCache = "\n".join(writeCache)
                conf_File.write(tmpwriteCache)
            except:  # On fail, save by line.
                for num, x in enumerate(writeCache):
                    x = "%s\n" % x
                    try:
                        conf_File.write(x)
                    except:
                        try:
                            conf_File.write(x.encode(encChk(x)))
                        except:
                            failed[num] = x.rstrip()

        self.mtime = getmtime(self.path)
        self.size = os.path.getsize(self.path)
        self.flush_conf(False)
        # Notify user for any errors.
        if failed:
            self.charFailed(failed)

    def fRisk(self):  # Polemos
        """Show filenames that may cause problems to the user."""
        if settings["query.file.risk"] or self.openmw:
            return  # Todo: Enable for OpenMW
        import gui.dialog as gui, wx

        engine = "Morrowind" if not self.openmw else "OpenMW"
        # Notify user
        tmessage = _("Some of your mod filenames seem to have problematic encodings.")
        message = (
            _(
                "There is a possibility that they might cause problems/bugs with Wrye Mash or %s functionality.\n"
                "Please consider renaming them.\n\nWould you like to see a list of the affected filenames?"
            )
            % engine
        )
        if (
            gui.ContinueQuery(
                None,
                tmessage,
                message,
                "query.file.risk",
                _("Problematic Filenames Detected"),
            )
            != wx.ID_OK
        ):
            return
        else:
            riskItms = "\n".join(self.filesRisk)
            gui.WarningMessage(
                None,
                _("The affected filenames are:\n\n%s" % riskItms),
                _("Affected Filenames List"),
            )
        del self.filesRisk[:]

    def fileNamChk(self, flist):
        """Check for irregular file namings."""
        probs = []
        for x in flist:
            try:
                x.decode(encChk(x))
            except:
                probs.append(x)
        return probs

    def charFailed(self, items):  # Polemos
        """Show failed entries to the user."""
        # Set data
        conf = "Morrowind.ini" if not self.openmw else "Openmw.cfg"
        confItms = (
            ("Archive", "GameFile")
            if not self.openmw
            else ("fallback-archive=", "content")
        )
        l = _("Line")
        # Extract mod errors
        mods = [
            ("%s %s: %s" % (l, x, items[x]))
            for x in items
            if any([y in items[x] for y in confItms])
        ]
        # Reload the config file
        self.loadConf()
        # If the errors are only for mod entries, skip them, keep the changes in the configuration file and notify user
        if len(items) == len(mods):
            errors = "\n".join(mods)
            self.criticalMsg(
                _(
                    "Problems encountered while updating %s. The following entries were not added:\n\n%s"
                    % (conf, errors)
                )
            )
        # If there are also errors on lines without mod entries, notify user and raise error to revert to backup
        if len(items) > len(mods):
            errors = "\n".join(
                [
                    (
                        ("%s %s: %s..." % (l, x, items[x][:35]))
                        if len(items[x]) > 35
                        else ("%s %s: %s" % (l, x, items[x]))
                    )
                    for x in items
                ]
            )
            self.criticalMsg(
                _(
                    "Problems encountered while updating %s. Will revert to backup, no changes will be saved:\n\n%s"
                    % (conf, errors)
                )
            )
            self.restoreBackup()

    def restoreBackup(self):  # Polemos: Good to have a safety switch.
        """Restores the latest morrowind.ini/openmw.cfg backup file on save failure."""
        # Does the last backup file exist?
        if os.path.isfile("%s.bak" % self.path):
            conf_bck = "%s.bak" % self.path
        # If missing, does the first backup ever taken exist?
        elif os.path.isfile("%s.baf" % self.path):
            conf_bck = "%s.baf" % self.path
        # Shit happens. Notify user and abort.
        else:
            return "Fatal: No backup file was found to restore configuration!"
        # Restore ops
        shutil.copy(conf_bck, self.path)
        self.loadConf()

    def makeBackup(self):
        """Create backup copy/copies of morrowind.ini/openmw.cfg file."""
        # --File Path
        original = self.path
        # --Backup
        backup = "%s.bak" % self.path
        shutil.copy(original, backup)
        # --First backup
        firstBackup = "%s.baf" % self.path
        if not os.path.exists(firstBackup):
            shutil.copy(original, firstBackup)

    def safeSave(self, simpleData=False):  # Polemos
        """Safe save conf file."""
        self.makeBackup()
        try:
            if not simpleData:
                self.save()
            else:
                self.saveS(simpleData)
        except ConfError as err:
            import gui.dialog as gui

            gui.ErrorMessage(None, err.message)
            self.restoreBackup()
        except Exception as err:
            self.restoreBackup()
        # If allowed, check filename risk
        if not self.skip and self.filesRisk:
            self.fRisk()
        self.skip = False  # Skip first check

    def hasChanged(self):
        """True if morrowind.ini/openmw.cfg file has changed."""
        return (self.mtime != getmtime(self.path)) or (
            self.size != os.path.getsize(self.path)
        )

    def refresh(self):
        """Load only if morrowind.ini/openmw.cfg has changed."""
        hasChanged = self.hasChanged()
        if hasChanged:
            self.loadConf()
        if self.maxPlugins is not None:
            if len(self.loadFiles) > self.maxPlugins:
                del self.loadFiles[self.maxPlugins :]
                self.safeSave()
        return hasChanged

    def refreshDoubleTime(self):
        """Refresh arrays that keep track of doubletime mods."""
        doubleTime = self.doubleTime
        doubleTime.clear()
        for loadFile in self.loadFiles:
            try:  # Polemos: Black magic here, move along.
                mtime = modInfos[loadFile].mtime
                doubleTime[mtime] = doubleTime.has_key(mtime)
            except:
                pass
        # --Refresh overLoaded too..
        exGroups = set()
        self.exOverLoaded.clear()
        for selFile in self.loadFiles:
            maExGroup = reExGroup.match(selFile)
            if maExGroup:
                exGroup = maExGroup.group(1)
                if exGroup not in exGroups:
                    exGroups.add(exGroup)
                else:
                    self.exOverLoaded.add(exGroup)

    def isWellOrdered(self, loadFile=None):
        if loadFile and loadFile not in self.loadFiles:
            return True
        # Yakoby: An attempt at a fix for issue #27.I am not sure why
        # this is now needed and wasn't before.One posibility is that
        # when modInfos gets manipulated this isn't refreshed.
        elif loadFile:
            mtime = modInfos[loadFile].mtime
            if mtime not in self.doubleTime:
                self.refreshDoubleTime()
            return not self.doubleTime[mtime]
        else:
            return not (True in self.doubleTime.values())

    def getDoubleTimeFiles(self):
        dtLoadFiles = []
        for loadFile in self.loadFiles:
            try:  # Polemos: It fails if restoring auto backup.
                if self.doubleTime[modInfos[loadFile].mtime]:
                    dtLoadFiles.append(loadFile)
            except:
                pass
        return dtLoadFiles

    def sortLoadFiles(self):
        """Sort load files into esm/esp, alphabetical order."""
        self.loadFiles.sort()
        self.loadFiles.sort(lambda a, b: cmp(a[-3:].lower(), b[-3:].lower()))

    def isMaxLoaded(self):
        """True if load list is full."""
        if self.maxPlugins is None:
            return False
        return len(self.loadFiles) >= self.maxPlugins

    def isLoaded(self, modFile):
        """True if modFile is in load list."""
        return modFile in self.loadFiles

    def load(self, Files, doSave=True, action="Plugins"):  # Polemos: Speed up
        """Add modFile/archive to load list."""
        if action == "Plugins":
            for x in Files:
                if x not in self.loadFiles:
                    if self.isMaxLoaded():
                        raise MaxLoadedError
                    self.loadFiles.append(x)
            if doSave:
                self.sortLoadFiles()
                self.safeSave()
            self.refreshDoubleTime()
            self.loadOrder = modInfos.getLoadOrder(self.loadFiles)
        elif action == "Archives":  # Polemos bsa support
            bsaSet = set(self.bsaFiles)
            self.bsaFiles.extend([x for x in Files if x not in bsaSet])
            self.safeSave()

    def unload(self, Files, doSave=True, action="Plugins"):  # Polemos: Speed up
        """Remove modFile/archive from load list."""
        if action == "Plugins":
            [self.loadFiles.remove(x) for x in Files if x in self.loadFiles]
            if doSave:
                self.safeSave()
            self.refreshDoubleTime()
            self.loadOrder = modInfos.getLoadOrder(self.loadFiles)
        if action == "Archives":  # Polemos bsa support
            [self.bsaFiles.remove(x) for x in Files]
            self.safeSave()


# ------------------------------------------------------------------------------


class MasterInfo:
    """Return info about masters."""

    def __init__(self, name, size):
        """Init."""
        self.oldName = self.name = name
        self.oldSize = self.size = size
        self.modInfo = modInfos.get(self.name, None)
        if self.modInfo:
            self.mtime = self.modInfo.mtime
            self.author = self.modInfo.tes3.hedr.author
            self.masterNames = self.modInfo.masterNames
        else:
            self.mtime = 0
            self.author = ""
            self.masterNames = tuple()
        self.isLoaded = True
        self.isNew = False  # --Master has been added

    def setName(self, name):
        self.name = name
        self.modInfo = modInfos.get(self.name, None)
        if self.modInfo:
            self.mtime = self.modInfo.mtime
            self.size = self.modInfo.size
            self.author = self.modInfo.tes3.hedr.author
            self.masterNames = self.modInfo.masterNames
        else:
            self.mtime = 0
            self.size = 0
            self.author = ""
            self.masterNames = tuple()

    def hasChanged(self):
        return (
            (self.name != self.oldName)
            or (self.size != self.oldSize)
            or (not self.isLoaded)
            or self.isNew
        )

    def isWellOrdered(self):
        if self.modInfo:
            return self.modInfo.isWellOrdered()
        else:
            return 1

    def getStatus(self):
        if not self.modInfo:
            return 30
        elif self.size != self.modInfo.size:
            return 10
        else:
            return 0

    def isExOverLoaded(self):
        """True if belongs to an exclusion group that is overloaded."""
        maExGroup = reExGroup.match(self.name)
        if not (mwIniFile.isLoaded(self.name) and maExGroup):
            return False
        else:
            return maExGroup.group(1) in mwIniFile.exOverLoaded

    def getObjectMap(self):
        """Object maps."""
        if self.name == self.oldName:
            return None
        else:
            return modInfos.getObjectMap(self.oldName, self.name)


utilsCommands = ("mish",)


class UtilsData(DataDict):  # Polemos: Many changes here.
    """UtilsData #-# D.C.-G for UtilsPanel extension."""

    def __init__(self):
        """Initialize."""
        self.dir = dirs["app"]
        self.data = {}
        self.badata = []
        if not os.path.isfile("utils.dcg"):
            self.rebuilt_config()

    def refresh(self):
        """Refresh list of utilities."""
        self.dir = dirs["app"]
        # -# Since there is only one utils file, its name is hardcoded.
        utilsFile = "utils.dcg"
        newData = {}
        if os.path.isfile(utilsFile) and os.access(utilsFile, os.R_OK):
            with io.open(utilsFile, "r", encoding="utf-8", errors="replace") as file:
                lines = file.readlines()
            for line in lines:
                line = line.rstrip()
                if not line.startswith(";") and line != "":
                    try:
                        ID, commandLine, arguments, description = line.split(";", 3)
                        newData[ID] = (commandLine, arguments, description.strip())
                        check = int(ID)
                    except:
                        continue
        changed = str(self.data) != str(newData)
        self.data = newData
        return changed

    def rebuilt_config(self):
        default_text = (
            "; utils.dcg\r\n"
            "; File containing the mash utils data\r\n"
            ";\r\n"
            "; Format of a Utility entry:\r\n"
            ";\r\n"
            "; ID of the utility; Filename; Parameters; Description of the utility; Name of the Utility\r\n\r\n"
        )
        with io.open("utils.dcg", "w", encoding="utf-8") as file:
            file.write(default_text)

    def delete(self, fileName):
        """Deletes member file."""
        filePath = self.dir.join(fileName)
        filePath.remove()
        del self.data[fileName]

    def save(self):  # Polemos: fixes
        """Writes the file on the disk."""
        utilsFile = "utils.dcg"
        orgData = {}
        self.badata = []
        if os.path.isfile(utilsFile) and os.access(utilsFile, os.R_OK):
            with io.open(utilsFile, "r", encoding="utf-8", errors="replace") as file:
                lines = file.readlines()
            lines = [line.rstrip() for line in lines]
            for line in lines:
                if not line.startswith(";") and line != "":
                    try:
                        ID, commandLine, arguments, description = line.split(";", 3)
                        orgData[ID] = (commandLine, arguments, description.strip())
                        check = int(ID)
                    except:
                        self.badata.append(line)
                        continue
        changed = str(self.data) != str(orgData)

        if changed:  # Items removed
            [
                lines.remove(line)
                for key in orgData.keys()
                if key not in self.data.keys()
                for line in lines
                if line.startswith(key)
            ]

            # Items added or modified
            for key, value in self.data.iteritems():
                if key not in orgData.keys():
                    try:
                        lines.append(
                            "%s;%s;%s;%s".encode("utf-8").decode("utf-8")
                            % ((key,) + value)
                        )
                    except:
                        lines.append("%s;%s;%s;%s".decode("utf-8") % ((key,) + value))
                elif key in orgData.keys():
                    for line in lines:
                        try:
                            if line.startswith(key):
                                idx = lines.index(line)
                                lines[idx] = "%s;%s;%s;%s" % ((key,) + value)
                        except:
                            pass
            with io.open(utilsFile, "w", encoding="utf-8", errors="replace") as file:
                lines = "\r\n".join([line for line in lines if line not in self.badata])
                try:
                    file.write(lines.encode("utf-8"))
                except:
                    file.write(lines)


# ------------------------------------------------------------------------------


class CommandsData:
    """Create Custom Commands."""

    def __init__(self, window):
        self.config_file_path = os.path.join(MashDir, "custom.dcg")
        import gui.dialog as gui

        self.gui = gui
        self.window = window
        self.data = {}

    def execute(self):
        self.load_commands()
        self.DoConfig()

    def Get(self):
        self.load_commands()
        return self.data

    def load_commands(self):
        if not os.path.isfile(self.config_file_path):
            self.save_commands(save_default=True)
        try:
            if os.path.isfile(self.config_file_path) and os.access(
                self.config_file_path, os.R_OK
            ):
                with io.open(
                    self.config_file_path, "r", encoding="utf-8", errors="replace"
                ) as file:
                    config_file = file.readlines()
                commands = {}
                for line in config_file:
                    line = line.strip()
                    if not line.startswith(";") and line != "":
                        try:
                            name = line.split(";")[0]
                            args = ";".join(line.split(";")[1:])
                            commands[name] = args
                        except:
                            pass
                self.data = commands
        except:
            pass  # self.gui.ErrorMessage(None, _(u'A problem has occurred while loading "custom.dcg" to import your custom commands.\n'))

    def save_commands(self, save_default=False):
        try:
            with io.open(
                self.config_file_path, "w", encoding="utf-8", errors="replace"
            ) as file:
                file.write(self.default_config_file())
                if not save_default:
                    for key, value in self.data.iteritems():
                        try:
                            file.write("%s;%s\n" % (key, value))
                        except:
                            pass
        except:
            pass  # self.gui.ErrorMessage(None, _(u'A problem has occurred while saving/creating "custom.dcg" to export your custom commands.\n'))

    def default_config_file(self):
        return (
            "; custom.dcg\n"
            "; File containing Custom Commands entries\n"
            ";\n"
            "; Format of a Custom Command entry:\n"
            ";\n"
            "; Name;Command parameters\n"
            "; Hint: use %target% variable to represent the position of file target(s) in your commands.\n\n"
        )

    def DoConfig(self):
        dialog = self.gui.ListDialog(self.window, _("Set Commands..."), dict(self.data))
        value = dialog.GetValue
        if value or value == {}:
            self.data = value
        else:
            return
        self.save_commands()


# ------------------------------------------------------------------------------


class ScreensData(DataDict):  # Polemos: added png support
    def __init__(self):
        """Initialize."""
        self.dir = dirs["app"]
        self.data = {}

    def refresh(self):
        """Refresh list of screenshots."""
        self.dir = dirs["app"]
        ssBase = GPath(
            mwIniFile.getSetting("General", "Screen Shot Base Name", "ScreenShot")
        )
        if ssBase.head:
            self.dir = self.dir.join(ssBase.head)
        newData = {}
        reImageExt = re.compile(r"\.(bmp|jpg|png)$", re.I)
        # --Loop over files in directory
        for fileName in self.dir.list():
            filePath = self.dir.join(fileName)
            maImageExt = reImageExt.search(fileName.s)
            if maImageExt and filePath.isfile():
                newData[fileName] = (
                    maImageExt.group(1).lower(),
                    filePath.mtime,
                    os.path.getsize(filePath._s),
                )  # Polemos: Added size attr.
        changed = self.data != newData
        self.data = newData
        return changed

    def delete(self, fileName):
        """Deletes member file."""
        filePath = self.dir.join(fileName)
        filePath.remove()
        del self.data[fileName]


# ------------------------------------------------------------------------------


class datamod_order:  # Polemos: OpenMW/TES3mp support
    """Create Datamods entries for OpenMW."""

    def __init__(self):
        """Initialize."""
        self.encod = settings["profile.encoding"]
        self.mwfiles = (
            settings["openmw.datafiles"]
            if os.path.isdir(settings["openmw.datafiles"])
            else None
        )
        self.conf_file = settings["openmwprofile"]
        self.mods = os.path.join(
            MashDir, "Profiles", settings["profile.active"], "mods.dat"
        )
        self.modsorder_path = os.path.join(
            MashDir, "Profiles", settings["profile.active"], "modsorder.dat"
        )
        self.order = []
        self.datafiles = []
        self.SetModOrder()

    def moveTo(self, mods):
        """Changes selected mod(s) order."""
        self.order = mods[:]
        self.create(self.mods, "\r\n".join((x for x in self.order)))
        self.RefreshProfile()

    def mopydir(self):
        """Check or create Mashdir."""
        self.mashdir = settings["mashdir"]
        if not os.path.isdir(self.mashdir):
            os.makedirs(self.mashdir)
            exists = False
        else:
            exists = True
        return exists

    def metainfo(self, mod):
        """Get data from mashmeta.inf file in mod directory."""
        data = {
            "Installer": "",
            "Version": "",
            "NoUpdateVer": "",
            "NewVersion": "",
            "Category": "",
            "Repo": "",
            "ID": "",
        }
        reList = re.compile(
            "(Installer|Version|NoUpdateVer|NewVersion|Category|Repo|ID)=(.+)"
        )
        # Special ModData
        if mod == self.mwfiles:
            data["Category"] = "Main Files"
            metadata = data
        elif mod == self.mashdir:
            data["Category"] = "Mash Files"
            metadata = data
        else:
            metadata = self.metaget(mod)[:]
        # Main
        for x in metadata:
            x = x.rstrip()
            maList = reList.match(x)
            if maList:
                key, value = maList.groups()
                if key == "Installer":
                    data[key] = value
                elif key == "Version":
                    data[key] = value
                elif key == "NoUpdateVer":
                    data[key] = value
                elif key == "NewVersion":
                    data[key] = value
                elif key == "Category":
                    data[key] = value
                elif key == "Repo":
                    data[key] = value
                elif key == "ID":
                    data[key] = value
        return data

    def metatext(self):  # Todo: add dialog for setting repos, url, etc ...
        """Default content for mashmeta.inf (mod dir)."""
        metatext = (
            "[General]",
            "Installer=",
            "Version=",
            "NoUpdateVer=",
            "NewVersion=",
            "Category=",
            "Repo=",
            "ID=",
        )
        return "\r\n".join(metatext)

    def metaget(self, mod):
        """Check if mashmeta.inf exist and create it if does not."""
        metafile = os.path.join(mod, "mashmeta.inf")
        if not os.path.isfile(metafile):
            self.create(metafile, self.metatext())
        return self.read(metafile)

    def RefreshProfile(self):
        """Get Data from user profile."""
        orderProfileDataMods = [
            dmod.rstrip()
            for dmod in self.read(self.mods)
            if os.path.isdir(dmod.rstrip())
        ]
        uniqProfileDataMods = list(set(orderProfileDataMods))
        self.ProfileDataMods = []
        for dmod in orderProfileDataMods:
            if dmod in uniqProfileDataMods:
                uniqProfileDataMods.remove(dmod)
                xfiles = os.path.dirname(dmod)
                for mulder in os.listdir(xfiles):
                    scully = os.path.join(xfiles, mulder)
                    if scully == dmod:
                        self.ProfileDataMods.append(dmod)
                        break
        if not self.check_mods_data():
            self.SetModOrder()

    def check_mods_data(self):
        """Checks for problems in mods.dat file."""
        return len(set(self.order)) == len(self.order)

    def mod_order(self):
        """Establish a New Mod Order Government (o)."""
        isdir = os.path.isdir
        if os.path.isfile(self.mods):
            self.order = [x.rstrip() for x in self.read(self.mods) if isdir(x.rstrip())]
            if not self.check_mods_data():
                self.order = []
            self.order.extend([x for x in self.datamods()[:] if x not in self.order])
            if all([self.mwfiles is not None, self.mwfiles not in self.order]):
                self.order.insert(0, self.mwfiles)
        self.create(self.mods, "\r\n".join((x for x in self.order)))

    def SetModOrder(self):
        """Init User Profile Data."""
        self.mod_order()
        self.RefreshProfile()

    def modflags(self, Version, NoUpdateVer, NewVersion, mod):
        """Assign mod flags."""
        flags = []
        moddir = settings["datamods"]
        if Version != NewVersion and NoUpdateVer != NewVersion:
            flags.append("(U)")
        if mod not in self.inmods:
            flags.append("!")
        if "!" in flags:  # Keep this.
            if moddir in mod:
                flags.remove("!")
        return flags if flags != [] else ""

    def get_mod_data(self):
        """Final mod data assembly and delivery."""
        self.RefreshProfile()
        result = {}
        basename = os.path.basename
        normpath = os.path.normpath
        chkActive = MWIniFile(self.conf_file).checkActiveState
        for num, mod in enumerate(self.ProfileDataMods):
            meta = self.metainfo(mod)
            Name = basename(normpath(mod))
            active_state = chkActive(mod)
            Version = meta["Version"]
            NoUpdateVer = meta["NoUpdateVer"]
            NewVersion = meta["NewVersion"]
            flags = self.modflags(Version, NoUpdateVer, NewVersion, mod)
            Category = meta["Category"]
            Inmods = True if mod in self.inmods else False
            data = [Name, num, flags, Version, Category, active_state, mod, Inmods]
            result[mod] = data
        return result

    def datamods(self):
        """Create Datamods data from openmw.cfg and Datamods dir."""
        # Init stuff
        isdir = os.path.isdir
        join = os.path.join
        # Openmw.cfg parsing
        self.datafiles = MWIniFile(settings["openmwprofile"]).openmw_data_files()[:]
        datafiles = self.datafiles[:]
        # DataMods dir parsing
        moddir = settings["datamods"]
        datamods = [join(moddir, dir) for dir in scandir.listdir(moddir)]
        # DataMods final list
        datafiles.extend((x for x in datamods if all([isdir(x), x not in datafiles])))
        if not self.mopydir():
            datafiles.append(self.mashdir)
        # Mods in DataMods Modified List
        self.inmods = datamods[:]
        self.inmods.append(self.mashdir)
        if self.mwfiles is not None:
            self.inmods.append(self.mwfiles)
        return datafiles

    def create(self, file, text=""):
        """Create a file and save text."""
        with io.open(file, "w", encoding=self.encod) as f:
            f.write(text)

    def read(self, file):
        """Read file contents from a file in a chosen dir."""
        with io.open(file, "r", encoding=self.encod) as f:
            return f.readlines()


# ------------------------------------------------------------------------------


class DataModsInfo(DataDict, datamod_order):  # Polemos: OpenMW/TES3mp support
    """Returns mod information."""

    data = {}

    def __init__(self):
        """Initialize."""
        datamod_order.__init__(self)

    def refresh(self):
        """Refresh list of Mods Directories."""
        newData = self.get_mod_data()
        changed = self.data != newData

        if settings["openmw"] and changed:
            self.data = {}

        # This is magic. Don't play with the dark arts. #
        for key, value in newData.iteritems():  #
            self.data[key] = value  #
        return changed


# ------------------------------------------------------------------------------


class BSA_order:  # Polemos
    """Create BSA entries."""

    def __init__(self):
        self.openmw = settings["openmw"]
        self.conf = self.get_conf_dir()
        self.dir = self.bsa_dir()

    def get_conf_dir(self):
        if not self.openmw:
            return dirs["app"].s  # Morrowind
        if self.openmw:
            return settings["openmwprofile"]  # OpenMW

    def bsa_dir(self):
        """Set the Data Files dir."""
        if not self.openmw:
            return dirs["mods"].s  # Morrowind
        if self.openmw:
            return MWIniFile(self.conf).openmw_data_files()  # OpenMW

    def bsa_files(self):
        """Return a list of bsa files."""
        if not self.openmw:
            bsas = [
                os.path.join(self.dir, bsafile)
                for bsafile in scandir.listdir(self.dir)
                if bsafile.endswith(".bsa")
            ]
        if self.openmw:
            bsas = []
            bsadir = self.bsa_dir()[:]
            # The comprehension below is faster (timed) than the loop it is based on,
            # even though we are using append() inside the comprehension (which defeats
            # the purpose)... Be my guest and change it.
            [
                [
                    bsas.append(os.path.join(moddir, bsafile))
                    for bsafile in scandir.listdir(moddir)
                    if bsafile.lower().endswith(".bsa")
                ]
                for moddir in bsadir
                if os.path.exists(moddir)
            ]
        return bsas

    def bsa_active(self):
        """Check which mods are active from conf files."""
        active = MWIniFile.get_active_bsa(MWIniFile(self.conf))
        return active

    def bsa_size(self, bsa):
        """Get file size, return empty if file is inaccessible."""
        try:
            return os.path.getsize(bsa) / 1024
        except:
            return ""

    def bsa_date(self, bsa):
        """Get file date, return empty if file is inaccessible."""
        try:
            return os.path.getmtime(bsa)
        except:
            return ""

    def get_bsa_data(self):
        """Final bsa info assembly and delivery."""
        bsa_files = self.bsa_files()[:]
        active = self.bsa_active()[:]
        result = {}
        for bsa_Path in bsa_files:
            Name = os.path.basename(bsa_Path)
            Active = True if Name in active else False
            Size = self.bsa_size(bsa_Path)
            Date = self.bsa_date(bsa_Path)
            entry = [Name, bsa_Path, Active, Size, Date]
            result[Name] = entry
        return result


# ------------------------------------------------------------------------------


class BSAdata(DataDict, BSA_order):  # Polemos
    """BSAdata factory."""

    data = {}

    def __init__(self):
        """Initialize."""
        BSA_order.__init__(self)
        self.refresh()

    def refresh(self):
        """Refresh list of BSAs."""
        newData = self.get_bsa_data()
        changed = self.data != newData

        if settings["openmw"] and changed:
            self.data = {}

        # This is magic. Don't play with the dark arts. #
        for key, value in newData.iteritems():  #
            self.data[key] = value  #
        return changed


# ------------------------------------------------------------------------------


class Packages_Factory:  # Polemos
    """Create Package entries."""

    def __init__(self):
        self.dir = settings["downloads"]

    def package_files(self):
        """Return a list of package files."""
        packages = [
            os.path.join(self.dir, package)
            for package in scandir.listdir(self.dir)
            if package.endswith((".zip", "rar", "7z"))
        ]
        return packages

    def package_installed(self, package):  # Polemos, todo: maybe implement...
        """Check which packages are installed from metafiles."""
        return False  # os.path.isfile('%s.meta' % package)

    def package_size(self, file):
        """Get file size, return empty if file is inaccessible."""
        try:
            return os.path.getsize(file)
        except:
            return ""

    def get_package_data(self):
        """Final package info assembly and delivery."""
        package_files = self.package_files()[:]
        result = {}
        for package in package_files:
            Name = os.path.basename(package)
            Installed = True if self.package_installed(package) else False
            Size = self.package_size(package)
            entry = [Name, package, Installed, Size]
            result[Name] = entry
        return result


# ------------------------------------------------------------------------------


class PackagesData(DataDict, Packages_Factory):  # Polemos
    """PackageData factory."""

    data = {}

    def __init__(self):
        """Initialize."""
        Packages_Factory.__init__(self)
        self.refresh()

    def refresh(self):
        """Refresh list of BSAs."""
        newData = self.get_package_data()
        changed = self.data != newData

        if changed:
            self.data = {}

        # This is magic. Don't play with the dark arts. #
        for key, value in newData.iteritems():  #
            self.data[key] = value  #
        return changed


# -----------------------------------------------------------------------------


class GetBckList:  # Polemos
    """Formulate backup files list."""

    bckList = []

    def __init__(self, fname=False):
        """Init."""
        self.bckList = []
        self.max = settings["backup.slots"]
        self.snapdir = os.path.join(MashDir, "snapshots")
        self.bckfiles = [
            os.path.join(self.snapdir, "%s%s.txt" % (fname, x)) for x in range(self.max)
        ]
        self.listFactory()

    def dtFactory(self, DateTime):
        """Date/Time Factory."""
        return time.strftime("%m/%d/%Y - %H:%M:%S", time.localtime(DateTime))

    def listFactory(self):
        """List Factory."""
        for num, bckfile in enumerate(self.bckfiles):
            if os.path.isfile(bckfile):
                timestamp = os.path.getmtime(bckfile)
                self.bckList.append(
                    _("%s. Backup dated: %s" % (num, self.dtFactory(timestamp)))
                )


# -----------------------------------------------------------------------------


class LoadModOrder:  # Polemos
    """Restore Datamods order and status."""

    modData = []

    def __init__(self, num, fname):
        """Init."""
        self.mode = fname
        self.encod = settings["profile.encoding"]
        bckfile = os.path.join(MashDir, "snapshots", "%s%s.txt" % (fname, num))
        self.parseBck(bckfile)

    def dataFactory(self, rawData):
        """Restore data from container."""
        if self.mode == "modsnap":
            self.modData = [x.rstrip().split('"') for x in rawData]
            for num, x in enumerate(self.modData):
                self.modData[num][0] = True if self.modData[num][0] == "True" else False
        elif self.mode == "datasnap":
            self.modData = [line.rstrip() for line in rawData]
            self.modData = filter(
                None, self.modData
            )  # Polemos: This may have problems in Python 3
        elif self.mode == "paksnap":
            self.modData = [
                (int(x[0]), GPath(x[1].replace('"', "")), int(x[2]))
                for x in [y.split(":") for y in rawData]
            ]

    def parseBck(self, bckFile):
        """Save backup file."""
        with io.open(bckFile, "r", encoding=self.encod) as bck:
            self.dataFactory(bck.readlines())


# -----------------------------------------------------------------------------


class SaveModOrder:  # Polemos
    """Backup of items order and status."""

    status = False

    def __init__(self, modData, mode, fname):
        """Init."""
        self.encod = settings["profile.encoding"]
        self.mode = mode
        self.modData = modData
        self.max = settings["backup.slots"]
        self.snapdir = os.path.join(MashDir, "snapshots")
        self.bckfiles = [
            os.path.join(self.snapdir, "%s%s.txt" % (fname, x)) for x in range(self.max)
        ]
        if not os.path.isdir(self.snapdir):
            try:
                os.makedirs(self.snapdir)
            except IOError:
                return  # todo: add access denied error
            except:
                return
        self.initbck()

    def initbck(self):
        """Init backup actions."""
        # If only one slot
        if self.max == 1:
            self.saveBck(self.bckfiles[0])
            return
        # Save to first available slot
        for bckFile in self.bckfiles:
            if not os.path.isfile(bckFile):
                self.saveBck(bckFile)
                return
        # If all slots are filled, rotate
        os.remove(self.bckfiles[(self.max - 1)])
        ids = range(self.max)
        ids.reverse()
        for item in ids:
            if item - 1 == -1:
                break
            os.rename(self.bckfiles[item - 1], self.bckfiles[item])
        try:
            self.saveBck(self.bckfiles[0])
        except IOError:
            return  # todo: add access denied error

    def saveBck(self, bckFile):
        """Save backup file."""
        with io.open(bckFile, "w", encoding=self.encod) as bck:
            if self.mode == "mods":
                for x in ['%s"%s\n' % (x[5], x[6]) for x in self.modData]:
                    bck.write(x)
            elif self.mode == "plugins":
                try:
                    bck.write(self.modData.decode(self.encod))
                except:
                    pass  # todo: add fail error
            elif self.mode == "installers":
                for x in self.modData:
                    try:
                        bck.write('%s:"%s":%s\n' % (x[0], x[1], x[2]))
                    except:
                        pass  # todo: add fail error
        self.status = True


# -----------------------------------------------------------------------------


class CopyTree:  # Polemos
    """File tree copy (generic)."""

    accessErr = False

    def __init__(self, parent, source_dir, target_dir):
        """Init."""
        self.parent = parent
        self.source_dir = source_dir
        self.target_dir = target_dir
        if self.chkTarg():
            return
        self.filesLen = self.cntItms()
        self.title = (
            "Overwriting..." if os.path.isdir(self.target_dir) else "Copying..."
        )
        self.copyAct()

    def chkTarg(self):
        """Check if copying to itself."""
        result = self.source_dir == self.target_dir
        if result:
            import gui.dialog as gui

            gui.ErrorMessage(
                self.parent,
                _("Operation aborted: Thou shall not copy a directory unto itself..."),
            )
        return result

    def copyAct(self):
        """Thread Copy Tree."""
        import wx
        import gui.dialog as gui

        self.dialog = gui.GaugeDialog(
            self.parent, self.target_dir, self.title, self.filesLen
        )
        self.dialog.Show()
        thrTreeOp = Thread(target=self.treeOp)
        thrTreeOp.start()
        with wx.WindowDisabler():
            while thrTreeOp.isAlive():
                wx.GetApp().Yield()
        if self.accessErr:
            gui.ErrorMessage(
                self.parent,
                _(
                    "Operation failed: Access denied. Unable to write on the destination."
                ),
            )

    def cntItms(self):
        """Count directory contents for progress status."""
        itms = 0
        for root, dirsn, files in os.walk(self.source_dir):
            itms += len(
                files
            )  # We will use only the len of files for the progress status
        return itms

    def treeOp(
        self,
    ):  # Polemos: This is a very fast implementation. Todo: post it on stackoverflow?
        """Filetree operations."""
        source_dir = self.source_dir
        target_dir = self.target_dir
        if not os.path.isdir(self.target_dir):
            os.makedirs(self.target_dir)
        # Commence
        try:
            cnt = 0
            for root, dirsn, files in scandir.walk(source_dir, topdown=False):
                for status, fname in enumerate(files, 1):
                    if self.filesLen < 41:
                        self.dialog.update(status)
                    else:
                        cnt += 1
                        if cnt >= 10:
                            self.dialog.update(status)
                            cnt = 0
                    relsource = os.path.relpath(root, source_dir)
                    if relsource == ".":
                        relsource = ""
                    source = os.path.join(root, fname)
                    target = os.path.join(target_dir, relsource, fname)
                    target_file_dir = os.path.join(target_dir, relsource)
                    if not os.path.isdir(target_file_dir):
                        os.makedirs(target_file_dir)
                    buffer = min(10485760, os.path.getsize(source))
                    if buffer == 0:
                        buffer = 1024
                    with open(source, "rb") as fsource:
                        with open(target, "wb") as fdest:
                            shutil.copyfileobj(fsource, fdest, buffer)
        except IOError:
            self.accessErr = True
        finally:
            self.dialog.update(self.filesLen)
            self.dialog.set_msg(_("Finished..."))
            time.sleep(2)  # Give some time for system file caching.
            self.dialog.Destroy()


class ResetTempDir:  # Polemos
    """Reset/clear Mash Temp dir."""

    try:
        tempdir = os.path.join(MashDir, "Temp")
    except:
        tempdir = os.path.join(MashDir, "Temp")
    status = True

    def __init__(self, window):
        """Init."""
        import gui.dialog

        wait = gui.dialog.WaitDialog(window, _("Please wait, cleaning temp folder..."))
        if os.path.isdir(self.tempdir):
            if not self.safe(self.tempdir):  # Polemos: todo: Add GUI to inform user.
                self.status = False
                return
            bolt.RemoveTree(self.tempdir)
        self.RecreateTempdir()
        wait.exit()

    def safe(self, tempdir):
        """Ensure Temp is Mash Temp."""
        if tempdir == os.path.abspath(os.sep):
            return False
        if [
            x
            for x in scandir.listdir(tempdir)
            if x in ["7z.exe", "mash.exe", "mash.py"]
        ]:
            return False
        return True

    def RecreateTempdir(self):
        """Recreate tempdir."""
        try:
            if not os.path.isdir(self.tempdir):
                os.mkdir(self.tempdir)
        except:
            pass


# Installers ------------------------------------------------------------------


class Installer(
    object
):  # Polemos: added MWSE compatibility, optimised, bug fixing, restored lost Bain func on many packages.
    """Object representing an installer archive, its user configuration, and its installation state."""

    # --Member data
    persistent = (
        "archive",
        "order",
        "group",
        "modified",
        "size",
        "crc",
        "fileSizeCrcs",
        "type",
        "isActive",
        "subNames",
        "subActives",
        "dirty_sizeCrc",
        "comments",
        "readMe",
        "packageDoc",
        "packagePic",
        "src_sizeCrcDate",
        "hasExtraData",
        "skipVoices",
        "espmNots",
    )
    volatile = (
        "data_sizeCrc",
        "skipExtFiles",
        "skipDirFiles",
        "status",
        "missingFiles",
        "mismatchedFiles",
        "refreshed",
        "mismatchedEspms",
        "unSize",
        "espms",
        "underrides",
    )
    __slots__ = persistent + volatile
    # --Package analysis/porting.
    docDirs = {"screenshots", "docs"}
    dataDirs = {
        "bookart",
        "fonts",
        "icons",
        "meshes",
        "music",
        "shaders",
        "sound",
        "splash",
        "textures",
        "video",
        "mash plus",
        "mits",
        "mwse",
        "animation",
    }
    dataDirsPlus = dataDirs | set()
    dataDirsMinus = {
        "mash",
        "replacers",
        "distantland",
        "clean",
    }  # --Will be skipped even if hasExtraData == True.
    reDataFile = re.compile(r"\.(esp|esm|bsa)$", re.I)
    reReadMe = re.compile(
        r"^([^\\]*)(dontreadme|read[ _]?me|lisez[ _]?moi)([^\\]*)\.(txt|rtf|htm|html|doc|odt)$",
        re.I,
    )
    skipExts = {".dll", ".dlx", ".exe", ".py", ".pyc", ".7z", ".zip", ".rar", ".db"}
    docExts = {
        ".txt",
        ".rtf",
        ".htm",
        ".html",
        ".doc",
        ".odt",
        ".jpg",
        ".png",
        ".pdf",
        ".css",
        ".xls",
    }
    # --Temp Files/Dirs
    tempDir = GPath("Temp")
    tempList = GPath("TempList.txt")
    # --Aliases
    off_local = {}

    # --Class Methods ----------------------------------------------------------
    @staticmethod
    def getGhosted():
        """Returns map of real to ghosted files in mods directory."""
        dataDir = dirs["mods"]
        ghosts = [x for x in dataDir.list() if x.cs[-6:] == ".ghost"]
        return {x.root: x for x in ghosts if not dataDir.join(x).root.exists()}

    @staticmethod
    def clearTemp():
        """Clear temp install directory -- DO NOT SCREW THIS UP!!!"""
        Installer.tempDir.rmtree(safety="Temp")

    @staticmethod
    def sortFiles(files):
        """Utility function. Sorts files by directory, then file name."""

        def sortKey(file):
            dirFile = file.lower().rsplit("\\", 1)
            if len(dirFile) == 1:
                dirFile.insert(0, "")
            return dirFile

        sortKeys = {x: sortKey(x) for x in files}
        return sorted(files, key=lambda x: sortKeys[x])

    @staticmethod
    def refreshSizeCrcDate(
        apRoot, old_sizeCrcDate, progress=None, removeEmpties=False, fullRefresh=False
    ):  # Polemos: fixed crc bug, +speed, more.
        """Update old_sizeCrcDate for root directory. This is used both by InstallerProject's and by InstallersData."""
        progress_info = settings["mash.installers.show.progress.info"]
        rootIsMods = apRoot == dirs["mods"]  # --Filtered scanning for mods directory.
        norm_ghost = (rootIsMods and Installer.getGhosted()) or {}
        ghost_norm = {y: x for x, y in norm_ghost.iteritems()}
        rootName = apRoot.stail
        progress = progress or bolt.Progress()
        new_sizeCrcDate = {}
        bethFiles = mush.bethDataFiles
        skipExts = Installer.skipExts
        asRoot = apRoot.s
        relPos = len(apRoot.s) + 1
        pending = set()
        # --Scan for changed files
        progress(0, _("%s: Pre-Scanning...\n ") % rootName)
        progress.setFull(1)
        dirDirsFiles = []
        emptyDirs = set()
        for asDir, sDirs, sFiles in scandir.walk(
            asRoot
        ):  # Polemos: replaced os.walk which is slow in Python 2.7 and below.
            progress(0.05, _("%s: Pre-Scanning:\n%s") % (rootName, asDir[relPos:]))
            if rootIsMods and asDir == asRoot:
                sDirs[:] = [
                    x for x in sDirs if x.lower() not in Installer.dataDirsMinus
                ]
            dirDirsFiles.append((asDir, sDirs, sFiles))
            if not (sDirs or sFiles):
                emptyDirs.add(GPath(asDir))
        progress(0, _("%s: Scanning...\n ") % rootName)
        progress.setFull(1 + len(dirDirsFiles))
        for index, (asDir, sDirs, sFiles) in enumerate(dirDirsFiles):
            progress(index)
            rsDir = asDir[relPos:]
            inModsRoot = rootIsMods and not rsDir
            apDir = GPath(asDir)
            rpDir = GPath(rsDir)
            for sFile in sFiles:
                ext = sFile[sFile.rfind(".") :].lower()
                rpFile = rpDir.join(sFile)
                if inModsRoot:
                    if ext in skipExts:
                        continue
                    if not rsDir and sFile.lower() in bethFiles:
                        continue
                    rpFile = ghost_norm.get(rpFile, rpFile)
                isEspm = not rsDir and (ext == ".esp" or ext == ".esm")
                apFile = apDir.join(sFile)
                size = apFile.size
                date = apFile.mtime
                oSize, oCrc, oDate = old_sizeCrcDate.get(rpFile, (0, 0, 0))
                if size == oSize and (date == oDate or isEspm):
                    new_sizeCrcDate[rpFile] = (oSize, oCrc, oDate)
                else:
                    pending.add(rpFile)
        # --Remove empty dirs?
        if settings["mash.installers.removeEmptyDirs"]:
            for dir in emptyDirs:
                try:
                    dir.removedirs()
                except OSError:
                    pass
        # --Force update?
        if fullRefresh:
            pending |= set(new_sizeCrcDate)
        changed = bool(pending) or (len(new_sizeCrcDate) != len(old_sizeCrcDate))
        # --Update crcs?
        if pending:
            progress(0, _("%s: Calculating CRCs...\n ") % rootName)
            progress.setFull(3 + len(pending))
            numndex = 0
            for index, rpFile in enumerate(
                sorted(pending)
            ):  # Polemos: Bugfix and also added some extra info...
                if progress_info:
                    try:
                        string = _(
                            "%s: Calculating CRCs...\n%s\nCRC: %s\nSize:  %sKB"
                        ) % (
                            rootName,
                            unicode(rpFile.s, sys.getfilesystemencoding()),
                            apFile.crc,
                            (apFile.size / 1024),
                        )
                    except:
                        string = _(
                            "%s: Calculating CRCs...\n%s\nCRC:  %s\nSize:  %sKB"
                        ) % (rootName, rpFile.s, apFile.crc, (apFile.size / 1024))
                if progress_info:
                    progress(index, string)
                # Polemos: Progress dialogs crawl if they have to show many items continuously. The same seems to
                # also happen on native windows progress dialogs (if you wonder why the "show more" is not ON by
                # default) and it is the main reason, in my opinion, of the extreme slowness in Windows 10 progress
                # dialogs. We mitigate this here by updating the progress dialog by steps of 10 until reaching the
                # final 9 items which are shown by steps of 1.
                elif numndex == 10:
                    progress(index)
                numndex = numndex + 1 if numndex < 10 else 0
                apFile = apRoot.join(norm_ghost.get(rpFile, rpFile))
                crc = apFile.crc
                size = apFile.size
                date = apFile.mtime
                new_sizeCrcDate[rpFile] = (size, crc, date)
        old_sizeCrcDate.clear()
        old_sizeCrcDate.update(new_sizeCrcDate)
        # --Done
        return changed

    # --Initization, etc -------------------------------------------------------
    def initDefault(self):
        """Inits everything to default values."""
        # --Package Only
        self.archive = ""
        self.modified = 0  # --Modified date
        self.size = 0  # --size of archive file
        self.crc = 0  # --crc of archive
        self.type = 0  # --Package type: 0: unset/invalid; 1: simple; 2: complex
        self.fileSizeCrcs = []
        self.subNames = []
        self.src_sizeCrcDate = {}  # --For InstallerProject's
        # --Dirty Update
        self.dirty_sizeCrc = {}
        # --Mixed
        self.subActives = []
        # --User Only
        self.skipVoices = False
        self.hasExtraData = False
        self.comments = ""
        self.group = ""  # --Default from abstract. Else set by user.
        self.order = -1  # --Set by user/interface.
        self.isActive = False
        self.espmNots = (
            set()
        )  # --Lowercase esp/m file names that user has decided not to install.
        # --Volatiles (unpickled values)
        # --Volatiles: directory specific
        self.refreshed = False
        # --Volatile: set by refreshDataSizeCrc
        self.readMe = self.packageDoc = self.packagePic = None
        self.data_sizeCrc = {}
        self.skipExtFiles = set()
        self.skipDirFiles = set()
        self.espms = set()
        self.unSize = 0
        # --Volatile: set by refreshStatus
        self.status = 0
        self.underrides = set()
        self.missingFiles = set()
        self.mismatchedFiles = set()
        self.mismatchedEspms = set()

    def __init__(self, archive):
        """Initialize."""
        self.initDefault()
        self.archive = archive.stail

    def __getstate__(self):
        """Used by pickler to save object state."""
        getter = object.__getattribute__
        return tuple(getter(self, x) for x in self.persistent)

    def __setstate__(self, values):
        """Used by unpickler to recreate object."""
        self.initDefault()
        setter = object.__setattr__
        for value, attr in zip(values, self.persistent):
            setter(self, attr, value)
        if self.dirty_sizeCrc is None:
            self.dirty_sizeCrc = {}  # --Use empty dict instead.
        self.refreshDataSizeCrc()

    def __copy__(self, iClass=None):
        """Create a copy of self -- works for subclasses too (assuming subclasses
        don't add new data members). iClass argument is to support Installers.updateDictFile
        """
        iClass = iClass or self.__class__
        clone = iClass(GPath(self.archive))
        copier = copy.copy
        getter = object.__getattribute__
        setter = object.__setattr__
        for attr in Installer.__slots__:
            setter(clone, attr, copier(getter(self, attr)))
        return clone

    def refreshDataSizeCrc(self):
        """Updates self.data_sizeCr and related variables. Also, returns dest_src map for install operation."""
        if isinstance(self, InstallerArchive):
            archiveRoot = GPath(self.archive).sroot
        else:
            archiveRoot = self.archive
        reReadMe = self.reReadMe
        docExts = self.docExts
        docDirs = self.docDirs
        dataDirsPlus = self.dataDirsPlus
        dataDirsMinus = self.dataDirsMinus
        skipExts = self.skipExts
        bethFiles = mush.bethDataFiles
        packageFiles = {"package.txt", "package.jpg"}
        unSize = 0
        espmNots = self.espmNots
        skipVoices = self.skipVoices
        off_local = self.off_local
        if espmNots and not skipVoices:
            skipEspmVoices = {x.cs for x in espmNots}
        else:
            skipEspmVoices = None
        skipDistantLOD = settings["mash.installers.skipDistantLOD"]
        hasExtraData = self.hasExtraData
        type = self.type
        if type == 2:
            allSubs = set(self.subNames[1:])
            activeSubs = {
                x for x, y in zip(self.subNames[1:], self.subActives[1:]) if y
            }
        # --Init to empty
        self.readMe = self.packageDoc = self.packagePic = None
        for attr in ("skipExtFiles", "skipDirFiles", "espms"):
            object.__getattribute__(self, attr).clear()
        data_sizeCrc = {}
        skipExtFiles = self.skipExtFiles
        skipDirFiles = self.skipDirFiles
        espms = self.espms
        dest_src = {}
        # --Bad archive?
        if type not in (1, 2):
            return dest_src
        # --Scan over fileSizeCrcs
        for full, size, crc in self.fileSizeCrcs:
            file = full  # --Default
            if type == 2:  # --Complex archive
                subFile = full.split("\\", 1)
                if len(subFile) == 2:
                    sub, file = subFile
                    if sub not in activeSubs:
                        if sub not in allSubs:
                            skipDirFiles.add(file)
                        continue
            rootPos = file.find("\\")
            extPos = file.rfind(".")
            fileLower = file.lower()
            # Polemos: The rootlower defines dirs in the root of the "selected
            # to be installed". This doesn't necessarily mean the package root.
            rootLower = (rootPos > 0 and fileLower[:rootPos]) or ""
            fileExt = (extPos > 0 and fileLower[extPos:]) or ""
            # --Skip file?
            if (
                rootLower == "omod conversion data"
                or fileLower[-9:] == "thumbs.db"
                or fileLower[-11:] == "desktop.ini"
            ):
                continue  # --Silent skip
            elif skipDistantLOD and fileLower[:10] == "distantlod":
                continue
            elif skipVoices and fileLower[:11] == "sound\\voice":
                continue
            elif file in bethFiles:
                skipDirFiles.add(full)
                continue
            # Polemos: fix for installing "Docs" sub-folders, without breaking bain install packages.
            elif (
                not hasExtraData
                and rootLower
                and rootLower not in dataDirsPlus
                and rootLower not in docDirs
            ):
                skipDirFiles.add(full)
                continue
            elif hasExtraData and rootLower and rootLower in dataDirsMinus:
                skipDirFiles.add(full)
                continue
            elif fileExt in skipExts:
                skipExtFiles.add(full)
                continue
            # --Remap (and/or skip)
            dest = file  # --Default. May be remapped below.
            # --Esps
            if not rootLower and reModExt.match(fileExt):
                pFile = pDest = GPath(file)
                if pFile in off_local:
                    pDest = off_local[pFile]
                    dest = pDest.s
                espms.add(pDest)
                if pDest in espmNots:
                    continue
            # --Esp related voices (Oblivion?)
            elif skipEspmVoices and fileLower[:12] == "sound\\voice\\":
                farPos = file.find("\\", 12)
                if farPos > 12 and fileLower[12:farPos] in skipEspmVoices:
                    continue
            # --Docs
            elif rootLower in docDirs:
                dest = "Docs\\" + file[rootPos + 1 :]
            elif not rootLower:
                maReadMe = reReadMe.match(file)
                if file.lower() == "masterlist.txt":
                    pass
                elif maReadMe:
                    if not (maReadMe.group(1) or maReadMe.group(3)):
                        dest = "Docs\\%s%s" % (archiveRoot, fileExt)
                    else:
                        dest = "Docs\\" + file
                    self.readMe = dest
                elif fileLower == "package.txt":
                    dest = self.packageDoc = "Docs\\" + archiveRoot + ".package.txt"
                elif fileLower == "package.jpg":
                    dest = self.packagePic = "Docs\\" + archiveRoot + ".package.jpg"
                elif fileExt in docExts:
                    dest = "Docs\\" + file
            # --Save
            key = GPath(dest)
            data_sizeCrc[key] = (size, crc)
            dest_src[key] = full
            unSize += size
        self.unSize = unSize
        (self.data_sizeCrc, old_sizeCrc) = (data_sizeCrc, self.data_sizeCrc)
        # --Update dirty?
        if self.isActive and data_sizeCrc != old_sizeCrc:
            dirty_sizeCrc = self.dirty_sizeCrc
            for file, sizeCrc in old_sizeCrc.iteritems():
                if file not in dirty_sizeCrc and sizeCrc != data_sizeCrc.get(file):
                    dirty_sizeCrc[file] = sizeCrc
        # --Done (return dest_src for install operation)
        return dest_src

    def refreshSource(self, archive, progress=None, fullRefresh=False):
        """Refreshes fileSizeCrcs, size, date and modified from source archive/directory."""
        raise AbstractError

    def refreshBasic(self, archive, progress=None, fullRefresh=False):
        """Extract file/size/crc info from archive."""
        self.refreshSource(archive, progress, fullRefresh)

        def fscSortKey(fsc):
            dirFile = fsc[0].lower().rsplit("\\", 1)
            if len(dirFile) == 1:
                dirFile.insert(0, "")
            return dirFile

        fileSizeCrcs = self.fileSizeCrcs
        sortKeys = {x: fscSortKey(x) for x in fileSizeCrcs}
        fileSizeCrcs.sort(key=lambda x: sortKeys[x])
        # --Type, subNames
        reDataFile = self.reDataFile
        dataDirs = self.dataDirs
        type = 0
        subNameSet = set()
        subNameSet.add("")
        for file, size, crc in fileSizeCrcs:
            fileLower = file.lower()
            if type != 1:
                frags = file.split("\\")
                nfrags = len(frags)
                # --Type 1?
                if (
                    nfrags == 1
                    and reDataFile.search(frags[0])
                    or nfrags > 1
                    and frags[0].lower() in dataDirs
                ):
                    type = 1
                    break
                # --Type 2?
                elif nfrags > 2 and frags[1].lower() in dataDirs:
                    subNameSet.add(frags[0])
                    type = 2
                elif nfrags == 2 and reDataFile.search(frags[1]):
                    subNameSet.add(frags[0])
                    type = 2
        self.type = type
        # --SubNames, SubActives
        if type == 2:
            actives = {
                x for x, y in zip(self.subNames, self.subActives) if (y or x == "")
            }
            self.subNames = sorted(subNameSet, key=string.lower)
            if (
                len(self.subNames) == 2
            ):  # --If only one subinstall, then make it active.
                self.subActives = [True, True]
            else:
                self.subActives = [(x in actives) for x in self.subNames]
        else:
            self.subNames = []
            self.subActives = []
        # --Data Size Crc
        self.refreshDataSizeCrc()

    def refreshStatus(self, installers):
        """Updates missingFiles, mismatchedFiles and status.
        Status:
        20: installed (green)
        10: mismatches (yellow)
        0: unconfigured (white)
        -10: missing files (red)
        -20: bad type (grey)
        """
        data_sizeCrc = self.data_sizeCrc
        data_sizeCrcDate = installers.data_sizeCrcDate
        abnorm_sizeCrc = installers.abnorm_sizeCrc
        missing = self.missingFiles
        mismatched = self.mismatchedFiles
        misEspmed = self.mismatchedEspms
        underrides = set()
        status = 0
        missing.clear()
        mismatched.clear()
        misEspmed.clear()
        if self.type == 0:
            status = -20
        elif data_sizeCrc:
            for file, sizeCrc in data_sizeCrc.iteritems():
                sizeCrcDate = data_sizeCrcDate.get(file)
                if not sizeCrcDate:
                    missing.add(file)
                elif sizeCrc != sizeCrcDate[:2]:
                    mismatched.add(file)
                    if not file.shead and reModExt.search(file.s):
                        misEspmed.add(file)
                if sizeCrc == abnorm_sizeCrc.get(file):
                    underrides.add(file)
            if missing:
                status = -10
            elif misEspmed:
                status = 10
            elif mismatched:
                status = 20
            else:
                status = 30
        # --Clean Dirty
        dirty_sizeCrc = self.dirty_sizeCrc
        for file, sizeCrc in dirty_sizeCrc.items():
            sizeCrcDate = data_sizeCrcDate.get(file)
            if (
                not sizeCrcDate
                or sizeCrc != sizeCrcDate[:2]
                or sizeCrc == data_sizeCrc.get(file)
            ):
                del dirty_sizeCrc[file]
        # --Done
        (self.status, oldStatus) = (status, self.status)
        (self.underrides, oldUnderrides) = (underrides, self.underrides)
        return self.status != oldStatus or self.underrides != oldUnderrides

    def install(self, archive, destFiles, data_sizeCrcDate, progress=None):
        """Install specified files to Morrowind\Data files directory."""
        raise AbstractError


class InstallerMarker(Installer):
    """Represents a marker installer entry. Currently only used for the '==Last==' marker"""

    __slots__ = tuple()  # --No new slots

    def __init__(self, archive):
        """Initialize."""
        Installer.__init__(self, archive)
        self.modified = time.time()

    def refreshSource(self, archive, progress=None, fullRefresh=False):
        """Refreshes fileSizeCrcs, size, date and modified from source archive/directory."""
        pass

    def install(self, name, destFiles, data_sizeCrcDate, progress=None):
        """Install specified files to Morrowind\Data files directory."""
        pass


class InstallerArchiveError(bolt.BoltError):
    """Installer exception."""

    pass


class InstallerArchive(Installer):
    """Represents an archive installer entry."""

    __slots__ = tuple()  # --No new slots

    # --File Operations --------------------------------------------------------
    def refreshSource(
        self, archive, progress=None, fullRefresh=False
    ):  # Polemos fixes, speed improvements.
        """Refreshes fileSizeCrcs, size, date and modified from source archive/directory."""
        # Basic file info
        self.modified = archive.mtime
        self.size = archive.size
        self.crc = archive.xxh
        # Get fileSizeCrcs
        fileSizeCrcs = self.fileSizeCrcs = []
        reList = re.compile("(Path|Folder|Size|CRC) = (.+)")
        file = size = crc = isdir = 0
        command = rf'7z.exe l -slt -sccUTF-8 "{archive.s}"'
        args = ushlex.split(command)
        ins = Popen(args, bufsize=32768, stdout=PIPE, creationflags=DETACHED_PROCESS)
        memload = [x for x in ins.stdout]
        for line in memload:
            maList = reList.match(line)
            if maList:
                key, value = maList.groups()
                if key == "Path":
                    file = (value.decode("utf-8")).strip()
                elif key == "Folder":
                    isdir = value[0] == "+"
                elif key == "Size":
                    size = int(value)
                elif key == "CRC":
                    try:
                        crc = int(value, 16)
                        if file and not isdir:
                            fileSizeCrcs.append((file, size, crc))
                    except:
                        pass
                    file = size = crc = isdir = 0
        if not fileSizeCrcs:
            import gui.dialog

            gui.dialog.ErrorMessage(
                None,
                _(
                    "7z module is"
                    " unable to read archive %s.\nTry extracting it and then repacking it before trying again."
                    % (archive.s)
                ),
            )
            return

    def unpackToTemp(
        self, archive, fileNames, progress=None
    ):  # Polemos fixes and addons.
        """Erases all files from self.tempDir and then extracts specified files from archive to self.tempDir.Note: fileNames = File names (not paths)."""
        # Not counting the unicode problems, there were some strange bugs here, wonder why. - Polemos
        try:
            check = fileNames
        except:
            import gui.dialog

            gui.dialog.ErrorMessage(
                None, _("No files to extract for selected archive.")
            )
            return
        progress = progress or bolt.Progress()
        progress.state, progress.full = 0, len(fileNames)
        # --Dump file list
        try:
            with io.open(self.tempList.s, "w", encoding="utf-8") as out:
                out.write("\n".join(fileNames))
        except:
            import gui.dialog

            gui.dialog.ErrorMessage(
                None,
                _(
                    'There was a problem installing your package.\nPlease do a "Full Refresh" from the menu and try again.'
                ),
            )
            self.clearTemp()
            return
        self.clearTemp()
        # --Extract files
        apath = dirs["installers"].join(archive)
        command = rf'7z.exe x "{apath.s}" -bb -y -o"{self.tempDir.s}" @{self.tempList.s} -scsUTF-8'
        args = ushlex.split(command)
        ins = Popen(args, stdout=PIPE, creationflags=DETACHED_PROCESS)
        reExtracting = re.compile("-\s+(.+)")
        reAllOk = re.compile("Everything is Ok")
        extracted = []
        for line in ins.stdout:
            extract_ok = reAllOk.match(line)
            maExtracting = reExtracting.match(line)
            if extract_ok:
                result = True
            if maExtracting:
                extracted.append(maExtracting.group(1).strip())
                progress.plus()
        try:
            check = result  # Polemos: Excepting is fast sometimes.
        except:
            import gui.dialog  # Polemos: In case of errors.

            gui.dialog.ErrorMessage(
                None, _("Errors occurred during extraction and/or Extraction failed.")
            )
        # Ensure that no file is read only:
        for thedir, subdirs, files in scandir.walk(
            self.tempDir.s
        ):  # Polemos: replaced os.walk which is slow in Python 2.7 and below.
            for f in files:
                path_po = os.path.join(thedir, f)
                try:
                    os.chmod(path_po, stat.S_IWRITE)
                except:  # Polemos: Yeah I know...
                    try:
                        os.system(r'attrib -R "%s" /S' % (path_po))
                    except:
                        pass
        self.tempList.remove()

    def install(
        self, archive, destFiles, data_sizeCrcDate, progress=None
    ):  # Polemos fixes.
        """Install specified files to Morrowind directory."""
        # Note: Installs "directly" from the archive here.
        progress = progress or bolt.Progress()
        destDir = dirs["mods"]
        destFiles = set(destFiles)
        data_sizeCrc = self.data_sizeCrc
        dest_src = {
            x: y for x, y in self.refreshDataSizeCrc().iteritems() if x in destFiles
        }
        if not dest_src:
            return 0
        # --Extract
        progress(0, _("%s\nExtracting files...") % archive.s)
        self.unpackToTemp(archive, dest_src.values(), SubProgress(progress, 0, 0.9))
        # --Move
        progress(0.9, _("%s\nMoving files...") % archive.s)
        progress.state, progress.full = 0, len(dest_src)
        count = 0
        norm_ghost = Installer.getGhosted()
        tempDir = self.tempDir
        for dest, src in dest_src.iteritems():
            size, crc = data_sizeCrc[dest]
            srcFull = tempDir.join(src)
            destFull = destDir.join(norm_ghost.get(dest, dest))
            if srcFull.exists():
                srcFull.moveTo(destFull)
                data_sizeCrcDate[dest] = (size, crc, destFull.mtime)
                progress.plus()
                count += 1
        self.clearTemp()
        return count

    def unpackToProject(self, archive, project, progress=None):  # Polemos fixes.
        """Unpacks archive to build directory."""
        progress = progress or bolt.Progress()
        files = self.sortFiles([x[0].strip() for x in self.fileSizeCrcs])
        if not files:
            return 0
        # --Clear Project
        destDir = dirs["installers"].join(project)
        if destDir.exists():
            destDir.rmtree(safety="Installers")
        # --Extract
        progress(0, project.s + _("\nExtracting files..."))
        self.unpackToTemp(archive, files, SubProgress(progress, 0, 0.9))
        # --Move
        progress(0.9, project.s + _("\nMoving files..."))
        progress.state, progress.full = 0, len(files)
        count = 0
        tempDir = self.tempDir
        for file in files:
            srcFull = tempDir.join(file)
            destFull = destDir.join(file)
            if not destDir.exists():
                destDir.makedirs()
            if srcFull.exists():
                srcFull.moveTo(destFull)
                progress.plus()
                count += 1
        self.clearTemp()
        return count


class InstallerProject(Installer):
    """Represents a directory/build installer entry."""

    __slots__ = tuple()  # --No new slots

    def removeEmpties(self, name):
        """Removes empty directories from project directory."""
        empties = set()
        projectDir = dirs["installers"].join(name)
        for asDir, sDirs, sFiles in scandir.walk(
            projectDir.s
        ):  # Polemos: replaced os.walk which is slow in Python 2.7 and below.
            if not (sDirs or sFiles):
                empties.add(GPath(asDir))
        for empty in empties:
            empty.removedirs()
        projectDir.makedirs()  # --In case it just got wiped out.

    def refreshSource(self, archive, progress=None, fullRefresh=False):
        """Refreshes fileSizeCrcs, size, date and modified from source archive/directory."""
        fileSizeCrcs = self.fileSizeCrcs = []
        src_sizeCrcDate = self.src_sizeCrcDate
        apRoot = dirs["installers"].join(archive)
        Installer.refreshSizeCrcDate(
            apRoot, src_sizeCrcDate, progress, True, fullRefresh
        )
        cumDate = 0
        cumSize = 0
        for file in [x.s for x in self.src_sizeCrcDate]:
            size, crc, date = src_sizeCrcDate[GPath(file)]
            fileSizeCrcs.append((file, size, crc))
            cumSize += size
            cumDate = max(cumDate, date)
        self.size = cumSize
        self.modified = cumDate
        self.crc = 0
        self.refreshed = True

    def install(self, name, destFiles, data_sizeCrcDate, progress=None):
        """Install specified files to Morrowind Data directory."""
        # Note: Installs from the "extracted archive" here.
        destDir = dirs["mods"]
        destFiles = set(destFiles)
        data_sizeCrc = self.data_sizeCrc
        dest_src = {
            x: y for x, y in self.refreshDataSizeCrc().iteritems() if x in destFiles
        }
        if not dest_src:
            return 0
        # --Copy Files
        count = 0
        norm_ghost = Installer.getGhosted()
        srcDir = dirs["installers"].join(name)
        progress.state, progress.full = 0, len(dest_src)
        for dest, src in dest_src.iteritems():
            size, crc = data_sizeCrc[dest]
            srcFull = srcDir.join(src)
            destFull = destDir.join(norm_ghost.get(dest, dest))
            if srcFull.exists():
                srcFull.copyTo(destFull)
                data_sizeCrcDate[dest] = (size, crc, destFull.mtime)
                progress.plus()
                count += 1
        return count

    def syncToData(self, package, projFiles):
        """Copies specified projFiles from Morrowind\Data files to project directory."""
        srcDir = dirs["mods"]
        projFiles = set(projFiles)
        srcProj = tuple(
            (x, y) for x, y in self.refreshDataSizeCrc().iteritems() if x in projFiles
        )
        if not srcProj:
            return (0, 0)
        # --Sync Files
        updated = removed = 0
        norm_ghost = Installer.getGhosted()
        projDir = dirs["installers"].join(package)
        for src, proj in srcProj:
            srcFull = srcDir.join(norm_ghost.get(src, src))
            projFull = projDir.join(proj)
            if not srcFull.exists():
                projFull.remove()
                removed += 1
            else:
                srcFull.copyTo(projFull)
                updated += 1
        self.removeEmpties(package)
        return (updated, removed)


class InstallersData(bolt.TankData, DataDict):  # Polemos fixes
    """Installers tank data. This is the data source for."""

    status_color = {
        -20: "grey",
        -10: "red",
        0: "white",
        10: "orange",
        20: "yellow",
        30: "green",
    }
    type_textKey = {1: "BLACK", 2: "NAVY"}

    def __init__(self):
        """Initialize."""
        self.openmw = settings["openmw"]
        self.dir = dirs["installers"]
        self.bashDir = self.dir.join("Bash")
        # --Tank Stuff
        bolt.TankData.__init__(self, settings)
        self.tankKey = "mash.installers"
        self.tankColumns = settings["mash.installers.cols"]
        self.title = _("Installers")
        # --Default Params
        self.defaultParam("columns", self.tankColumns)
        self.defaultParam("colWidths", settings["mash.installers.colWidths"])
        self.defaultParam("colAligns", settings["mash.installers.colAligns"])
        self.defaultParam("colSort", settings["mash.installers.sort"])
        # --Persistent data
        self.dictFile = PickleDict(self.bashDir.join("Installers.dat"))
        self.data = {}
        self.data_sizeCrcDate = {}
        # --Volatile
        self.abnorm_sizeCrc = (
            {}
        )  # --Normative sizeCrc, according to order of active packages
        self.hasChanged = False
        self.loaded = False
        self.lastKey = GPath("==Last==")
        self.renamedSizeDate = (0, 0)

    def addMarker(self, name):
        path = GPath(name)
        self.data[path] = InstallerMarker(path)

    def setChanged(self, hasChanged=True):
        """Mark as having changed."""
        self.hasChanged = hasChanged

    def refresh(
        self, progress=None, what="DIONS", fullRefresh=False
    ):  # D.C.-G. Modified to avoid system error if installers path is not reachable.
        """Refresh info."""
        if not os.access(dirs["installers"].s, os.W_OK):
            return "noDir"
        progress = progress or bolt.Progress()
        # --MakeDirs
        self.bashDir.makedirs()
        # --Refresh Data
        changed = False
        self.refreshRenamed()
        if not self.loaded:
            progress(0, _("Loading Data...\n"))
            self.dictFile.load()
            data = self.dictFile.data
            self.data = data.get("installers", {})
            self.data_sizeCrcDate = data.get("sizeCrcDate", {})
            self.updateDictFile()
            self.loaded = True
            changed = True
        # --Last marker
        if self.lastKey not in self.data:
            self.data[self.lastKey] = InstallerMarker(self.lastKey)
        # --Refresh Other
        if "D" in what:
            changed |= Installer.refreshSizeCrcDate(
                dirs["mods"],
                self.data_sizeCrcDate,
                progress,
                settings["mash.installers.removeEmptyDirs"],
                fullRefresh,
            )
        if "I" in what:
            changed |= self.refreshRenamed()
        if "I" in what:
            changed |= self.refreshInstallers(progress, fullRefresh)
        if "O" in what or changed:
            changed |= self.refreshOrder()
        if "N" in what or changed:
            changed |= self.refreshNorm()
        if "S" in what or changed:
            changed |= self.refreshStatus()
        # --Done
        if changed:
            self.hasChanged = True
        return changed

    def updateDictFile(self):
        """Updates self.data to use new classes."""
        if self.dictFile.vdata.get("version", 0):
            return
        # --Update to version 1
        for name in self.data.keys():
            installer = self.data[name]
            if isinstance(installer, Installer):
                self.data[name] = installer.__copy__(InstallerArchive)
        self.dictFile.vdata["version"] = 1

    def save(self):
        """Saves to pickle file."""
        if self.hasChanged:
            self.dictFile.data["installers"] = self.data
            self.dictFile.data["sizeCrcDate"] = self.data_sizeCrcDate
            self.dictFile.save()
            self.hasChanged = False

    def saveCfgFile(
        self,
    ):  # -# D.C.-G.,  Polemos: fixes, change mash.ini into an override.
        """Save the installers path to mash.ini."""
        mashini_loc = os.path.join(MashDir, "mash.ini")
        if not os.path.exists(mashini_loc) or self.openmw:
            return
        import ConfigParser

        mash_ini = False
        if GPath("mash.ini").exists():
            mashIni = ConfigParser.ConfigParser()
            try:
                with io.open("mash.ini", "r", encoding="utf-8") as f:
                    mashIni.readfp(f)
                mash_ini = True
                instPath = GPath(mashIni.get("General", "sInstallersDir").strip()).s
            except:
                mash_ini = False
                instPath = ""
        else:
            instPath = ""
        if instPath != dirs["installers"].s:
            if not mash_ini:
                if os.path.exists(os.path.join(MashDir, "mash_default.ini")):
                    with io.open("mash_default.ini", "r", encoding="utf-8") as f:
                        d = f.read()
                else:
                    d = "[General]\n"
                with io.open("mash.ini", "w", encoding="utf-8") as f:
                    f.write(d)
                mashIni = ConfigParser.ConfigParser()
                try:
                    with io.open("mash.ini", "r", encoding="utf-8") as f:
                        mashIni.readfp(f)
                except:
                    pass
            mashIni.set(
                "General", "sInstallersDir", os.path.abspath(dirs["installers"].s)
            )
            installers_po = "[General]\nsInstallersDir=%s" % (
                str(GPath(mashIni.get("General", "sInstallersDir").strip()))
                .replace("bolt.Path(u'", "")
                .replace("')", "")
            ).decode("unicode_escape")
            with io.open("mash.ini", "wb+", encoding="utf-8") as f:
                f.write(installers_po)

    def getSorted(self, column, reverse):
        """Returns items sorted according to column and reverse."""
        data = self.data
        items = data.keys()
        if column == "Package":
            items.sort(reverse=reverse)
        elif column == "Files":
            items.sort(key=lambda x: len(data[x].fileSizeCrcs), reverse=reverse)
        else:
            items.sort()
            attr = column.lower()
            if column in ("Package", "Group"):
                getter = lambda x: object.__getattribute__(data[x], attr).lower()
                items.sort(key=getter, reverse=reverse)
            else:
                getter = lambda x: object.__getattribute__(data[x], attr)
                items.sort(key=getter, reverse=reverse)
        settings["mash.installers.sort"] = column
        # --Special sorters
        if settings["mash.installers.sortStructure"]:
            items.sort(key=lambda x: data[x].type)
        if settings["mash.installers.sortActive"]:
            items.sort(key=lambda x: not data[x].isActive)
        if settings["mash.installers.sortProjects"]:
            items.sort(key=lambda x: not isinstance(data[x], InstallerProject))
        return items

    def getColumns(self, item=None):  # --Item Info
        """Returns text labels for item or for row header if item is None."""
        columns = self.getParam("columns")
        if item is None:
            return columns[:]
        labels, installer = [], self.data[item]
        for column in columns:
            if column == "Package":
                labels.append(item.s)
            elif column == "Files":
                labels.append(formatInteger(len(installer.fileSizeCrcs)))
            else:
                value = object.__getattribute__(installer, column.lower())
                if column in ("Package", "Group"):
                    pass
                elif column == "Order":
                    value = f"{value}"
                elif column == "Modified":
                    value = formatDate(value)
                elif column == "Size":
                    try:
                        value = megethos(value)
                    except:
                        value = f"{formatInteger(value/1024)}KB"
                else:
                    raise ArgumentError(column)
                labels.append(value)
        return labels

    def getGuiKeys(self, item):
        """Returns keys for icon and text and background colors."""
        installer = self.data[item]
        # --Text
        if installer.type == 2 and len(installer.subNames) == 2:
            textKey = self.type_textKey[1]
        else:
            textKey = self.type_textKey.get(installer.type, "GREY")
        # --Background
        backKey = (installer.skipDirFiles and "mash.installers.skipped") or None
        if installer.dirty_sizeCrc:
            backKey = "bash.installers.dirty"
        elif installer.underrides:
            backKey = "mash.installers.outOfOrder"
        # --Icon
        iconKey = (
            ("off", "on")[installer.isActive]
            + "."
            + self.status_color[installer.status]
        )
        if installer.type < 0:
            iconKey = "corrupt"
        elif isinstance(installer, InstallerProject):
            iconKey += ".dir"
        return (iconKey, textKey, backKey)

    def getName(self, item):
        """Returns a string name of item for use in dialogs, etc."""
        return item.s

    def getColumn(self, item, column):
        """Returns item data as a dictionary."""
        raise UncodedError

    def setColumn(self, item, column, value):
        """Sets item values from a dictionary."""
        raise UncodedError

    # --Dict Functions -----------------------------------------------------------
    def __delitem__(self, item):
        """Delete an installer. Delete entry AND archive file itself."""
        if item == self.lastKey:
            return
        installer = self.data[item]
        apath = self.dir.join(item)
        if isinstance(installer, InstallerProject):
            apath.rmtree(safety="Installers")
        else:
            apath.remove()
        del self.data[item]

    def copy(self, item, destName, destDir=None):
        """Copies archive to new location."""
        if item == self.lastKey:
            return
        destDir = destDir or self.dir
        apath = self.dir.join(item)
        apath.copyTo(destDir.join(destName))
        if destDir == self.dir:
            self.data[destName] = installer = copy.copy(self.data[item])
            installer.isActive = False
            self.refreshOrder()
            self.moveArchives([destName], self.data[item].order + 1)

    def rename(self, item, destName, destDir=None):  # Polemos
        """Rename archive/folder."""
        if item == self.lastKey:
            return
        destDir = destDir or self.dir
        apath = self.dir.join(item)
        if not apath.renameTo(destDir.join(destName)):
            return False
        if destDir == self.dir:
            self.data[destName] = installer = copy.copy(self.data[item])
            installer.isActive = False
            self.refreshOrder()
            self.moveArchives([destName], self.data[item].order)
            del self.data[item]
            return True

    # --Refresh Functions --------------------------------------------------------
    def refreshRenamed(self):
        """Refreshes Installer.off_local from corresponding csv file."""
        changed = False
        pRenamed = dirs["mods"].join("Mash", "Official_Local.csv")
        if not pRenamed.exists():
            changed = bool(Installer.off_local)
            self.renamedSizeDate = (0, 0)
            Installer.off_local.clear()
        elif self.renamedSizeDate != (pRenamed.size, pRenamed.mtime):
            self.renamedSizeDate = (pRenamed.size, pRenamed.mtime)
            off_local = {}
            reader = bolt.CsvReader(pRenamed)
            for fields in reader:
                if len(fields) < 2 or not fields[0] or not fields[1]:
                    continue
                off, local = map(string.strip, fields[:2])
                if not reModExt.search(off) or not reModExt.search(local):
                    continue
                off, local = map(GPath, (off, local))
                if off != local:
                    off_local[off] = local
            reader.close()
            changed = off_local != Installer.off_local
            Installer.off_local = off_local
        # --Refresh Installer mappings
        if changed:
            for installer in self.data.itervalues():
                installer.refreshDataSizeCrc()
        # --Done
        return changed

    def refreshInstallers(self, progress=None, fullRefresh=False):
        """Refresh installer data."""
        progress = progress or bolt.Progress()
        changed = False
        pending = set()
        projects = set()
        # --Current archives
        newData = {}
        if not self.openmw:  # Polemos: Regular Morrowind support
            for i in self.data.keys():
                if isinstance(self.data[i], InstallerMarker):
                    newData[i] = self.data[i]
        for archive in dirs["installers"].list():
            apath = dirs["installers"].join(archive)
            isdir = apath.isdir()
            if isdir:
                projects.add(archive)
            if (isdir and archive != "Bash") or archive.cext in (".7z", ".zip", ".rar"):
                installer = self.data.get(archive)
                if not installer:
                    pending.add(archive)
                elif (isdir and not installer.refreshed) or (
                    (installer.size, installer.modified) != (apath.size, apath.mtime)
                ):
                    newData[archive] = installer
                    pending.add(archive)
                else:
                    newData[archive] = installer
        if fullRefresh:
            pending |= set(newData)
        changed = bool(pending) or (len(newData) != len(self.data))
        if not self.openmw:  # Polemos: Regular Morrowind support
            # --New/update crcs?
            for subPending, iClass in zip(
                (pending - projects, pending & projects),
                (InstallerArchive, InstallerProject),
            ):
                if not subPending:
                    continue
                progress(0, _("Scanning Packages..."))
                progress.setFull(len(subPending))
                for index, package in enumerate(sorted(subPending)):
                    progress(index, _("Scanning Packages...\n %s" % package.s))
                    installer = newData.get(package)
                    if not installer:
                        installer = newData.setdefault(package, iClass(package))
                    apath = dirs["installers"].join(package)
                    try:
                        installer.refreshBasic(
                            apath, SubProgress(progress, index, index + 1)
                        )
                    except InstallerArchiveError:
                        installer.type = -1
        self.data = newData
        return changed

    def refreshRenamedNeeded(self):
        pRenamed = dirs["mods"].join("Mash", "Official_Local.csv")
        if not pRenamed.exists():
            return bool(Installer.off_local)
        else:
            return self.renamedSizeDate != (pRenamed.size, pRenamed.mtime)

    def refreshInstallersNeeded(self):
        """Returns true if refreshInstallers is necessary. (Point is to skip use
        of progress dialog when possible."""
        for archive in dirs["installers"].list():
            apath = dirs["installers"].join(archive)
            if not apath.isfile() or not archive.cext in (".7z", ".zip", ".rar"):
                continue
            installer = self.data.get(archive)
            if not installer or (installer.size, installer.modified) != (
                apath.size,
                apath.mtime,
            ):
                return True
        return False

    def refreshOrder(self):
        """Refresh installer status."""
        changed = False
        data = self.data
        ordered, pending = [], []
        for archive, installer in self.data.iteritems():
            if installer.order >= 0:
                ordered.append(archive)
            else:
                pending.append(archive)
        pending.sort()
        ordered.sort()
        ordered.sort(key=lambda x: data[x].order)
        if self.lastKey in ordered:
            index = ordered.index(self.lastKey)
            ordered[index:index] = pending
        else:
            ordered += pending
        order = 0
        for archive in ordered:
            if data[archive].order != order:
                data[archive].order = order
                changed = True
            order += 1
        return changed

    def refreshNorm(self):
        """Refresh self.abnorm_sizeCrc."""
        data = self.data
        active = [x for x in data if data[x].isActive]
        active.sort(key=lambda x: data[x].order)
        # --norm
        norm_sizeCrc = {}
        for package in active:
            norm_sizeCrc.update(data[package].data_sizeCrc)
        # --Abnorm
        abnorm_sizeCrc = {}
        data_sizeCrcDate = self.data_sizeCrcDate
        for path, sizeCrc in norm_sizeCrc.iteritems():
            sizeCrcDate = data_sizeCrcDate.get(path)
            if sizeCrcDate and sizeCrc != sizeCrcDate[:2]:
                abnorm_sizeCrc[path] = sizeCrcDate[:2]
        (self.abnorm_sizeCrc, oldAbnorm_sizeCrc) = (abnorm_sizeCrc, self.abnorm_sizeCrc)
        return abnorm_sizeCrc != oldAbnorm_sizeCrc

    def refreshStatus(self):
        """Refresh installer status."""
        changed = False
        for installer in self.data.itervalues():
            changed |= installer.refreshStatus(self)
        return changed

    # --Operations -------------------------------------------------------------
    def moveArchives(self, moveList, newPos):
        """Move specified archives to specified position."""
        moveSet = set(moveList)
        data = self.data
        numItems = len(data)
        orderKey = lambda x: data[x].order
        oldList = sorted(data, key=orderKey)
        newList = [x for x in oldList if x not in moveSet]
        moveList.sort(key=orderKey)
        newList[newPos:newPos] = moveList
        for index, archive in enumerate(newList):
            data[archive].order = index
        self.setChanged()

    def install(self, archives, progress=None, last=False, override=True):
        """Install selected archives.
        what:
            'MISSING': only missing files.
            Otherwise: all (unmasked) files.
        """
        progress = progress or bolt.Progress()
        # --Mask and/or reorder to last
        mask = set()
        if last:
            self.moveArchives(archives, len(self.data))
        else:
            maxOrder = max(self[x].order for x in archives)
            for installer in self.data.itervalues():
                if installer.order > maxOrder and installer.isActive:
                    mask |= set(installer.data_sizeCrc)
        # --Install archives in turn
        progress.setFull(len(archives))
        archives.sort(key=lambda x: self[x].order, reverse=True)
        for index, archive in enumerate(archives):
            progress(index, archive.s)
            installer = self[archive]
            destFiles = set(installer.data_sizeCrc) - mask
            if not override:
                destFiles &= installer.missingFiles
            if destFiles:
                installer.install(
                    archive,
                    destFiles,
                    self.data_sizeCrcDate,
                    SubProgress(progress, index, index + 1),
                )
            installer.isActive = True
            mask |= set(installer.data_sizeCrc)
        self.refreshStatus()

    def uninstall(self, unArchives, progress=None):
        """Uninstall selected archives."""
        unArchives = set(unArchives)
        data = self.data
        data_sizeCrcDate = self.data_sizeCrcDate
        getArchiveOrder = lambda x: self[x].order
        # --Determine files to remove and files to restore. Keep in mind that
        #  that multiple input archives may be interspersed with other archives
        #  that may block (mask) them from deleting files and/or may provide
        #  files that should be restored to make up for previous files. However,
        #  restore can be skipped, if existing files matches the file being
        #  removed.
        masked = set()
        removes = set()
        restores = {}
        # --March through archives in reverse order...
        for archive in sorted(data, key=getArchiveOrder, reverse=True):
            installer = data[archive]
            # --Uninstall archive?
            if archive in unArchives:
                for data_sizeCrc in (installer.data_sizeCrc, installer.dirty_sizeCrc):
                    for file, sizeCrc in data_sizeCrc.iteritems():
                        sizeCrcDate = data_sizeCrcDate.get(file)
                        if (
                            file not in masked
                            and sizeCrcDate
                            and sizeCrcDate[:2] == sizeCrc
                        ):
                            removes.add(file)
            # --Other active archive. May undo previous removes, or provide a restore file.
            #  And/or may block later uninstalls.
            elif installer.isActive:
                files = set(installer.data_sizeCrc)
                myRestores = (removes & files) - set(restores)
                for file in myRestores:
                    if (
                        installer.data_sizeCrc[file]
                        != data_sizeCrcDate.get(file, (0, 0, 0))[:2]
                    ):
                        restores[file] = archive
                    removes.discard(file)
                masked |= files
        # --Remove files
        emptyDirs = set()
        modsDir = dirs["mods"]
        progress.state, progress.full = 0, len(removes)
        for file in removes:
            progress.plus()
            path = modsDir.join(file)
            path.remove()
            (path + ".ghost").remove()
            del data_sizeCrcDate[file]
            emptyDirs.add(path.head)
        # --Remove empties
        for emptyDir in emptyDirs:
            if emptyDir.isdir() and not emptyDir.list():
                emptyDir.removedirs()
        # --De-activate
        for archive in unArchives:
            data[archive].isActive = False
        # --Restore files
        restoreArchives = sorted(
            set(restores.itervalues()), key=getArchiveOrder, reverse=True
        )
        if ["mash.installers.autoAnneal"] and restoreArchives:
            progress.setFull(len(restoreArchives))
            for index, archive in enumerate(restoreArchives):
                progress(index, archive.s)
                installer = data[archive]
                destFiles = {x for x, y in restores.iteritems() if y == archive}
                if destFiles:
                    installer.install(
                        archive,
                        destFiles,
                        data_sizeCrcDate,
                        SubProgress(progress, index, index + 1),
                    )
        # --Done
        progress.state = len(removes)
        self.refreshStatus()

    def anneal(self, anPackages=None, progress=None):
        """Anneal selected packages. If no packages are selected, anneal all.
        Anneal will:
        * Correct underrides in anPackages.
        * Install missing files from active anPackages."""
        data = self.data
        data_sizeCrcDate = self.data_sizeCrcDate
        anPackages = set(anPackages or data)
        getArchiveOrder = lambda x: data[x].order
        # --Get remove/refresh files from anPackages
        removes = set()
        for package in anPackages:
            installer = data[package]
            removes |= installer.underrides
            if installer.isActive:
                removes |= installer.missingFiles
                removes |= set(installer.dirty_sizeCrc)
        # --March through packages in reverse order...
        restores = {}
        for package in sorted(data, key=getArchiveOrder, reverse=True):
            installer = data[package]
            # --Other active package. May provide a restore file.
            #  And/or may block later uninstalls.
            if installer.isActive:
                files = set(installer.data_sizeCrc)
                myRestores = (removes & files) - set(restores)
                for file in myRestores:
                    if (
                        installer.data_sizeCrc[file]
                        != data_sizeCrcDate.get(file, (0, 0, 0))[:2]
                    ):
                        restores[file] = package
                    removes.discard(file)
        # --Remove files
        emptyDirs = set()
        modsDir = dirs["mods"]
        for file in removes:
            path = modsDir.join(file)
            path.remove()
            (path + ".ghost").remove()
            data_sizeCrcDate.pop(file, None)
            emptyDirs.add(path.head)
        # --Remove empties
        for emptyDir in emptyDirs:
            if emptyDir.isdir() and not emptyDir.list():
                emptyDir.removedirs()
        # --Restore files
        restoreArchives = sorted(
            set(restores.itervalues()), key=getArchiveOrder, reverse=True
        )
        if restoreArchives:
            progress.setFull(len(restoreArchives))
            for index, package in enumerate(restoreArchives):
                progress(index, package.s)
                installer = data[package]
                destFiles = {x for x, y in restores.iteritems() if y == package}
                if destFiles:
                    installer.install(
                        package,
                        destFiles,
                        data_sizeCrcDate,
                        SubProgress(progress, index, index + 1),
                    )

    def getConflictReport(self, srcInstaller, mode):
        """Returns report of overrides for specified package for display on conflicts tab.
        mode: O: Overrides; U: Underrides"""
        data = self.data
        srcOrder = srcInstaller.order
        conflictsMode = mode == "OVER"
        if conflictsMode:
            mismatched = set(srcInstaller.data_sizeCrc)
        else:
            mismatched = srcInstaller.underrides
        showInactive = (
            conflictsMode and settings["mash.installers.conflictsReport.showInactive"]
        )
        showLower = (
            conflictsMode and settings["mash.installers.conflictsReport.showLower"]
        )
        if not mismatched:
            return ""
        src_sizeCrc = srcInstaller.data_sizeCrc
        packConflicts = []
        getArchiveOrder = lambda x: data[x].order
        for package in sorted(self.data, key=getArchiveOrder):
            installer = data[package]
            if installer.order == srcOrder:
                continue
            if not showInactive and not installer.isActive:
                continue
            if not showLower and installer.order < srcOrder:
                continue
            curConflicts = Installer.sortFiles(
                [
                    x.s
                    for x, y in installer.data_sizeCrc.iteritems()
                    if x in mismatched and y != src_sizeCrc[x]
                ]
            )
            if curConflicts:
                packConflicts.append((installer.order, package.s, curConflicts))
        # --Unknowns
        isHigher = -1
        buff = cStringIO.StringIO()
        for order, package, files in packConflicts:
            if showLower and (order > srcOrder) != isHigher:
                isHigher = order > srcOrder
                buff.write(
                    "= %s %s\n" % ((_("Lower"), _("Higher"))[isHigher], "=" * 40)
                )
            buff.write("==%d== %s\n" % (order, package))
            for file in files:
                buff.write(file)
                buff.write("\n")
            buff.write("\n")
        report = buff.getvalue()
        if not conflictsMode and not report and not srcInstaller.isActive:
            report = _("No Underrides. Mod is not completely un-installed.")
        return report


class FileLibrary(FileRep):
    """File representation for generating library books.
    Generates library books from input text file and current mod load list."""

    def __init__(self, fileInfo, canSave=True, log=None, progress=None):
        """Initialize."""
        self.srcBooks = {}  # --srcBooks[srcId] = (bookRecord,modName)
        self.altBooks = {}  # --altBooks[altId] = (bookRecord,modName)
        self.libList = []  # --libId1, libId2, etc. in same order as in text file.
        self.libMap = {}  # --libMap[libId]  = (srcId,altId)
        FileRep.__init__(self, fileInfo, canSave, log, progress)

    def loadUI(self, factory={"GLOB": Glob, "BOOK": Book, "SCPT": Scpt, "CELL": Cell}):
        """Loads data from file."""
        FileRep.loadUI(self, factory)

    def loadText(self, inName):
        """Read library book list from specified text file."""
        reComment = re.compile(r"\s*\#.*")
        ins = file(inName)
        for line in ins:
            # --Strip spaces and comments
            line = reComment.sub("", line)
            line = line.rstrip()
            # --Skip empty/comment lines
            if not line:
                continue
            # --Parse line
            (libId, srcId, altId) = line.split("\t")[:3]
            self.libList.append(libId)
            self.libMap[libId] = (srcId, altId)
        # --Done
        ins.close()

    def getBooks(self):
        """Extracts source book data from currently loaded mods."""
        srcIds = set([srcId for srcId, altId in self.libMap.values()])
        altIds = set([altId for srcId, altId in self.libMap.values()])
        factory = {"BOOK": Book}
        for modName in mwIniFile.loadOrder:
            print(modName)
            fileRep = FileRep(modInfos[modName], False)
            fileRep.load(keepTypes=None, factory=factory)
            for record in fileRep.records:
                if record.name == "BOOK":
                    bookId = record.getId()
                    if bookId in srcIds:
                        # print '',bookId
                        print(f" {bookId}")
                        self.srcBooks[bookId] = (record, modName)
                    elif bookId in altIds:
                        # print '',bookId
                        print(f" {bookId}")
                        self.altBooks[bookId] = (record, modName)

    def copyBooks(self):
        """Copies non-Morrowind books to self."""
        skipMods = {"Morrowind.esm", self.fileInfo.name}
        for id, (record, modName) in self.srcBooks.items() + self.altBooks.items():
            if modName not in skipMods:
                self.setRecord(copy.copy(record))

    def genLibData(self):
        """Creates new esp with placed refs for lib books. WILL OVERWRITE!"""
        import mush

        tsMain = string.Template(mush.libGenMain)
        tsIfAltId = string.Template(mush.libGenIfAltId)
        # --Data Records
        for id in ("lib_action", "lib_actionCount"):
            glob = self.getRecord("GLOB", id, Glob)
            (glob.type, glob.value) = ("s", 0)
            glob.setChanged()
        setAllCode = "begin lib_setAllGS\n"
        setNoneCode = "begin lib_setNoneGS\n"
        for libId in self.libList:
            (srcId, altId) = self.libMap[libId]
            srcBook = self.srcBooks.get(srcId)[0]
            if not srcBook:
                # print '%s: Missing source: %s' % (libId,srcId)
                print(f"{libId}: Missing source: {srcId}")
                continue
            # --Global
            glob = self.getRecord("GLOB", libId + "G", Glob)
            (glob.type, glob.value) = ("s", 0)
            glob.setChanged()
            # --Script
            scriptId = libId + "LS"
            script = self.getRecord("SCPT", scriptId, Scpt)
            scriptCode = tsMain.substitute(
                libId=libId,
                srcId=srcId,
                ifAltId=(
                    (altId and tsIfAltId.substitute(libId=libId, altId=altId)) or ""
                ),
            )
            script.setCode(scriptCode)
            script.setChanged()
            # --Book
            srcBook.load(unpack=True)
            book = self.getRecord("BOOK", libId, Book)
            book.model = srcBook.model
            book.title = srcBook.title
            book.icon = srcBook.icon
            book.text = srcBook.text
            book.script = scriptId
            book.setChanged()
            # --Set Scripts
            setAllCode += "set %sG to 1\n" % (libId,)
            setNoneCode += "set %sG to 0\n" % (libId,)
        # --Set scripts
        for id, code in (("lib_setAllGS", setAllCode), ("lib_setNoneGS", setNoneCode)):
            code += ";--Done\nstopScript %s\nend\n" % (id,)
            script = self.getRecord("SCPT", id, Scpt)
            script.setCode(code)
            script.setChanged()

    def genLibCells(self):
        """Generates standard library"""
        # --Cell Records
        objNum = 1
        cellParameters = (
            ("East", 270, 0, 0, 0, -6),
            ("North", 180, 270, 90, 6, 0),
            ("South", 0, 90, 90, -6, 0),
            ("West", 90, 0, 180, 0, 6),
        )
        for name, rx, ry, rz, dx, dy in cellParameters:
            # --Convert to radians.
            rx, ry, rz = [rot * math.pi / 180.0 for rot in (rx, ry, rz)]
            # --Create cell
            cellName = "BOOKS " + name
            cell = self.getRecord("CELL", cellName, Cell)
            cell.cellName = cellName
            (cell.flags, cell.gridX, cell.gridY) = (1, 1, 1)
            del cell.objects[:]
            del cell.tempObjects[:]
            tempObjects = cell.tempObjects = []
            for index, libId in enumerate(self.libList):
                srcId = self.libMap[libId][0]
                if srcId not in self.srcBooks:
                    continue
                srData = SubRecord("DATA", 24)
                srData.setData(
                    struct.pack("6f", index * dx, index * dy, 100, rx, ry, rz)
                )
                tempObjects.append((0, objNum, libId, [Cell_Frmr(), srData]))
                objNum += 1
            cell.setChanged()

    def doImport(self, textFile):
        """Does all the import functions."""
        self.loadText(textFile)
        self.getBooks()
        # self.copyBooks()
        self.genLibData()
        self.genLibCells()
        self.sortRecords()


# Processing Functions, Classes -----------------------------------------------


class CharSetImporter:
    """Imports CharSets from text file to mod."""

    def __init__(self):
        self.log = Log()
        self.classStats = {}

    def loadText(self, fileName):
        """TextMunch: Reads in 0/30 level settings and spits out a level setting script."""
        # --Constants
        reComment = re.compile(";.*")
        reClassName = re.compile(r"@\s*([a-zA-Z0-9_]+)")
        reStats = re.compile(r"\s*(\d+)\s+(\d+)")
        statNames = (
            "Agility",
            "Block",
            "Light Armor",
            "Marksman",
            "Sneak",
            "Endurance",
            "Heavy Armor",
            "Medium Armor",
            "Spear",
            "Intelligence",
            "Alchemy",
            "Conjuration",
            "Enchant",
            "Security",
            "Personality",
            "Illusion",
            "Mercantile",
            "Speechcraft",
            "Speed",
            "Athletics",
            "Hand To Hand",
            "Short Blade",
            "Unarmored",
            "Strength",
            "Acrobatics",
            "Armorer",
            "Axe",
            "Blunt Weapon",
            "Long Blade",
            "Willpower",
            "Alteration",
            "Destruction",
            "Mysticism",
            "Restoration",
            "Luck",
        )
        # --Read file
        with open(fileName) as inn:
            curStats = className = None
            for line in inn:
                stripped = reComment.sub("", line).strip()
                maClassName = reClassName.match(stripped)
                maStats = reStats.match(stripped)
                if not stripped:
                    pass
                elif maClassName:
                    className = maClassName.group(1)
                    curStats = self.classStats[className] = []
                elif maStats:
                    v00, v30 = [int(stat) for stat in maStats.groups()]
                    curStats.append((v00, v30))
                else:
                    raise MoshError(
                        _("Bad line in CharSet class file.")
                        + line.strip()
                        + " >> "
                        + stripped
                    )
        # --Post Parse
        for className, stats in self.classStats.items():
            if len(stats) != 35:
                raise MoshError(_("Bad number of stats for class ") + className)
            stats = self.classStats[className] = dict(zip(statNames, stats))
            # --Health
            str00, str30 = stats["Strength"]
            end00, end30 = stats["Endurance"]
            hea00 = (str00 + end00) / 2
            hea30 = (str30 + end30) / 2 + end30 * 29 / 10
            stats["Health"] = (hea00, hea30)

    def printMajors(self):
        """Print major and minor skills for each class."""
        import mush

        skills = mush.combatSkills + mush.magicSkills + mush.stealthSkills
        for className, stats in sorted(self.classStats.items()):
            print(f"{className}-------------------------------")
            skillStats = [(key, value) for key, value in stats.items() if key in skills]
            skillStats.sort(key=lambda a: a[1][1], reverse=True)
            for low, high in ((0, 5), (5, 10)):
                for skill, stat in sorted(skillStats[low:high]):
                    print(f"{skill:-13s}  {stat[1]:3d}")
                print()

    def save(self, fileInfo):
        """Add charset scripts to esp."""
        fileRep = FileRep(fileInfo)
        fileRep.load(factory={"SCPT": Scpt})
        fileRep.unpackRecords({"SCPT"})
        fileRep.indexRecords({"SCPT"})
        # --Add scripts
        for className in self.classStats.keys():
            print(className)
            id = f"wr_lev{className}GS"
            script = fileRep.getRecord("SCPT", id, Scpt)
            script.setCode(self.getScript(className))
        # --Done
        fileRep.sortRecords()
        fileRep.safeSave()

    def getScript(self, className):
        """Get stat setting script for classname."""
        # --Constants
        import mush

        charSet0 = string.Template(mush.charSet0)
        charSet1 = string.Template(mush.charSet1)
        reSpace = re.compile(r"\s+")
        statGroups = (
            ("Primary", mush.primaryAttributes),
            ("Secondary", ("Health",)),
            ("Combat Skills", mush.combatSkills),
            ("Magic Skills", mush.magicSkills),
            ("Stealth Skills", mush.stealthSkills),
        )
        # --Dump Script
        stats = self.classStats[className]
        out = cStringIO.StringIO()
        out.write(charSet0.substitute(className=className))
        for group, statNames in statGroups:
            out.write(";--" + group + "\n")
            for statName in statNames:
                shortName = reSpace.sub("", statName)
                v00, v30 = stats[statName]
                if v00 == v30:
                    out.write(
                        "set%s %d\n"
                        % (
                            shortName,
                            v00,
                        )
                    )
                else:
                    out.write(
                        "  set stemp to %d + ((%d - %d)*level/30)\n" % (v00, v30, v00)
                    )
                    out.write("set%s stemp\n" % (shortName,))
            out.write("\n")
        out.write(charSet1.substitute(className=className))
        return out.getvalue()


class ScheduleGenerator:
    """Generates schedules from input text files."""

    def __init__(self):
        import mush

        self.log = Log()
        # --Project
        self.project = None
        # --Definitions
        #  defs[key] = string
        self.defs = {}
        self.defs.update(dictFromLines(mush.scheduleDefs, re.compile(r":\s+")))
        # --Code
        #  code[town] = [[lines0],[lines1],[lines2]...]
        #  lines0 used for all cycles
        self.code = {}
        # --Sleep (sleep, lighting, etc.)
        #  sleep[town][cycle] = [(cell1,state1),(cell2,state2),...]
        #  state = '-' (not sleeping), '+' (sleeping)
        self.sleep = {}
        # --Schedule
        #  schedule[town][npc] = [(condition1,[act1,act2,act3,act4]),(condition2,[...])]
        #  actN = (posString,aiString)
        self.schedule = {}
        # --New towns. I.e., towns that just imported.
        self.newTowns = set()
        # --Template Strings
        self.tsMaster = string.Template(mush.scheduleMaster)
        self.tsCycle1 = string.Template(mush.scheduleCycle1)
        self.tsSleep0 = string.Template(mush.scheduleSleep0)
        self.tsSleep1 = string.Template(mush.scheduleSleep1)
        self.tsSleep2 = string.Template(mush.scheduleSleep2)
        self.tsReset0 = string.Template(mush.scheduleReset0)
        self.tsReset1 = string.Template(mush.scheduleReset1)
        self.tsReset2 = string.Template(mush.scheduleReset2)

    # --Schedule
    def loadText(self, fileName, pickScheduleFile=None, imported=None):
        """Read schedule from file."""
        # --Localizing
        defs = self.defs
        log = self.log
        # --Re's
        reCell = re.compile('\s*(".*?")')
        reCodeCycle = re.compile("\s*([1-4][ ,1-4]*)")
        reComment = re.compile(r"\s*\#.*")
        reDef = re.compile(r"\.([a-zA-Z]\w+)")
        rePos = re.compile("-?\d+\s+-?\d+\s+-?\d+\s+-?\d+")
        reRepeat = re.compile("= (\d)")
        reSleep = re.compile(r"([=+\-\*\^~x])\s+(.+)$")
        reWander = re.compile("wander +(\d+)")
        reIsMember = re.compile('isMember +(".+")')
        # --Functions/Translators
        replDef = lambda a: defs[a.group(1)]
        # --0: awake, 1: sleep+trespass, 2: sleep 3: dim trespass
        sleepStates = {"=": None, "-": 0, "+": 1, "*": 2, "^": 3, "~": 4, "x": 5}
        # --Log
        header = os.path.split(fileName)[-1]
        if len(header) < 70:
            header += "=" * (70 - len(header))
        log.setHeader(header)
        # --Imported
        isTopFile = imported is None
        if isTopFile:
            imported = []
        # --Input variables
        section = None
        town = None
        townNpcs = set()
        townSchedule = None
        npcSchedule = None
        codeCycles = [0]
        # --Parse input file
        with file(fileName) as ins:
            for line in ins:
                # --Strip spaces and comments
                line = reComment.sub("", line)
                line = line.rstrip()
                # --Skip empty/comment lines
                if not line:
                    continue
                # --Section header?
                if line[0] == "@":
                    # (town|defs|night|code|npcName)[: npcCondition]
                    parsed = line[1:].split(":", 1)
                    id = parsed[0].strip()
                    # --Non-npc?
                    if id in {
                        "town",
                        "defs",
                        "night",
                        "evening",
                        "code",
                        "import",
                        "project",
                    }:
                        section = id
                        if section in ("evening", "night"):
                            townSleep = self.sleep[town]
                        elif section == "code":
                            cycles = [0]
                            townCode = self.code[town] = [[], [], [], [], []]
                    else:
                        section = "npc"
                        npc = id
                        # --Any town,npc combination will overwrite any town,npc
                        #  combination from an imported file.
                        if (town, npc) not in townNpcs:
                            townNpcs.add((town, npc))
                            townSchedule[npc] = []
                        npcSchedule = [0, 0, 0, 0]
                        condition = len(parsed) == 2 and parsed[1].strip()
                        townSchedule[npc].append((condition, npcSchedule))
                    if section not in {"town", "import", "project"}:
                        log("  " + line[1:])
                # --Data
                else:
                    # --Import
                    if section == "import":
                        newPath = line.strip()
                        log(_("IMPORT: ") + newPath)
                        if not os.path.exists(newPath) and pickScheduleFile:
                            caption = "Find sub-import file %s:" % (newPath,)
                            newPath = pickScheduleFile(caption, newPath)
                        if not (newPath and os.path.exists(newPath)):
                            raise StateError(
                                "Unable to import schedule file: " + line.strip()
                            )
                        if newPath.lower() in [dir.lower() for dir in imported]:
                            log(_("  [%s already imported.]") % (newPath,))
                        else:
                            log.indent += "> "
                            imported.append(newPath)
                            self.loadText(newPath, pickScheduleFile, imported)
                            log.indent = log.indent[:-2]
                    # --Project
                    elif section == "project" and isTopFile:
                        self.project = line.strip()
                        log(_("PROJECT: ") + self.project)
                    # --Defs
                    elif section == "defs":
                        (key, value) = line.strip().split(":", 1)
                        defs[key] = value.strip()
                    # --Town
                    elif section == "town":
                        town = line.strip()
                        log.setHeader(town)
                        if isTopFile:
                            self.newTowns.add(town)
                        if town not in self.schedule:
                            self.schedule[town] = {}
                            self.sleep[town] = {3: {}, 4: {}}
                        townSchedule = self.schedule[town]
                        npcSchedule = None
                        codeCycles = []
                    # --Code
                    elif section == "code":
                        line = reDef.sub(replDef, line)
                        maCodeCycle = reCodeCycle.match(line)
                        if maCodeCycle:
                            codeCycles = [
                                int(x) for x in maCodeCycle.group(1).split(",")
                            ]
                            continue
                        for cycle in codeCycles:
                            townCode[cycle].append(line)
                    # --Evening/Night
                    elif section in ("evening", "night"):
                        cycle = {"evening": 3, "night": 4}[section]
                        line = reDef.sub(replDef, line)
                        chunks = [chunk.strip() for chunk in line.split(";")]
                        maSleep = reSleep.match(chunks[0])
                        if not maSleep:
                            continue
                        (cell, defaultState) = (
                            maSleep.group(2),
                            sleepStates[maSleep.group(1)],
                        )
                        cellStates = (defaultState,)
                        for chunk in chunks[1:]:
                            chunk = chunk.strip()
                            maSleep = reSleep.match(chunk)
                            if not maSleep or maSleep.group(1) == "=":
                                raise MoshError(
                                    _("Bad sleep condition state for %s in %s: %s")
                                    % (section, town, line)
                                )
                            condition, state = (
                                maSleep.group(2),
                                sleepStates[maSleep.group(1)],
                            )
                            condition = reIsMember.sub(r"getPCRank \1 >= 0", condition)
                            cellStates += ((condition, state),)
                        townSleep[cycle][cell] = cellStates
                    # --NPC
                    elif section == "npc":
                        # --Get Cycle
                        cycle = int(line[0])
                        rem = line[2:]
                        # --Repeater?
                        maRepeat = reRepeat.match(rem)
                        if maRepeat:
                            oldCycle = int(maRepeat.group(1))
                            npcSchedule[cycle - 1] = npcSchedule[oldCycle - 1]
                            continue
                        # --Replace defs
                        rem = reDef.sub(replDef, rem)
                        # --Cell
                        maCell = reCell.match(rem)
                        if not maCell:
                            raise MoshError(
                                _("Pos cell not defined for %s %s %d")
                                % (town, npc, cycle)
                            )
                        cell = maCell.group(1)
                        rem = rem[len(cell) :].strip()
                        # --Pos
                        maPos = rePos.match(rem)
                        coords = maPos.group(0).strip().split()
                        coords[-1] = (
                            f"{int(coords[-1])*57}"  # --Workaround interior rotation bug
                        )
                        pos = f"positionCell {' '.join(coords)} {cell}"
                        rem = rem[len(maPos.group(0)) :].strip()
                        # --Wander/Travel
                        ai = reWander.sub(r"wander \1 5 10  ", rem)
                        # --Save
                        npcSchedule[cycle - 1] = (pos, ai)

    def dumpText(self, fileName):
        """Write schedule to file."""
        with file(fileName, "w") as out:
            for town in sorted(self.towns):
                # --Header
                out.write("; " + town + " " + "=" * (76 - len(town)) + "\n")
                # --Cycle Scripts
                for cycle in [1, 2, 3, 4]:
                    out.write(self.getCycleScript(town, cycle))
                    out.write("\n")
                # --Master, cells scripts
                out.write(self.getSleepScript(town, 3))
                out.write("\n")
                out.write(self.getSleepScript(town, 4))
                out.write("\n")
                out.write(self.getMasterScript(town))
                out.write("\n")

    def save(self, fileInfo):
        """Add schedule scripts to esp."""
        fileRep = FileRep(fileInfo)
        fileRep.load(factory={"SCPT": Scpt, "DIAL": Dial, "INFO": Info})
        fileRep.unpackRecords({"SCPT"})
        fileRep.indexRecords({"SCPT"})

        # --Add scripts
        def setScript(id, code):
            script = fileRep.getRecord("SCPT", id, Scpt)
            script.setCode(code)

        for town in sorted(self.newTowns):
            # --Cycle Scripts
            for cycle in (1, 2, 3, 4):
                setScript("SC_%s_%d" % (town, cycle), self.getCycleScript(town, cycle))
            # --Master, sleep scripts
            for cycle in (3, 4):
                setScript("SC_%s_C%d" % (town, cycle), self.getSleepScript(town, cycle))
            setScript("SC_%s_Master" % (town,), self.getMasterScript(town))
        # --Reset Scripts
        if self.project:
            setScript("SC_%s_ResetGS" % (self.project,), self.getResetScript())
            setScript(
                "SC_%s_ResetStatesGS" % (self.project,), self.getResetStatesScript()
            )
        # --Add dialog scripts
        # --Find Hello entries
        recIndex = 0
        records = fileRep.records
        while recIndex < len(records):
            record = records[recIndex]
            recIndex += 1
            if isinstance(record, Dial):
                record.load(unpack=True)
                if record.type == 1 and record.id == "Hello":
                    break
        # --Sub scripts into hello entries
        reSCInit = re.compile(r"^;--SC_INIT: +(\w+)", re.M)
        while recIndex < len(records):
            record = records[recIndex]
            recIndex += 1
            if record.name != "INFO":
                break
            record.load(unpack=True)
            script = record.script
            if not script:
                continue
            maSCInit = reSCInit.search(script)
            # --No SCInit marker in script?
            if not maSCInit:
                continue
            town = maSCInit.group(1)
            # --SCInit for uncovered town?
            if town not in self.newTowns:
                continue
            # --Truncate script and add npc initializers
            script = script[: maSCInit.end()]
            for npc in sorted(self.schedule[town].keys()):
                script += '\r\nset SC_temp to "%s".nolore' % (npc,)
            script += "\r\nset SC_%s_State to -1" % (town,)
            script += '\r\n;messagebox "Initialized %s"' % (town,)
            # --Save changes
            record.script = winNewLines(script)
            record.setChanged()
        # --Done
        fileRep.sortRecords()
        fileRep.safeSave()

    def getResetScript(self):
        """Return SC_[Project]_ResetGS script."""
        if not self.project:
            raise StateError(_("No project has been defined!"))
        text = self.tsReset0.substitute(project=self.project)
        for town in sorted(self.schedule.keys()):
            text += self.tsReset1.substitute(town=town)
        text += self.tsReset2.substitute(project=self.project)
        return text

    def getResetStatesScript(self):
        """Return SC_[Project]_ResetStatesGS script."""
        if not self.project:
            raise StateError(_("No project has been defined!"))
        text = "begin SC_%s_ResetStatesGS\n" % (self.project,)
        text += ";--Sets state variables for %s project to zero.\n" % (self.project,)
        for town in sorted(self.schedule.keys()):
            text += "set SC_%s_State to 0\n" % (town,)
        text += "stopScript SC_%s_ResetStatesGS\nend\n" % (self.project,)
        return text

    def getMasterScript(self, town):
        """Return master script for town."""
        c3 = iff(self.sleep[town][3], "", ";")
        c4 = iff(self.sleep[town][4], "", ";")
        return self.tsMaster.substitute(town=town, c3=c3, c4=c4)

    def getSleepScript(self, town, cycle):
        """Return cells ("C") script for town, cycle."""
        out = cStringIO.StringIO()
        tcSleep = self.sleep[town][cycle]
        # --No cells defined?
        if len(tcSleep) == 0:
            out.write(self.tsSleep0.substitute(town=town, cycle=cycle))
        else:
            out.write(self.tsSleep1.substitute(town=town, cycle=cycle))
            # --Want to sort so that generic names are last. (E.g. "Vos" after "Vos, Chapel")
            #  But sort also needs to ignore leading and trailing quotes in cell string.
            #  So, compare trimmed cell string, and then reverse sort.
            for cell in sorted(tcSleep.keys(), key=lambda a: a[1:-1], reverse=True):
                cellStates = tcSleep[cell]
                defaultState = cellStates[0]
                out.write("elseif ( getPCCell %s )\n" % (cell,))
                if defaultState is None:
                    continue
                for count, (condition, state) in enumerate(cellStates[1:]):
                    ifString = ["if", "elseif"][count > 0]
                    out.write(
                        "\t%s ( %s )\n\t\tset SC_Sleep to %s\n"
                        % (ifString, condition, state)
                    )
                if len(cellStates) > 1:
                    out.write(
                        "\telse\n\t\tset SC_Sleep to %s\n\tendif\n" % (defaultState,)
                    )
                else:
                    out.write("\tset SC_Sleep to %s\n" % (defaultState,))
            out.write(self.tsSleep2.substitute(town=town, cycle=cycle))

        return out.getvalue()

    def getCycleScript(self, town, cycle):
        """Return cycle script for town, cycle."""
        # --Schedules
        reWanderCell = re.compile("wander[, ]+(\d+)", re.I)
        rePosCell = re.compile('positionCell +(\-?\d+) +(\-?\d+) +(\-?\d+).+"(.+)"')
        townCode = self.code.get(town, 0)
        townSchedule = self.schedule[town]
        npcs = sorted(townSchedule.keys())
        out = cStringIO.StringIO()
        cycleCode = ""
        if townCode:
            for line in townCode[0] + townCode[cycle]:
                cycleCode += "\t" + line + "\n"
        out.write(
            self.tsCycle1.substitute(town=town, cycle=f"{cycle}", cycleCode=cycleCode)
        )
        for npc in npcs:
            out.write(f'if ( "{npc}"->getDisabled )\n')
            out.write(f'elseif ( "{npc}"->getItemCount SC_offSchedule != 0 )\n')
            for condition, npcSchedule in townSchedule[npc]:
                if not condition:
                    out.write("else\n")
                else:
                    out.write(f"elseif ( {condition} )\n")
                (pos, ai) = npcSchedule[cycle - 1]
                out.write("\tif ( action < 20 )\n")
                out.write(f'\t\t"{npc}"->{pos}\n')
                if ai != "NOAI":
                    # --Wandering in exterior cell?
                    maWanderCell = reWanderCell.match(ai)
                    maPosCell = rePosCell.match(pos)
                    if (
                        maWanderCell
                        and (int(maWanderCell.group(1)) > 0)
                        and (maPosCell.group(4).find(",") == -1)
                    ):
                        xx, yy, zz, cell = maPosCell.groups()
                        out.write(f'\t\t"{npc}"->aiTravel {xx} {yy} {zz}\n')
                        out.write("\t\tset action to 10\n\telse\n")
                    out.write(f'\t\t"{npc}"->ai{ai}\n')
                out.write("\tendif\n")
            out.write("endif\n")
        out.write("if ( action != 10 )\n\tset action to 20\nendif\n")
        out.write("end\n")
        return out.getvalue()


# Initialization ------------------------------------------------------------------------ #
# -# First modified by D.C.-G. - Changed by Polemos to be an override.
# -#
# -# Avoiding error return on installers path creation not allowed.
# -# D.C.-G.: I implemented this because my installers directory is on a remote drive ;-)
# -# ==>> ONLY FOR WINDOWS
# -# Errors skipped:
# -#   * path not accessible physically (missing drive or unacceptable URL);
# -#   * the user does not have the rights to write in the destination folder.
# --------------------------------------------------------------------------------------- #


def defaultini():  # Polemos: The default ini.
    """Create mash_default.ini if none exists."""
    default_ini = (
        ";--This is the generic version of Mash.ini. If you want to set values here,\n"
        ';  then copy this to "mash.ini" and edit as desired.\n'
        ";Use mash.ini as an override when you need the Installers dir in a remote or relative location.\n"
        "[General]\n"
        ";--sInstallersDir is the Alternate root directory for installers, etc. You can\n"
        ";  use absolute path (c:\Games\Morrowind Mods) or relative path where the path\n"
        ";  is relative to Morrowind install directory.\n"
        "sInstallersDir=Installers ;--Default\n"
        ";sInstallersDir=..\Morrowind Mods\Installers ;--Alternate"
    )
    try:
        with io.open("mash_default.ini", "w", encoding="utf-8") as f:
            f.write(default_ini)
    except:
        pass


def DCGremote():  # Polemos just optimised to avoid code repeats.
    """Remote drive error skipping."""
    if sys.platform.lower().startswith("win"):
        drv, pth = os.path.splitdrive(dirs["installers"].s)
        if os.access(drv, os.R_OK):
            dirs["installers"].makedirs()


def initDirs():  # Polemos fixes, changes + OpenMW/TES3mp support
    """Init directories. Assume that settings has already been initialized."""
    if not settings["openmw"]:  # Regular Morrowind
        dirs["app"] = GPath(settings["mwDir"])
        dirs["mods"] = dirs["app"].join("Data Files")

        dirs["installers"] = GPath(settings["sInstallersDir"])
        DCGremote()
        # Polemos: Mash.ini produces more problems than benefits. Removed for now.
        """if GPath('mash.ini').exists():  # Mash.ini override
            mashini_read()
        else:
            dirs['installers'] = GPath(settings['sInstallersDir'])
            DCGremote()"""

    if settings["openmw"]:  # OpenMW/TES3mp support
        dirs["app"] = GPath(settings["openmwDir"])
        dirs["mods"] = GPath(settings["datamods"])
        dirs["installers"] = GPath(settings["downloads"])
        DCGremote()


def mashini_read():  # Polemos: Make mash.ini an override.
    """Read Mash.ini and get installers loc. It overrides settings.pkl"""
    # Polemos: Mash.ini produces more problems than benefits. Deactivated for now.
    defaultini()

    installers_set = settings["sInstallersDir"]
    mashIni = None

    if os.path.exists(os.path.join(MashDir, "mash.ini")):
        import ConfigParser

        mashIni = ConfigParser.ConfigParser()
        try:
            with io.open("mash.ini", "r", encoding="utf-8") as f:
                mashIni.readfp(f)
        except:
            pass

    if mashIni:
        if mashIni.has_option("General", "sInstallersDir"):
            installers = GPath(mashIni.get("General", "sInstallersDir").strip())
    else:
        installers = GPath(installers_set)

    if installers.isabs():
        dirs["installers"] = installers
    else:
        dirs["installers"] = dirs["app"].join(installers)

    DCGremote()


def initSettings(path="settings.pkl"):
    global settings
    settings = Settings(path)
    reWryeMash = re.compile("^wrye\.mash")
    for key in settings.data.keys():
        newKey = reWryeMash.sub("mash", key)
        if newKey != key:
            settings[newKey] = settings[key]
            del settings[key]
    settings.loadDefaults(settingDefaults)


# Main ------------------------------------------------------------------------ #
if __name__ == "__main__":
    print("Compiled")
# -*- coding: utf-8 -*-

# Wrye Mash Polemos fork GPL License and Copyright Notice ==============================
#
# This file is part of Wrye Mash Polemos fork.
#
# Wrye Mash, Polemos fork Copyright (C) 2017-2021 Polemos
# * based on code by Yacoby copyright (C) 2011-2016 Wrye Mash Fork Python version
# * based on code by Melchor copyright (C) 2009-2011 Wrye Mash WMSA
# * based on code by Wrye copyright (C) 2005-2009 Wrye Mash
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
#
#  Copyright on the original code 2005-2009 Wrye
#  Copyright on any non trivial modifications or substantial additions 2009-2011 Melchor
#  Copyright on any non trivial modifications or substantial additions 2011-2016 Yacoby
#  Copyright on any non trivial modifications or substantial additions 2017-2020 Polemos
#
# ======================================================================================

# Original Wrye Mash License and Copyright Notice ======================================
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# ========================================================================================

# File Structure ==============================================================
# Record Types/Order
# - Used for record sorting.
# - Order increment flags:
#   + increment order by 1
#   . don't increment order

recordTypes = """
TES3 +
GMST +
GLOB +
CLAS +
FACT +
RACE +
SOUN +
SKIL +
MGEF +
SCPT +
SSCR +
REGN +
BSGN +
LTEX +
SPEL +

ACTI +
ALCH +
APPA +
ARMO +
BODY +
BOOK +
CLOT +
CONT +
CREA +
DOOR +
ENCH +
INGR +
LEVC +
LEVI +
LIGH +
LOCK +
MISC +
NPC_ +
PROB +
REPA +
STAT +
WEAP +

CNTC +
CREC +
NPCC +

CELL +
LAND .
PGRD .
SNDG +
REFR +
DIAL +
INFO .

QUES +
JOUR +
KLST +
FMAP +
PCDT +
STLN +
GAME +
SPLM +
"""

# Installer
bethDataFiles = {
    "morrowind.esm",
    "tribunal.esm",
    "bloodmoon.esm",
    "morrowind.bsa",
    "tribunal.bsa",
    "bloodmoon.bsa",
}

# Game Info ===================================================================
# Skill Related

primaryAttributes = (
    "Agility",
    "Endurance",
    "Intelligence",
    "Personality",
    "Speed",
    "Strength",
    "Willpower",
    "Luck",
)

combatSkills = (
    "Armorer",
    "Athletics",
    "Axe",
    "Block",
    "Blunt Weapon",
    "Heavy Armor",
    "Long Blade",
    "Medium Armor",
    "Spear",
)

magicSkills = (
    "Alchemy",
    "Alteration",
    "Conjuration",
    "Destruction",
    "Enchant",
    "Illusion",
    "Mysticism",
    "Restoration",
    "Unarmored",
)

stealthSkills = (
    "Acrobatics",
    "Hand To Hand",
    "Light Armor",
    "Marksman",
    "Mercantile",
    "Security",
    "Short Blade",
    "Sneak",
    "Speechcraft",
)

# Wrye Level Set ==============================================================
charSet0 = """begin wr_lev${className}GS
short action
short stemp
short level

if ( menuMode )
  return

elseif ( action == 0 ) ;--Initialize
  set level to wr_lev${className}
  set action to 10
  return

elseif ( action == 10 ) ;--Option Menu
  messagebox "Choose the Way of the ${className} [level %g]?" level "Yes" "+5" "+1" "-1" "-5" "No"
  set action to 20
  return

elseif ( action == 20 ) ;--Option selected
  set stemp to getButtonPressed
  if ( stemp == -1 ) ;--Not pressed yet
  elseif ( stemp == 0 ) ; Do it
     set action to 30
  elseif ( stemp == 1 ) ; +5
    if ( level < 96 )
      set level to level + 5
      set action to 10
    endif
  elseif ( stemp == 2 ) ;+1
    if ( level < 100 )
      set level to level + 1
      set action to 10
    endif
  elseif ( stemp == 3 ) ;-1
    if ( level > 1 )
      set level to level - 1
      set action to 10
    endif
  elseif ( stemp == 4 ) ;-5
    if ( level > 5 )
      set level to level - 5
      set action to 10
    endif
  elseif ( stemp == 5 ) ;--Cancel
    set action to 100
  endif
  return

elseif ( action == 30 ) ;--Do it
  ;--Fall through

elseif ( action == 100 ) ;--Terminate
  set action to 0
  stopScript wr_lev${className}GS
  return
endif

;--Levels
set wr_lev${className} to level
set wr_levSetLevelGS.level to level
startScript wr_levSetLevelGS

;--Cap stats at level 30
if ( level > 30 )
  set level to 30
endif
"""

charSet1 = """messagebox "You now follow the Way of the ${className}, level %g." level
playSound skillraise
set action to 100
end"""

# Library Generator ===========================================================
# Templates
libGenMain = """begin ${libId}LS
short disabled
short action

if ( onActivate )
    if ( menuMode == 0 )
        activate
    endif
    return  
elseif ( action != lib_action )
    ;pass
elseif ( disabled != ${libId}G )
    return
elseif ( ${libId}G )
    set disabled to 0
    enable
    return
else
    set disabled to 1
    disable
    return
endif

;--Action changed...
if ( lib_action != 1 )
elseif ( ${libId}G )
elseif ( player->getItemCount "${srcId}" )
    set lib_actionCount to lib_actionCount + 1
    set ${libId}G to 1
${ifAltId}endif
set action to lib_action

end"""

libGenIfAltId = """elseif ( player->getItemCount "${altId}" )
    set lib_actionCount to lib_actionCount + 1
    set ${libId}G to 1
"""

# Scheduling ==================================================================
# Templates

# --Master
scheduleMaster = """begin SC_${town}_Master
dontSaveObject
if ( menuMode )
	return
elseif ( cellChanged )
	set SC_offScheduleG to 0
elseif ( SC_${town}_State == 0 )
	return
elseif ( SC_Reschedule )
	set SC_${town}_State to -1
	set SC_Reschedule to 0
elseif ( gamehour < 7 )
	if ( SC_${town}_State != 4 )
    	set SC_Reschedule to 0
		set SC_${town}_State to 4
		startScript SC_${town}_4
	endif
	${c4}startScript SC_${town}_C4
	return
elseif ( gamehour < 12 )
	if ( SC_${town}_State != 1 )
    	set SC_Reschedule to 0
		set SC_${town}_State to 1
		startScript SC_${town}_1
	endif
	return
elseif ( gamehour < 19 )
	if ( SC_${town}_State != 2 )
    	set SC_Reschedule to 0
		set SC_${town}_State to 2
		startScript SC_${town}_2
	endif
	return
else
	if ( SC_${town}_State != 3 )
    	set SC_Reschedule to 0
		set SC_${town}_State to 3
		startScript SC_${town}_3
	endif
	${c3}startScript SC_${town}_C3
	return
endif
end
"""

# --Cycle
scheduleCycle1 = """begin SC_${town}_${cycle}
short action
float timer
if ( action == 0 ) ;--First pass
elseif ( action == 20 ) ;--Terminate
	set action to 0
	set timer to 0
	stopScript SC_${town}_${cycle}
	return
;--Action == 10
elseif ( SC_${town}_State != ${cycle} )
	set action to 20
	return
elseif ( getInterior )
	return
elseif ( timer < 0.5 )
	set timer to timer + getSecondsPassed
	return
else ;--Second Pass
	set action to 20
endif

if ( action == 0 )
	;messagebox "Starting SC_${town}_${cycle}"
	if ( SC_PlayBells )
		 playSound "SC_ScheduleSND"
	endif
${cycleCode}endif

"""

# --Sleep
scheduleSleep0 = """begin SC_${town}_C${cycle}
;--Null sleep script. Should never be run, but just in case...
if ( cellChanged )
	set SC_Sleep to 0
	stopScript SC_${town}_C${cycle}
endif
end
"""

scheduleSleep1 = """begin SC_${town}_C${cycle}
short prevState

if ( prevState != SC_${town}_State )
	set prevState to SC_${town}_State
	;Fall through
elseif ( cellChanged == 0 )
	return
endif

if ( SC_${town}_State != ${cycle} )
	set SC_Sleep to 0
	stopScript SC_${town}_C${cycle}
"""

scheduleSleep2 = """else
	set SC_Sleep to 0
	stopScript SC_${town}_C${cycle}
endif
end
"""

# --Reset
scheduleReset0 = """begin SC_${project}_ResetGS
;--Resets schedules to morning schedule for all towns.
float timer
short playBells
set playBells to SC_PlayBells
set SC_PlayBells to 0
if ( timer < 0 )
    set timer to timer + getSecondsPassed
    return
endif
"""

scheduleReset1 = """if ( SC_${town}_State > 0 )
    messagebox "Resetting $town..."
    startScript SC_${town}_1
    set timer to -2.0
endif
"""

scheduleReset2 = """messagebox "All towns reset."
set SC_PlayBells to playBells
stopScript SC_${project}_ResetGS
end"""

# Defs
scheduleDefs = """
#--Misc
stand: wander 0

#--Idles
#     stand still
#     0  shift legs
#     0  0  look behind
#     0  0  0  scratch head
#     0  0  0  0  shift clothes; hf: hands on hip
#     0  0  0  0  0  yawn
#     0  0  0  0  0  0  fingers, look around
#     0  0  0  0  0  0  0  hands to chest
#     0  0  0  0  0  0  0  0  weapon, touch head; kf: scratch head
#     0  0  0  0  0  0  0  0  0
s01:  0  5 20 40 15 60  0 10
s02:  0 15 15 20 10 40  0 25

i00:  0  5  5  5 10 10
i10:  0 10 60 20 10 10 
i30:  0 30 10 10 
i31:  0 30 20 30 30  0 15 15 # fidget/heartburn
i40:  0 40 20 10 10
i40a: 0 40 20 10 10  0 20 # fidget
i41:  0 40 20 10 10 10
i42:  0 40 20 20 10
i43:  0 40 20 20 10 10
i43a: 0 40 20 10 10  0 40 # heartburn
i44:  0 40 30 30 10
i45:  0 40 40 40 10
i46:  0 40 40 40 10 10  0 10
i50:  0 50 20 20 10
i50a: 0 50 20 10 10  0  0 10
i51:  0 50 20 20 20 10
i52:  0 50 30 30 20 10
i53:  0 50 50 10 10

i60:  0 60 20 10
i61:  0 60 20 10  0 10
i62:  0 60 20 10 10
i62a: 0 60 20 10 10  0 10
i63:  0 60 20 10 10  0  0 10 
i63a: 0 60 20 10 10  0  0 10 10 #heart/weaps
i63b: 0 60 20 10 10  0  0  0 10 #weap
i64:  0 60 20 10 10 10 
i65:  0 60 20 20 10
i65a: 0 60 20 20 20
i66:  0 60 20 20 10 10
i67:  0 60 20 20 10 10 10
i68:  0 60 20 20 20 10
i69:  0 60 20 20 20 10 10 10

i70:  0 60 30 10 10
i71:  0 60 30 30 10
i72:  0 60 30 30 10 10
i74:  0 60 30 30 10 10 10

i80:  0 60 40 30 20 10 10
i81:  0 60 40 40 10 10
i82:  0 60 40 40 20 10 10

i90:  0 60 60 10 10
i91:  0 60 60 100 10
"""
# -*- coding: utf-8 -*-

# Wrye Mash Polemos fork GPL License and Copyright Notice ==============================
#
# Wrye Mash, Polemos fork Copyright (C) 2017-2021 Polemos
# * based on code by Yacoby copyright (C) 2011-2016 Wrye Mash Fork Python version
# * based on code by Melchor copyright (C) 2009-2011 Wrye Mash WMSA
# * based on code by Wrye copyright (C) 2005-2009 Wrye Mash
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
#
#  Copyright on the original code 2005-2009 Wrye
#  Copyright on any non trivial modifications or substantial additions 2009-2011 Melchor
#  Copyright on any non trivial modifications or substantial additions 2011-2016 Yacoby
#  Copyright on any non trivial modifications or substantial additions 2017-2020 Polemos
#
# ======================================================================================

# GPL License and Copyright Notice ============================================
#
#  Wrye Bolt is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bolt; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Bolt copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# =============================================================================


import cPickle
from unimash import _  # Polemos
import os
import re
import shutil
import struct
import sys
import time
from types import *
from zlib import crc32
import io, stat, scandir, ushlex, thread, xxhash  # Polemos
from subprocess import PIPE, check_call  # Polemos: KEEP => check_call <= !!
from sfix import Popen  # Polemos
import compat

# Exceptions
from merrors import mError as BoltError
from merrors import (
    AbstractError as AbstractError,
    ArgumentError as ArgumentError,
    StateError as StateError,
)
from merrors import UncodedError as UncodedError, ConfError as ConfError


# Constants
MashDir = os.path.dirname(sys.argv[0])
DETACHED_PROCESS = 0x00000008  # Polemos: No console window.
_gpaths = {}

# LowStrings


class LString(object):
    """Strings that compare as lower case strings."""

    __slots__ = ("_s", "_cs")

    def __init__(self, s):
        if isinstance(s, LString):
            s = s._s
        self._s = s
        self._cs = s.lower()

    def __getstate__(self):
        """Used by pickler. _cs is redundant,so don't include."""
        return self._s

    def __setstate__(self, s):
        """Used by unpickler. Reconstruct _cs."""
        self._s = s
        self._cs = s.lower()

    def __len__(self):
        return len(self._s)

    def __str__(self):
        return self._s

    def __repr__(self):
        return "bolt.LString(%s)" % repr(self._s)

    def __add__(self, other):
        return LString(self._s + other)

    def __hash__(self):
        """Hash"""
        return hash(self._cs)

    def __cmp__(self, other):
        """Compare"""
        if isinstance(other, LString):
            return cmp(self._cs, other._cs)
        else:
            return cmp(self._cs, other.lower())


# Paths ----------------------------------------------------------------------- #


def GPath(name):
    """Returns common path object for specified name/path."""
    if name is None:
        return None
    elif not name:
        norm = name
    elif isinstance(name, Path):
        norm = name._s
    else:
        norm = os.path.normpath(name)
    path = _gpaths.get(norm)
    if path is not None:
        return path
    else:
        return _gpaths.setdefault(norm, Path(norm))


class Path(object):  # Polemos: Unicode fixes.
    """A file path. May be just a directory, filename or full path.
    Paths are immutable objects that represent file directory paths."""

    # --Class Vars/Methods
    norm_path = {}  # --Dictionary of paths
    mtimeResets = []  # --Used by getmtime

    @staticmethod
    def get(name):
        """Returns path object for specified name/path."""
        name.encode("utf-8")
        if isinstance(name, Path):
            norm = name._s
        else:
            norm = os.path.normpath(name)
        return Path.norm_path.setdefault(norm, Path(norm))

    @staticmethod
    def getNorm(name):  # Sharlikran's commit for Python 2.7.8
        """Return the normpath for specified name/path object."""
        if isinstance(name, Path):
            return name._s
        elif not name:
            return name
        else:
            return os.path.normpath(name)

    @staticmethod
    def getCase(name):
        """Return the normpath+normcase for specified name/path object."""
        if not name:
            return name
        if isinstance(name, Path):
            return name._cs
        else:
            return os.path.normcase(os.path.normpath(name))

    @staticmethod
    def getcwd():
        return Path(os.getcwd().encode("utf-8"))

    def setcwd(self):
        """Set cwd. Works as either instance or class method."""
        if isinstance(self, Path):
            dir = self._s.encode("utf-8")
        else:
            dir = self
        os.chdir(dir)

    # --Instance stuff --------------------------------------------------
    # --Slots: _s is normalized path. All other slots are just pre-calced variations of it.
    __slots__ = ("_s", "_cs", "_csroot", "_sroot", "_shead", "_stail", "_ext", "_cext")

    def __init__(self, name):
        """Initialize."""
        if isinstance(name, Path):
            self.__setstate__(name._s)
        elif type(name) is unicode:
            self.__setstate__(name)
        else:
            self.__setstate__(str(name))

    def __getstate__(self):
        """Used by pickler. _cs is redundant,so don't include."""
        return self._s

    def __setstate__(self, norm):
        """Used by unpickler. Reconstruct _cs."""
        self._s = norm
        self._cs = os.path.normcase(norm)
        self._sroot, self._ext = os.path.splitext(norm)
        self._shead, self._stail = os.path.split(norm)
        self._cext = os.path.normcase(self._ext)
        self._csroot = os.path.normcase(self._sroot)

    def __len__(self):
        return len(self._s)

    def __repr__(self):
        # return "bolt.Path(%s)" % `self._s`
        return f"bolt.Path({self._s})"

    # --Properties--------------------------------------------------------
    # --String/unicode versions.
    @property
    def s(self):
        """Path as string."""
        return self._s

    @property
    def cs(self):
        """Path as string in normalized case."""
        return self._cs

    @property
    def csroot(self):
        """Root as string."""
        return self._csroot

    @property
    def sroot(self):
        """Root as string."""
        return self._sroot

    @property
    def shead(self):
        """Head as string."""
        return self._shead

    @property
    def stail(self):
        """Tail as string."""
        return self._stail

    # --Head, tail
    @property
    def headTail(self):
        """For alpha\beta.gamma returns (alpha,beta.gamma)"""
        return map(GPath, (self._shead, self._stail))

    @property
    def head(self):
        """For alpha\beta.gamma, returns alpha."""
        return GPath(self._shead)

    @property
    def tail(self):
        """For alpha\beta.gamma, returns beta.gamma."""
        return GPath(self._stail)

    # --Root, ext
    @property
    def rootExt(self):
        return (GPath(self._sroot), self._ext)

    @property
    def root(self):
        """For alpha\beta.gamma returns alpha\beta"""
        return GPath(self._sroot)

    @property
    def ext(self):
        """Extension (including leading period, e.g. '.txt')."""
        return self._ext

    @property
    def cext(self):
        """Extension in normalized case."""
        return self._cext

    @property
    def temp(self):
        """Temp file path.."""
        return self + ".tmp"

    @property
    def backup(self):
        """Backup file path."""
        return self + ".bak"

    # --size, atim, ctime
    @property
    def size(self):  # Polemos: os.path.getsize -> os.stat().st_size
        """Size of file."""
        return os.stat(self._s).st_size

    @property
    def atime(self):
        return os.path.getatime(self._s)

    @property
    def ctime(self):
        return os.path.getctime(self._s)

    def getmtime(
        self,
    ):  #  Polemos: Does the Y2038 bug still exist in Python 2.7.15? Todo: Check for Y2038 bug.
        """Returns mtime for path. But if mtime is outside of epoch, then resets mtime to an in-epoch date and uses that."""
        mtime = int(os.path.getmtime(self._s))
        # --Y2038 bug? (os.path.getmtime() can't handle years over unix epoch)
        if mtime <= 0:
            import random

            # --Kludge mtime to a random time within 10 days of 1/1/2037
            mtime = time.mktime((2037, 1, 1, 0, 0, 0, 3, 1, 0))
            mtime += random.randint(0, 10 * 24 * 60 * 60)  # --10 days in seconds
            self.mtime = mtime
            Path.mtimeResets.append(self)
        return mtime

    def setmtime(self, mtime):
        os.utime(self._s, (self.atime, int(mtime)))

    mtime = property(getmtime, setmtime, doc="Time file was last modified.")

    @property
    def xxh(self):  # Polemos
        """Calculates and returns xxhash value for self."""
        xxhs = xxhash.xxh32()
        with self.open("rb", 65536) as ins:
            for x in xrange((self.size / 65536) + 1):
                xxhs.update(ins.read(65536))
        return xxhs.intdigest()

    @property
    def crc(
        self,
    ):  # Polemos: Optimized. It went from 23 sec to 6 sec in a 6700k system.
        """Calculates and returns crc value for self."""
        if conf.settings["advanced.7zipcrc32b"] and self.size > 16777216:
            #  7z is faster on big files
            args = ushlex.split('7z.exe h "%s"' % self.s)
            ins = Popen(args, bufsize=-1, stdout=PIPE, creationflags=DETACHED_PROCESS)
            return int([x for x in ins.stdout][14].split(":")[1], 16)
        # crc = 0L
        crc = 0
        with self.open("rb", 65536) as ins:
            for x in xrange((self.size / 65536) + 1):
                crc = crc32(ins.read(65536), crc)
        # return crc if crc > 0 else 4294967296L + crc
        return crc if crc > 0 else 4294967296 + crc

    # --Path stuff -------------------------------------------------------
    # --New Paths, subpaths
    def __add__(self, other):
        return GPath(self._s + Path.getNorm(other))

    def join(*args):
        norms = [Path.getNorm(x) for x in args]
        return GPath(os.path.join(*norms))

    def list(self):
        """For directory: Returns list of files."""
        if not os.path.exists(self._s):
            return []
        return [GPath(x) for x in scandir.listdir(self._s)]  # Pol: Seems better.

    def walk(self, topdown=True, onerror=None, relative=False):
        """Like os.walk."""
        if relative:
            start = len(self._s)
            return (
                (GPath(x[start:]), [GPath(u) for u in y], [GPath(u) for u in z])
                for x, y, z in scandir.walk(topdown, onerror)
            )  # Polemos: replaced os.walk which is slow in Python 2.7 and below.
        else:
            return (
                (GPath(x), [GPath(u) for u in y], [GPath(u) for u in z])
                for x, y, z in scandir.walk(topdown, onerror)
            )  # See above.

    # --File system info
    # --THESE REALLY OUGHT TO BE PROPERTIES.
    def exists(self):
        return os.path.exists(self._s)

    def isdir(self):
        return os.path.isdir(self._s)

    def isfile(self):
        return os.path.isfile(self._s)

    def isabs(self):
        return os.path.isabs(self._s)

    # --File system manipulation
    def open(self, *args):
        """Open a file function."""
        if self._shead and not os.path.exists(self._shead):
            os.makedirs(self._shead)
        return open(self._s, *args)

    def parsePath(self):  # Polemos
        """Return a file path."""
        if self._shead and not os.path.exists(self._shead):
            os.makedirs(self._shead)
        return self._s

    def codecs_open(self, *args):  # Polemos
        """Open a unicode file function."""
        if self._shead and not os.path.exists(self._shead):
            os.makedirs(self._shead)
        return io.open(self._s, *args, encoding="utf-8")

    def makedirs(self):
        """Create dir function."""
        if not self.exists():
            os.makedirs(self._s)

    def remove(self):  # Polemos fix
        """Remove function."""
        if self.exists():
            try:
                os.remove(self._s)
            except:
                self.undeny(self._s, action="os.remove")

    def removedirs(self):
        """Remove dir function."""
        if self.exists():
            os.removedirs(self._s)

    def rmtree(
        self, safety="PART OF DIRECTORY NAME"
    ):  # Polemos fix: shutil.rmtree has a bug in 2.7. Delay to try to bypass.
        """Removes directory tree. As a safety factor, a part of the directory name must be supplied."""
        if self.isdir() and safety and safety.lower() in self._cs:
            for x in range(3):  # Drizzt tries.
                try:
                    shutil.rmtree(self._s, onerror=self.undeny_1err)
                    break
                except OSError:
                    time.sleep(2)
            # if self.isdir(): self.message_po((u'Error: Access denied.\n\nCannot delete %s.' % (self._s))) #
            # Polemos: Looks nice to have, ain't it? Don't try it, seriously don't.                         #

    # --start, move, copy, touch, untemp
    def start(self):  # Polemos fix
        """Starts file as if it had been double clicked in file explorer."""
        try:
            os.startfile(self._s)
        except:
            pass  # Todo: Add a msg to inform user

    def copyTo(self, destName):  # Polemos fix
        """Copy function."""
        destName = GPath(destName)
        if self.isdir():
            shutil.copytree(self._s, destName._s)
        else:
            if destName._shead and not os.path.exists(destName._shead):
                os.makedirs(destName._shead)
            try:
                shutil.copyfile(self._s, destName._s)
            except:
                pass
            destName.mtime = self.mtime

    def renameTo(self, destName):  # Polemos
        """Rename function."""
        destName = GPath(destName)
        try:
            os.rename(self._s, destName._s)
        except:
            return False
        if not self.isdir():
            try:
                destName.mtime = self.mtime
            except:
                pass
        return True

    def moveTo(self, destName):  # Polemos fix
        """Move function."""
        destPath = GPath(destName)
        if destPath._cs == self._cs:
            return
        if destPath._shead and not os.path.exists(destPath._shead):
            os.makedirs((destPath._shead))
        elif destPath.exists():
            try:
                os.remove(destPath._s)
            except:
                self.undeny(destPath._s, action="os.remove")
        try:
            shutil.move(self._s, destPath._s)
        except:
            pass

    def touch(self):
        """Like unix 'touch' command. Creates a file with current date/time."""
        if self.exists():
            self.mtime = time.time()
        else:
            self.temp.open("w").close()
            self.untemp()

    def untemp(self, doBackup=False):  # Polemos fix
        """Replaces file with temp version, optionally making backup of file first."""
        if self.exists():
            if doBackup:
                self.backup.remove()
                shutil.move(self._s, self.backup._s)
            else:
                try:
                    os.remove(self._s)
                except:
                    self.undeny(self._s, action="os.remove")
        shutil.move(self.temp._s, self._s)

    def message_po(self, message=None):  # Polemos:  Not implemented.
        """Custom messaging."""
        import gui.dialog

        if message is None:
            message = _(
                "Errors occurred during file operations.\nTry running Wrye Mash with Admin rights."
            )
        gui.dialog.ErrorMessage(None, _(message))
        return

    def undeny(self, path, destdir=None, action=None):  # Polemos.
        """Remove Read only attribute."""

        def write_on(path):
            try:
                os.chmod(path, stat.S_IWRITE)  # Part pythonic,
            # except: check_call(ur'attrib -R %s /S' % (path))  # part hackish (Yeah I know).
            except:
                check_call(f"attrib -R {path} /S")  # part hackish (Yeah I know).

        try:
            write_on(path)
            if action is None:
                return
            elif action == "os.remove":
                os.remove(path)
            elif action == "shutil.move":
                shutil.move(path, destdir)  # Not implemented.
        except:
            pass  # self.message_po(_(u'Error: Access denied.\nTry running Wrye Mash with Admin rights.')) #
            # Polemos: Nope, nope... nope...                                                         #

    def undeny_1err(self, func, path, _):  # Polemos
        """Remove readonly, and retry..."""
        os.chmod(path, stat.S_IWRITE)
        func(path)

    # Polemos: Special Methods Magic from Wrye Bash 307 Beta2.
    # --Hash/Compare, based on the _cs attribute so case insensitive. NB: Paths
    # directly compare to basestring and Path and will blow for anything else
    def __hash__(self):
        return hash(self._cs)

    def __eq__(self, other):
        if isinstance(other, Path):
            return self._cs == other._cs
        else:
            return self._cs == Path.getCase(other)

    def __ne__(self, other):
        if isinstance(other, Path):
            return self._cs != other._cs
        else:
            return self._cs != Path.getCase(other)

    def __lt__(self, other):
        if isinstance(other, Path):
            return self._cs < other._cs
        else:
            return self._cs < Path.getCase(other)

    def __ge__(self, other):
        if isinstance(other, Path):
            return self._cs >= other._cs
        else:
            return self._cs >= Path.getCase(other)

    def __gt__(self, other):
        if isinstance(other, Path):
            return self._cs > other._cs
        else:
            return self._cs > Path.getCase(other)

    def __le__(self, other):
        if isinstance(other, Path):
            return self._cs <= other._cs
        else:
            return self._cs <= Path.getCase(other)


# Util Constants --------------------------------------------------------------
# --Unix new lines
reUnixNewLine = re.compile(r"(?<!\r)\n")

# Util Classes ----------------------------------------------------------------


class CsvReader:
    """For reading csv files. Handles both command tab separated (excel) formats."""

    def __init__(self, path):
        import csv

        self.ins = path.open("rb")
        format = ("excel", "excel-tab")["\t" in self.ins.readline()]
        self.ins.seek(0)
        self.reader = csv.reader(self.ins, format)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next()

    def close(self):
        self.reader = None
        self.ins.close()


# ------------------------------------------------------------------------------


class DataDict:
    """Mixin class that handles dictionary emulation, assuming that dictionary has the 'data' attribute."""

    def __contains__(self, key):
        return key in self.data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def setdefault(self, key, default):  # Polemos fix
        return self.data.setdefault(key, default)

    def keys(self):
        return self.data.keys()

    def values(self):
        return self.data.values()

    def items(self):
        return self.data.items()

    def has_key(self, key):
        return self.data.has_key(key)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def pop(self, key, default=None):
        return self.data.pop(key, default)

    def iteritems(self):
        return self.data.iteritems()

    def iterkeys(self):
        return self.data.iterkeys()

    def itervalues(self):
        return self.data.itervalues()


# ------------------------------------------------------------------------------


class RemoveTree:  # Polemos
    """FileTree removal actions."""

    def __init__(self, tree):
        """Init."""
        if any([type(tree) is str, type(tree) is unicode]):
            tree = (tree,)
        self.rmTree(tree)

    def undeny(self, func, path, _):
        """Remove readonly, and retry..."""
        try:
            os.chmod(path, stat.S_IWRITE)
            func(path)
        except:
            pass

    def rmTree(self, tree):
        """Remove Tree."""
        for branch in tree:
            if branch == "\\":
                break  # Polemos: You never know.
            if os.path.isdir(branch):
                for tries in range(3):
                    try:
                        shutil.rmtree(branch, onerror=self.undeny)
                        break
                    except:
                        time.sleep(2)


# ------------------------------------------------------------------------------


class MetaStamp:  # Polemos
    """Metafile creation."""

    def __init__(self, target_dir, package_name_data):
        """Init."""
        self.target_dir = target_dir
        self.metafile = os.path.join(target_dir, "mashmeta.inf")
        self.Installer = package_name_data[2]
        self.Version = "" if not package_name_data[4] else package_name_data[4]
        self.Repo = "Nexus" if package_name_data[3] else ""
        self.ID = package_name_data[3]
        self.MetaCreate()

    def MetaCreate(self):
        """Create mod metafile."""
        metatext = (
            "[General]",
            "Installer=%s" % self.Installer,
            "Version=%s" % self.Version,
            "NoUpdateVer=",
            "NewVersion=",
            "Category=",
            "Repo=%s" % self.Repo,
            "ID=%s" % self.ID,
        )
        tries = 0
        while tries != 3:
            if os.path.isfile(self.metafile):
                break
            try:
                with io.open(self.metafile, "w", encoding="utf-8") as f:
                    f.write("\r\n".join(metatext))
            except:
                tries += 1
                time.sleep(0.3)


# ------------------------------------------------------------------------------


class MetaParse:  # Polemos
    """Metafile parsing."""

    Data = []

    def __init__(self, metadir):
        """Init."""
        metafile = os.path.join(metadir, "mashmeta.inf")
        if not os.path.isfile(metafile):
            return
        self.Data = self.MetaRead(metafile)

    def metaScan(self, metafile):
        """Read metafile contents."""
        with io.open(metafile, "r", encoding="utf-8") as f:
            return f.readlines()

    def MetaRead(self, metafile):
        """Parse mod metafile."""
        data = {
            "Installer": "",
            "Version": "",
            "NoUpdateVer": "",
            "NewVersion": "",
            "Category": "",
            "Repo": "",
            "ID": "",
        }
        reList = re.compile(
            "(Installer|Version|NoUpdateVer|NewVersion|Category|Repo|ID)=(.+)"
        )
        metadata = self.metaScan(metafile)[:]
        # Main
        for x in metadata:
            x = x.rstrip()
            maList = reList.match(x)
            if maList:
                key, value = maList.groups()
                if key == "Installer":
                    data[key] = value
                elif key == "Version":
                    data[key] = value
                elif key == "NoUpdateVer":
                    data[key] = value
                elif key == "NewVersion":
                    data[key] = value
                elif key == "Category":
                    data[key] = value
                elif key == "Repo":
                    data[key] = value
                elif key == "ID":
                    data[key] = value
        return data


# ------------------------------------------------------------------------------


class ModInstall:  # Polemos
    """File tree manipulations (OpenMW)."""

    def __init__(self, parent, mod_name, modsfolder, source_dir, target_dir, filesLen):
        """Init."""
        self.parent = parent
        self.mod_name = mod_name
        self.modsfolder = modsfolder
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.filesLen = filesLen
        self.chkStatus()

    def doAction(self):
        """Set action route."""
        if self.actionData[0]:  # Backup existing mod
            if not self.backup():
                return
        if self.actionData[1] != self.mod_name:  # Rename mod
            if self.actionData[1] == "":
                self.error("rename")
                return
            self.mod_name = self.actionData[1]
            self.target_dir = os.path.join(self.modsfolder, self.mod_name)
            self.doAction()
            return
        if self.actionData[2] == "rename":
            self.simpleInstall()
        if self.actionData[2] == "overwrite":
            self.overwrite()
        if self.actionData[2] == "replace":
            self.replace()

    def error(self, error):
        """Notify user of errors."""
        import gui.dialog as gui

        if error == "backup":
            msg = _(
                "Error: Unable to backup existing mod folder!!!\n\nInstallation was aborted, no actions were taken."
            )
        elif error == "install":
            msg = _(
                "Error: Could not finish installation!!!\n\nInstallation was aborted."
            )
        elif error == "rename":
            msg = _(
                "Error: An invalid mod name was supplied!!!\n\nInstallation was aborted, no actions were taken."
            )
        elif error == "overwrite":
            msg = _("Error: Unable to merge mods!!!\n\nInstallation was aborted.")
        elif error == "replace":
            msg = _(
                "Error: Unable to delete existing mod folder!!!\n\nInstallation was aborted."
            )
        gui.ErrorMessage(self.parent, msg)

    def chkStatus(self):
        """Check folder conditions."""
        if os.path.isdir(self.target_dir):
            self.showgui()
            return
        self.simpleInstall()

    def simpleInstall(self):
        """Simple Installation."""
        try:
            self.copyMod()
        except:
            self.error("install")

    def copyMod(self, source_dir=None, target_dir=None):
        """Multithread Copy ops."""
        import gui.dialog as gui

        if source_dir is not None:
            self.source_dir = source_dir
        if target_dir is not None:
            self.target_dir = target_dir
        self.dialog = gui.GaugeDialog(
            self.parent, title=_("Installing..."), max=self.filesLen
        )
        self.dialog.set_msg(_("Installing..."))
        self.progress()  # todo: make modal
        thread.start_new_thread(self.treeOp, ("treeOpThread",))

    def treeOp(self, id):
        """Files/Folders operations."""
        source_dir = self.source_dir
        target_dir = self.target_dir
        if not os.path.isdir(self.target_dir):
            os.makedirs(self.target_dir)
        for root, dirsn, files in scandir.walk(source_dir, topdown=False):
            for num, fname in enumerate(files, 1):
                self.dialog.update(num)
                relsource = os.path.relpath(root, source_dir)
                if relsource == ".":
                    relsource = ""
                source = os.path.join(root, fname)
                target = os.path.join(target_dir, relsource, fname)
                target_file_dir = os.path.join(target_dir, relsource)
                if not os.path.isdir(target_file_dir):
                    os.makedirs(target_file_dir)
                buffer = min(10485760, os.path.getsize(source))
                if buffer == 0:
                    buffer = 1024
                with open(source, "rb") as fsource:
                    with open(target, "wb") as fdest:
                        shutil.copyfileobj(fsource, fdest, buffer)
                try:
                    os.remove(source)
                except:
                    pass
            try:
                os.rmdir(root)
            except:
                pass
        self.dialog.update(self.filesLen)
        self.dialog.set_msg(_("Finished..."))
        time.sleep(2)  # Give some time for system file caching.
        self.dialog.Destroy()

    def progress(self):
        """Progress indicator."""
        self.dialog.Show()

    def overwrite(self):
        """Merge folders."""
        try:
            self.copyMod()
        except:
            self.error("overwrite")

    def replace(self):
        """Replace folder."""

        def undeny(func, path, _):
            try:
                os.chmod(path, stat.S_IWRITE)
                func(path)
            except:
                os.system(r'attrib -R "%s" /S' % path)

        try:
            shutil.rmtree(self.target_dir, onerror=undeny)
        except:
            self.error("replace")
        self.simpleInstall()

    def backup(self):
        """Make a backup of old dir."""
        try:
            ID = 0
            while True:
                if ID == 0:
                    ID = ""
                NewDirName = "%s%s%s" % (self.target_dir, "backup", ID)
                if not os.path.isdir(NewDirName):
                    if self.actionData[2] == "replace":
                        os.rename(self.target_dir, NewDirName)
                    elif self.actionData[2] == "overwrite":
                        self.copyMod(self.target_dir, NewDirName)
                    break
                if not ID:
                    ID = 0
                ID += 1
        except:
            self.error("backup")
            return False
        return True

    def showgui(self):
        """Dialog processor."""
        import gui.dialog as gui

        self.actionData = gui.ConflictDialog(self.parent, self.mod_name).GetData
        if not self.actionData:
            return
        if self.actionData[2] == "rename":
            if os.path.isdir(os.path.join(self.modsfolder, self.actionData[1])):
                self.showgui()
                return
        self.doAction()


# ------------------------------------------------------------------------------


class ModNameFactory:  # Polemos
    """Extract info from modname (if any) and return Mod Name data."""

    getModName = []

    def __init__(self, mod):
        """Init."""
        self.mod = mod
        self.factory()

    def cleanPath(self, mod):
        """Remove file path."""
        return os.path.basename(mod.lower().rstrip("\\"))

    def cleanExt(self, mod):
        """Remove extension."""
        exts = [".7z", ".zip", ".rar"]
        for num, ext in enumerate(exts):
            if mod.lower().endswith(ext):
                return mod.rstrip(ext)

    def getNexus(self, mod):
        """Get Nexus info from mod."""
        modparts = mod.split("-")
        modNexus, modName = False, False
        for part in modparts:
            if len(part) == 5:
                try:
                    modNexus, modstr = int(part), part
                except:
                    continue
        if modNexus:
            modtmp = mod.replace(modstr, "<;>").split("<;>")
            modName, modVer = modtmp[0], modtmp[1]
            if modVer.startswith("-"):
                modVer = modVer.lstrip("-").replace("-", ".")
            modVer = modVer.replace("-", ".").replace("_", ".")
            if modName.endswith("-"):
                modName = modName.rstrip("-")
        else:
            modVer = False
        return modName, modNexus, modVer

    def factory(self):
        """Modname analysis."""
        modNoPath = self.cleanPath(self.mod)
        modNoExt = self.cleanExt(modNoPath)
        modName, modNexus, modVer = self.getNexus(modNoExt)
        self.getModName = (modName, modNoExt, modNoPath, modNexus, modVer)


# ------------------------------------------------------------------------------


class DataFilesDetect:  # Polemos
    """Detect Data Files root from package."""

    data_files = None
    common_folders = [
        "bookart",
        "fonts",
        "icons",
        "meshes",
        "music",
        "shaders",
        "sound",
        "splash",
        "textures",
        "video",
        "mwse",
        "distantland",
    ]

    def __init__(self, package_paths, max_depth, mw_files):
        """Init."""
        self.package_paths = package_paths
        self.max_depth = max_depth
        self.mw_files = mw_files

    def TreeFactory(self, data_files):
        """Create path from data."""
        if not data_files:
            return ("", ("root", "\\", -1))
        if data_files[0][2] == 0:
            return (data_files[0][1], ("\\", data_files[0][1], 0))
        result = [data_files[0][1]]
        for x in self.package_paths:
            if (x[1], x[2]) == (data_files[0][0], data_files[0][2] - 1):
                result.append(x[1])
        result.reverse()
        return (os.path.join("", *result), data_files)

    def getDataFiles(self):
        """Return Data Files or None."""
        # No folders in Package root?
        root_folders = [x for x in self.package_paths if x[2] == 0]
        if len(root_folders) == 0:
            return self.TreeFactory(root_folders)
        # Is there a "Data Files" dir?
        data_files = [
            x for x in self.package_paths if x[1].lower() == "Data Files".lower()
        ]
        if all([data_files, len(data_files) == 1]):
            return self.TreeFactory(data_files)
        # Single folder in Package root?
        if len(root_folders) == 1:
            if (
                not root_folders[0][1] in self.common_folders
            ):  # If subfolder is not a common Mw folder
                root_folders_contents = [x for x in self.package_paths if x[2] == 1]
                contents = [
                    x for x in root_folders_contents if x[0] == root_folders[0][1]
                ]
                if any((x for x in contents if x[1].lower() in self.common_folders)):
                    return self.TreeFactory(root_folders)
            else:  # If subfolder IS a common Mw folder
                return self.TreeFactory(root_folders)
        # Multiple folders in package root containing Mw common files/folders?
        if len(root_folders) > 1:
            if not all(
                [
                    True if x in self.common_folders else False
                    for x in [x[1] for x in root_folders]
                ]
            ):
                root_fold_names = [x[1] for x in self.package_paths if x[2] == 0]
                sub_root = [
                    x
                    for x in self.package_paths
                    if x[0] in root_fold_names and x[2] == 1
                ]
                if (
                    len(set([x[0] for x in sub_root if x[1] in self.common_folders]))
                    > 1
                ):
                    return None
                sub_root_files = [
                    x for x in self.mw_files if x[0] in root_fold_names and x[2] == 1
                ]
                if (
                    len(
                        set(
                            [
                                x[0]
                                for x in sub_root_files
                                if x[1] in [x[1] for x in self.mw_files]
                            ]
                        )
                    )
                    > 1
                ):
                    return None
        # Multiple folders in package root?
        if len(root_folders) > 1:
            if any(
                (True for x in root_folders if x[1].lower() in self.common_folders)
            ):  # Are they common Mw folders?
                return self.TreeFactory(root_folders)
        # Any single folder with Mw files?
        common = [x[1] for x in self.mw_files]
        common.extend(self.common_folders)
        if common:
            data_files = [x for x in self.package_paths if x[1] in common]
            return self.TreeFactory(data_files)
        return None


# ------------------------------------------------------------------------------


class CleanJunkTemp:  # Polemos
    """Simple junk files cleaning."""

    junklist = ("thumbs.db", "desktop.ini")
    try:
        tempdir = os.path.join(MashDir, "Temp")
    except:
        tempdir = os.path.join(MashDir, "Temp")
    junk_files = []

    def __init__(self):
        """Init..."""
        self.scan()
        self.clean()

    def scan(self):
        """Scan for junk files."""
        for root, dirs, files in scandir.walk(self.tempdir, topdown=True):
            for file in files:
                if file in self.junklist:
                    junk = os.path.join(root, file.lower())
                    self.junk_files.append(junk)

    def clean(self):
        """Clean junk files."""
        for x in self.junk_files:
            try:
                os.chmod(x, stat.S_IWRITE)
                os.remove(x)
            except:
                pass


# ------------------------------------------------------------------------------


class ArchiveInfo:  # Polemos
    """Read archive contents."""

    getPackageData = []
    common_ext = [".esp", ".esm", ".bsa", ".omwgame", ".omwaddon", ".ttf", ".fnt"]

    def __init__(self, package_path):
        """Init."""
        self.package_path = package_path
        self.parseArchiveStructure()
        self.parseArchiveFiles()
        self.result()

    def archive(self, cmd):
        """Read Package contents."""
        args = ushlex.split(cmd)
        ins = Popen(args, stdout=PIPE, creationflags=DETACHED_PROCESS)
        return ins.stdout

    def parser(self, cmd):
        """Parse archive data."""
        parsed_data = []
        virgin = True
        for entry in self.archive(cmd):
            if virgin:
                if entry[:7] == "Path = ":
                    virgin = False
                    continue
            if entry[:7] == "Path = ":
                parsed_data.append(entry[7:].strip())
        return parsed_data

    def parseArchiveFiles(self):
        """Get Package special files data."""
        # cmd = ur'7z.exe l -slt -sccUTF-8 "%s" *.esp *.esm *.bsa *.omwgame *.omwaddon *.ttf *.fnt -r' % self.package_path
        cmd = f'7z.exe l -slt -sccUTF-8 "{self.package_path}" *.esp *.esm *.bsa *.omwgame *.omwaddon *.ttf *.fnt -r'
        files_path = self.parser(cmd)
        self.mwfiles = self.dataFactory(files_path, tree=False)

    def parseArchiveStructure(self):
        """Get package structure data."""
        # cmd = ur'7z.exe l -slt -sccUTF-8 "%s" -r *\\ -xr!*\\*.*' % self.package_path
        cmd = rf'7z.exe l -slt -sccUTF-8 "{self.package_path}" -r *\ -xr!*\*.*'
        package_folders = self.parser(cmd)
        self.package_paths = self.dataFactory(package_folders)

    def dataFactory(self, data, tree=True):
        """Create file data."""
        objects = [tuple(x.split("\\")) for x in data]
        tmp_level = []
        max_depth = 0
        try:
            max_depth = max([len(x) for x in objects if len(x) > max_depth])
        except:
            pass
        for level in range(max_depth):
            for object in objects:
                if not tree:
                    try:  # For folders
                        if object[level][-4:].lower() not in self.common_ext:
                            continue
                    except:  # For files
                        level = len(object)
                        if object[level - 1][-4:].lower() not in self.common_ext:
                            continue
                try:
                    parent = object[level - 1] if level - 1 >= 0 else "\\"
                except:
                    parent = "\\"
                try:
                    tmp_level.append((parent, object[level], level))
                except:
                    continue
        if tree:
            self.max_depth = max_depth
        return tuple(sorted([x for x in set(tmp_level)]))

    def result(self):
        """Return Archive tree data."""
        self.getPackageData = (self.package_paths, self.max_depth, self.mwfiles)


# ------------------------------------------------------------------------------


class MultiThreadGauge:  # Polemos
    """Provides a multithreaded gauge for archive packing/unpacking."""

    getInstallLen = 0

    def __init__(self, window, packData, mode="unpack"):
        """Init..."""
        self.mode = mode
        if mode == "unpack":
            package_tempdir, package_path, data_files = packData
            title = _("Unpacking...")
            if data_files == "\\":
                data_files = ""
            else:
                data_files = f'"{data_files}*"'
            # cmd = ur'7z.exe -bb -bsp1 x "%s" %s -o"%s" -aoa -scsUTF-8' % (package_path, data_files, package_tempdir)
            cmd = f'7z.exe -bb -bsp1 x "{package_path}" {data_files} -o"{package_tempdir}" -aoa -scsUTF-8'
            self.getmodlen(rf'7z.exe l "{package_path}" {data_files}')
        if mode == "pack":
            pack_source, pack_target = packData
            if pack_target.endswith(".rar"):
                pack_target = f"{pack_target[:-4]}.7z"
            title = _("Packing...")
            cmd = f'7z.exe -bb -bsp1 a "{pack_target}" "{pack_source}\*"'
            cmd = cmd.replace("\\", "/")
        self.cmd = cmd
        import gui.dialog as gui

        self.dialog = gui.GaugeDialog(window, title=title)
        thread.start_new_thread(self.process, ("ProcThr",))
        self.dialog.ShowModal()

    def getmodlen(self, cmd):
        """Get quantity of files to be installed."""
        args = ushlex.split(cmd)
        ins = Popen(args, stdout=PIPE, creationflags=DETACHED_PROCESS)
        for entry in ins.stdout:
            lendata = entry
        lendata = lendata.split()
        self.getInstallLen = int(lendata[4]) if len(lendata) >= 5 else 0

    def process(self, id):
        """Main process thread."""
        args = ushlex.split(self.cmd)
        self.output = Popen(args, stdout=PIPE, creationflags=DETACHED_PROCESS)
        while self.output.poll() is None:
            line = self.output.stdout.readline()
            if "%" in line:
                self.update(int(line[0:3]), "%s%%" % int(line[0:3]))
        self.kill()

    def kill(self):
        """Quit functions."""
        self.output.stdout.close()
        if self.mode == "unpack":
            msg0, msg1 = _("Finishing Unpacking..."), _("Finished Unpacking.")
        else:
            msg0, msg1 = _("Finishing Packing..."), _("Finished Packing.")
        self.update(99, msg0)
        self.update(100, msg1)
        time.sleep(1)
        self.dialog.Destroy()

    def update(self, num, msg=""):
        """Update GaugeDialog."""
        self.dialog.set_msg(msg)
        self.dialog.update(num)


# ------------------------------------------------------------------------------


class MainFunctions:
    """Encapsulates a set of functions and/or object instances so that they can
    be called from the command line with normal command line syntax.

    Functions are called with their arguments. Object instances are called
    with their method and method arguments. E.g.:
    * bish bar arg1 arg2 arg3
    * bish foo.bar arg1 arg2 arg3"""

    def __init__(self):
        """Initialization."""
        self.funcs = {}

    def add(self, func, key=None):
        """Add a callable object.
        func - A function or class instance.
        key - Command line invocation for object (defaults to name of func).
        """
        key = key or func.__name__
        self.funcs[key] = func
        return func

    def main(self):
        """Main function. Call this in __main__ handler."""
        # --Get func
        args = sys.argv[1:]
        attrs = args.pop(0).split(".")
        key = attrs.pop(0)
        func = self.funcs.get(key)
        if not func:
            # Old Python 2 code
            # print _(u'Unknown function/object:'), key
            print(gettext.gettext("Unknown function/object:"), key)
            return
        for attr in attrs:
            func = getattr(func, attr)
        # --Separate out keywords args
        keywords = {}
        argDex = 0
        reKeyArg = re.compile(r"^\-(\D\w+)")
        reKeyBool = re.compile(r"^\+(\D\w+)")
        while argDex < len(args):
            arg = args[argDex]
            if reKeyArg.match(arg):
                keyword = reKeyArg.match(arg).group(1)
                value = args[argDex + 1]
                keywords[keyword] = value
                del args[argDex : argDex + 2]
            elif reKeyBool.match(arg):
                keyword = reKeyBool.match(arg).group(1)
                keywords[keyword] = True
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        func(*args, **keywords)


## SEE HTML/WryeText.py for the usage of this.
# --Commands Singleton
_mainFunctions = MainFunctions()


def mainfunc(func):
    """A function for adding funcs to _mainFunctions. Used as a function decorator ("@mainfunc")."""
    _mainFunctions.add(func)
    return func


class PickleDict:
    """Dictionary saved in a pickle file.
    Note: self.vdata and self.data are not reassigned! (Useful for some clients.)"""

    def __init__(self, path, readOnly=False):
        """Initialize."""
        self.path = path
        self.backup = path.backup
        self.readOnly = readOnly
        self.vdata = {}
        self.data = {}

    def exists(self):
        return self.path.exists() or self.backup.exists()

    def load(self):
        """Loads vdata and data from file or backup file.

        If file does not exist, or is corrupt, then reads from backup file. If
        backup file also does not exist or is corrupt, then no data is read. If
        no data is read, then self.data is cleared.

        If file exists and has a vdata header, then that will be recorded in
        self.vdata. Otherwise, self.vdata will be empty.

        Returns:
          0: No data read (files don't exist and/or are corrupt)
          1: Data read from file
          2: Data read from backup file
        """
        self.vdata.clear()
        self.data.clear()
        for path in (self.path, self.backup):
            if path.exists():
                ins = None
                try:
                    ins = path.open("rb")
                    header = compat.uncpickle(ins)
                    if header == "VDATA":
                        self.vdata.update(compat.uncpickle(ins))
                        self.data.update(compat.uncpickle(ins))
                    else:
                        self.data.update(header)
                    ins.close()
                    return 1 + (path == self.backup)
                except EOFError:
                    if ins:
                        ins.close()
                except Exception as e:
                    print(e)
                    if ins:
                        ins.close()
        # --No files and/or files are corrupt
        return 0

    def save(self):
        """Save to pickle file."""
        if self.readOnly:
            return False
        # --Pickle it
        out = self.path.temp.open("wb")
        for data in ("VDATA", self.vdata, self.data):
            cPickle.dump(data, out, -1)
        out.close()
        self.path.untemp(True)
        return True


# ------------------------------------------------------------------------------


class Settings(DataDict):
    """Settings/configuration dictionary with persistent storage.

    Default setting for configurations are either set in bulk (by the
    loadDefaults function) or are set as needed in the code (e.g., various
    auto-continue settings for mash. Only settings that have been changed from
    the default values are saved in persistent storage.

    Directly setting a value in the dictionary will mark it as changed (and thus
    to be archived). However, an indirect change (e.g., to a value that is a
    list) must be manually marked as changed by using the setChanged method."""

    def __init__(self, dictFile):
        """Initialize. Read settings from dictFile."""
        self.dictFile = dictFile
        if self.dictFile:
            dictFile.load()
            self.vdata = dictFile.vdata.copy()
            self.data = dictFile.data.copy()
        else:
            self.vdata = {}
            self.data = {}
        self.changed = []
        self.deleted = []

    def loadDefaults(self, defaults):
        """Add default settings to dictionary. Will not replace values that are already set."""
        for key in defaults.keys():
            if key not in self.data:
                self.data[key] = defaults[key]

    def setDefault(self, key, default):
        """Sets a single value to a default value if it has not yet been set."""
        pass

    def save(self):
        """Save to pickle file. Only key/values marked as changed are saved."""
        dictFile = self.dictFile
        if not dictFile or dictFile.readOnly:
            return
        dictFile.load()
        dictFile.vdata = self.vdata.copy()
        for key in self.deleted:
            dictFile.data.pop(key, None)
        for key in self.changed:
            dictFile.data[key] = self.data[key]
        dictFile.save()

    def setChanged(self, key):
        """Marks given key as having been changed. Use if value is a dictionary, list or other object."""
        if key not in self.data:
            raise ArgumentError(_("No settings data for %s" % key))
        if key not in self.changed:
            self.changed.append(key)

    def getChanged(self, key, default=None):
        """Gets and marks as changed."""
        if default is not None and key not in self.data:
            self.data[key] = default
        self.setChanged(key)
        return self.data.get(key)

    # --Dictionary Emulation
    def __setitem__(self, key, value):
        """Dictionary emulation. Marks key as changed."""
        if key in self.deleted:
            self.deleted.remove(key)
        if key not in self.changed:
            self.changed.append(key)
        self.data[key] = value

    def __delitem__(self, key):
        """Dictionary emulation. Marks key as deleted."""
        if key in self.changed:
            self.changed.remove(key)
        if key not in self.deleted:
            self.deleted.append(key)
        del self.data[key]

    def setdefault(self, key, value):
        """Dictionary emulation. Will not mark as changed."""
        if key in self.data:
            return self.data[key]
        if key in self.deleted:
            self.deleted.remove(key)
        self.data[key] = value
        return value

    def pop(self, key, default=None):
        """Dictionary emulation: extract value and delete from dictionary."""
        if key in self.changed:
            self.changed.remove(key)
        if key not in self.deleted:
            self.deleted.append(key)
        return self.data.pop(key, default)


class StructFile(file):
    """File reader/writer with extra functions for handling structured data."""

    def unpack(self, format, size):
        """Reads and unpacks according to format."""
        return struct.unpack(format, self.read(size))

    def pack(self, format, *data):
        """Packs data according to format."""
        self.write(struct.pack(format, *data))


class TableColumn:
    """Table accessor that presents table column as a dictionary."""

    def __init__(self, table, column):
        self.table = table
        self.column = column

    def __iter__(self):
        """Dictionary emulation."""
        tableData = self.table.data
        column = self.column
        return (key for key in tableData.keys() if (column in tableData[key]))

    def keys(self):
        return list(self.__iter__())

    def items(self):
        """Dictionary emulation."""
        tableData = self.table.data
        column = self.column
        return [
            (key, tableData[key][column])
            for key in tableData.keys()
            if (column in tableData[key])
        ]

    def has_key(self, key):
        """Dictionary emulation."""
        return self.__contains__(key)

    def clear(self):
        """Dictionary emulation."""
        self.table.delColumn(self.column)

    def get(self, key, default=None):
        """Dictionary emulation."""
        return self.table.getItem(key, self.column, default)

    # --Overloaded
    def __contains__(self, key):
        """Dictionary emulation."""
        tableData = self.table.data
        return tableData.has_key(key) and tableData[key].has_key(self.column)

    def __getitem__(self, key):
        """Dictionary emulation."""
        return self.table.data[key][self.column]

    def __setitem__(self, key, value):
        """Dictionary emulation. Marks key as changed."""
        self.table.setItem(key, self.column, value)

    def __delitem__(self, key):
        """Dictionary emulation. Marks key as deleted."""
        self.table.delItem(key, self.column)


class Table(DataDict):
    """Simple data table of rows and columns, saved in a pickle file. It is
    currently used by modInfos to represent properties associated with modfiles,
    where each modfile is a row, and each property (e.g. modified date or
    'mtime') is a column.

    The "table" is actually a dictionary of dictionaries. E.g.
        propValue = table['fileName']['propName']
    Rows are the first index ('fileName') and columns are the second index
    ('propName')."""

    def __init__(self, dictFile):
        """Intialize and read data from dictFile, if available."""
        self.dictFile = dictFile
        dictFile.load()
        self.vdata = dictFile.vdata
        self.data = dictFile.data
        self.hasChanged = False

    def save(self):
        """Saves to pickle file."""
        dictFile = self.dictFile
        if self.hasChanged and not dictFile.readOnly:
            self.hasChanged = not dictFile.save()

    def getItem(self, row, column, default=None):
        """Get item from row, column. Return default if row,column doesn't exist."""
        data = self.data
        if row in data and column in data[row]:
            return data[row][column]
        else:
            return default

    def getColumn(self, column):
        """Returns a data accessor for column."""
        return TableColumn(self, column)

    def setItem(self, row, column, value):
        """Set value for row, column."""
        data = self.data
        if row not in data:
            data[row] = {}
        data[row][column] = value
        self.hasChanged = True

    def setItemDefault(self, row, column, value):
        """Set value for row, column."""
        data = self.data
        if row not in data:
            data[row] = {}
        self.hasChanged = True
        return data[row].setdefault(column, value)

    def delItem(self, row, column):
        """Deletes item in row, column."""
        data = self.data
        if row in data and column in data[row]:
            del data[row][column]
            self.hasChanged = True

    def delRow(self, row):
        """Deletes row."""
        data = self.data
        if row in data:
            del data[row]
            self.hasChanged = True

    def delColumn(self, column):
        """Deletes column of data."""
        data = self.data
        for rowData in data.values():
            if column in rowData:
                del rowData[column]
                self.hasChanged = True

    def moveRow(self, oldRow, newRow):
        """Renames a row of data."""
        data = self.data
        if oldRow in data:
            data[newRow] = data[oldRow]
            del data[oldRow]
            self.hasChanged = True

    def copyRow(self, oldRow, newRow):
        """Copies a row of data."""
        data = self.data
        if oldRow in data:
            data[newRow] = data[oldRow].copy()
            self.hasChanged = True

    # --Dictionary emulation
    def __setitem__(self, key, value):
        self.data[key] = value
        self.hasChanged = True

    def __delitem__(self, key):
        del self.data[key]
        self.hasChanged = True

    def setdefault(self, key, default):
        if key not in self.data:
            self.hasChanged = True
        return self.data.setdefault(key, default)  # fix

    def pop(self, key, default=None):
        self.hasChanged = True
        return self.data.pop(key, default)


class TankData:
    """Data source for a Tank table."""

    def __init__(self, params):
        """Initialize."""
        self.tankParams = params
        # --Default settings. Subclasses should define these.
        self.tankKey = self.__class__.__name__
        self.tankColumns = []  # --Full possible set of columns.
        self.title = self.__class__.__name__
        self.hasChanged = False

    def getParam(self, key, default=None):  # --Parameter access
        """Get a GUI parameter.
        Typical Parameters:
        * columns: list of current columns.
        * colNames: column_name dict
        * colWidths: column_width dict
        * colAligns: column_align dict
        * colReverse: column_reverse dict (colReverse[column] = True/False)
        * colSort: current column being sorted on
        """
        return self.tankParams.get(self.tankKey + "." + key, default)

    def defaultParam(self, key, value):
        """Works like setdefault for dictionaries."""
        return self.tankParams.setdefault(self.tankKey + "." + key, value)

    def updateParam(self, key, default=None):
        """Get a param, but also mark it as changed.
        Used for deep params like lists and dictionaries."""
        return self.tankParams.getChanged(self.tankKey + "." + key, default)

    def setParam(self, key, value):
        """Set a GUI parameter."""
        self.tankParams["%s.%s" % (self.tankKey, key)] = value

    # --Collection
    def setChanged(self, hasChanged=True):
        """Mark as having changed."""
        pass

    def refresh(self):
        """Refreshes underlying data as needed."""
        pass

    def getRefreshReport(self):
        """Returns a (string) report on the refresh operation."""
        return None

    def getSorted(self, column, reverse):
        """Returns items sorted according to column and reverse."""
        raise AbstractError

    # --Item Info
    def getColumns(self, item=None):
        """Returns text labels for item or for row header if item == None."""
        columns = self.getParam("columns", self.tankColumns)
        if item is None:
            return columns[:]
        raise AbstractError

    def getName(self, item):
        """Returns a string name of item for use in dialogs, etc."""
        return item

    def getGuiKeys(self, item):
        """Returns keys for icon and text and background colors."""
        iconKey = textKey = backKey = None
        return (iconKey, textKey, backKey)


# Util Functions --------------------------------------------------------------
def copyattrs(source, dest, attrs):
    """Copies specified attrbutes from source object to dest object."""
    for attr in attrs:
        setattr(dest, attr, getattr(source, attr))


def cstrip(inString):
    """Convert c-string (null-terminated string) to python string."""
    zeroDex = inString.find("\x00")
    if zeroDex == -1:
        return inString
    else:
        return inString[:zeroDex]


def csvFormat(format):
    """Returns csv format for specified structure format."""
    csvFormat = ""
    for char in format:
        if char in "bBhHiIlLqQ":
            csvFormat += ",%d"
        elif char in "fd":
            csvFormat += ",%f"
        elif char in "s":
            csvFormat += ',"%s"'
    return csvFormat[1:]  # --Chop leading comma


deprintOn = False


def deprint(*args, **keyargs):
    """Prints message along with file and line location."""
    if not deprintOn and not keyargs.get("on"):
        return
    import inspect

    stack = inspect.stack()
    file, line, function = stack[1][1:4]
    # Old Python 2 code.
    # print '%s %4d %s: %s' % (GPath(file).tail.s, line, function, ' '.join(map(str, args)))
    print(f"{GPath(file).tail.s} {line:4d} {function}: {' '.join(map(str, args))}")


def delist(header, items, on=False):
    """Prints list as header plus items."""
    if not deprintOn and not on:
        return
    import inspect

    stack = inspect.stack()
    file, line, function = stack[1][1:4]
    # Old Python 2 code.
    # print '%s %4d %s: %s' % (GPath(file).tail.s,line,function,str(header))
    print(f"{GPath(file).tail.s} {line:4d} {function}: {str(header)}")
    if items is None:
        print("> None")
    else:
        # for indexItem in enumerate(items): print '>%2d: %s' % indexItem
        for index, item in enumerate(items):
            print(f">{index:%2d} {item}")


def getMatch(reMatch, group=0):
    """Returns the match or an empty string."""
    if reMatch:
        return reMatch.group(group)
    else:
        return ""


def intArg(arg, default=None):
    """Returns argument as an integer. If argument is a string, then it converts it using int(arg,0)."""
    if arg is None:
        return default
    elif isinstance(arg, StringType):
        return int(arg, 0)
    else:
        return int(arg)


def invertDict(indict):
    """Invert a dictionary."""
    return dict((y, x) for x, y in indict.iteritems())


def listFromLines(lines):  # ???
    """Generate a list from a string with lines, stripping comments and skipping empty strings."""
    reComment = re.compile("#.*")
    temp = [reComment.sub("", x).strip() for x in lines.split("\n")]
    temp = [x for x in temp if x]
    return temp


def listSubtract(alist, blist):
    """Return a copy of first list minus items in second list."""
    result = []
    for item in alist:
        if item not in blist:
            result.append(item)
    return result


def listJoin(*inLists):
    """Joins multiple lists into a single list."""
    outList = []
    for inList in inLists:
        outList.extend(inList)
    return outList


def listGroup(items):
    """Joins items into a list for use in a regular expression.
    E.g., a list of ('alpha','beta') becomes '(alpha|beta)'"""
    return "(" + ("|".join(items)) + ")"


def rgbString(red, green, blue):
    """Converts red, green blue ints to rgb string."""
    return chr(red) + chr(green) + chr(blue)


def rgbTuple(rgb):
    """Converts red, green, blue string to tuple."""
    return struct.unpack("BBB", rgb)


def unQuote(inString):
    """Removes surrounding quotes from string."""
    if len(inString) >= 2 and inString[0] == '"' and inString[-1] == '"':
        return inString[1:-1]
    else:
        return inString


def winNewLines(inString):
    """Converts unix newlines to windows newlines."""
    return reUnixNewLine.sub("\r\n", inString)


# Log/Progress ----------------------------------------------------------------


# -*- coding: utf-8 -*-

# Wrye Mash Polemos fork GPL License and Copyright Notice ==============================
#
# This file is part of Wrye Mash Polemos fork.
#
# Wrye Mash, Polemos fork Copyright (C) 2017-2021 Polemos
# * based on code by Yacoby copyright (C) 2011-2016 Wrye Mash Fork Python version
# * based on code by Melchor copyright (C) 2009-2011 Wrye Mash WMSA
# * based on code by Wrye copyright (C) 2005-2009 Wrye Mash
# License: http://www.gnu.org/licenses/gpl.html GPL version 2 or higher
#
#  Copyright on the original code 2005-2009 Wrye
#  Copyright on any non trivial modifications or substantial additions 2009-2011 Melchor
#  Copyright on any non trivial modifications or substantial additions 2011-2016 Yacoby
#  Copyright on any non trivial modifications or substantial additions 2017-2020 Polemos
#
# ======================================================================================

# Original Wrye Mash License and Copyright Notice ======================================
#
#  Wrye Mash is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  Wrye Bolt is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Mash; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  Wrye Mash copyright (C) 2005, 2006, 2007, 2008, 2009 Wrye
#
# ========================================================================================

import sys, io, os
from datetime import datetime
from stat import S_IWUSR, S_IREAD

maxLogEntries = 20  # Polemos: Max number of sessions stored in the log.


def logCheck():
    """Check and limit log size."""
    try:
        os.chmod("WryeMash.log", S_IWUSR | S_IREAD)
        with io.open("WryeMash.log", "r") as fileBasedLogger:
            rawLog = fileBasedLogger.readlines()
            index = [
                n for n, x in enumerate(rawLog) if "=== Wrye Mash started. ===" in x
            ]
        if len(index) >= maxLogEntries:
            with io.open("WryeMash.log", "w") as fileBasedLogger:
                index.reverse()
                fileBasedLogger.write("".join(rawLog[index[maxLogEntries - 1] :]))
    except:
        pass  # Unable to access the log file. C'est La Vie.


class ErrorLogger:
    """Class can be used for a writer to write to multiple streams. Duplicated
    in both possible startup files so log can be created without external
    dependencies"""

    def __init__(self, outStream):
        """Init."""
        self.outStream = outStream

    def write(self, message):
        """Write to out-stream."""
        try:
            # There can be more than one stream; outStream may be a single
            # stream or a list of them.
            [stream.write(message) for stream in self.outStream]
        except:
            pass


# Logger start
logCheck()
fileBasedLogger = file("WryeMash.log", "a+")
sys.stdout, sys.stderr = ErrorLogger((fileBasedLogger, sys.__stdout__)), ErrorLogger(
    (fileBasedLogger, sys.__stderr__)
)
fileBasedLogger.write(
    "\n%s: # ===================== Wrye Mash started. ===================== #\n"
    % datetime.now()
)

# Main
# import masher
import master

## NOTE: MainLoop is inherited from the wx.App class.
if len(sys.argv) > 1:
    master.MashApp(int(sys.argv[1])).MainLoop()
else:
    master.MashApp().MainLoop()

fileBasedLogger.close()
