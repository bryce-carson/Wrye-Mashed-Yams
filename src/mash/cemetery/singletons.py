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

# Original Wrye Mash License and Copyright Notice ======================================
#  This file is part of Wrye Mash.
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
# ======================================================================================

# Polemos: Not a pure singleton pattern yet.

# Main Interface
mashFrame = None
MenuBar = None
statusBar = None
# Utilities Panel
utilsList = None
# Installers Panel
gInstList = None
gInstallers = None
# OpenMW Datamods Panel
ModdataList = None
ModPackageList = None
# Mods/Plugins Panel
modList = None
modDetails = None
ArchivesList = None
BSArchives = None
modsMastersList = None
# Saves Panel
saveList = None
saveDetails = None
savesMastersList = None
# Screenshots Panel
screensList = None
# Dialogs
helpBrowser = None
journalBrowser = None
docBrowser = None
settingsWindow = None
# Misc
MashDir = None
user_profile = None
Profile = None
images = {}


# TODO: certain application functionality should have a command line API.
class Callables:
    """A singleton set of objects (typically functions or class instances) that
    can be called as functions from the command line.

    Functions are called with their arguments, while object instances are called
    with their method and then their functions. E.g.:
    * bish afunction arg1 arg2 arg3
    * bish anInstance.aMethod arg1 arg2 arg3"""

    def __init__(self):  # --Ctor
        """Initialization."""
        self.callObjs = {}

    def add(self, callObj, callKey=None):  # --Add a callable
        """Add a callable object.

        callObj:
            A function or class instance.
        callKey:
            Name by which the object will be accessed from the command line.
            If callKey is not defined, then callObj.__name__ is used."""
        callKey = callKey or callObj.__name__
        self.callObjs[callKey] = callObj

    def help(self, callKey):  # --Help
        """Print help for specified callKey."""
        help(self.callObjs[callKey])

    def main(self):  # --Main
        callObjs = self.callObjs
        # --Call key, tail
        callParts = string.split(sys.argv[1], ".", 1)
        callKey = callParts[0]
        callTail = len(callParts) > 1 and callParts[1]
        # --Help request?
        if callKey == "-h":
            help(self)
            return
        # --Not have key?
        if callKey not in callObjs:
            print("Unknown function/object:", callKey)
            return
        # --Callable
        callObj = callObjs[callKey]
        if type(callObj) == types.StringType:
            callObj = eval(callObj)
        if callTail:
            callObj = eval("callObj." + callTail)
        # --Args
        args = sys.argv[2:]
        # --Keywords?
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
                keywords[keyword] = 1
                del args[argDex]
            else:
                argDex = argDex + 1
        # --Apply
        callObj(*args, **keywords)


# --Callables Singleton
callables = Callables()


def mainFunction(func):
    """A function for adding functions to callables."""
    callables.add(func)
    return func


class Log:
    """Log Callable. This is the abstract/null version. Useful version should
    override write functions.

    Log is divided into sections with headers. Header text is assigned (through
    setHeader), but isn't written until a message is written under it. I.e.,
    if no message are written under a given header, then the header itself is
    never written."""

    def __init__(self):
        """Initialize."""
        self.header = None
        self.prevHeader = None
        self.indent = ""

    def setHeader(self, header):
        """Sets the header."""
        self.header = header

    def __call__(self, message):
        """Callable. Writes message, and if necessary, header and footer."""
        if self.header != self.prevHeader:
            if self.prevHeader:
                self.writeFooter()
            if self.header:
                self.writeHeader(self.header)
            self.prevHeader = self.header
        self.writeMessage(message)

    # --Abstract/null writing functions...
    def writeHeader(self, header):
        """Write header. Abstract/null version."""
        pass

    def writeFooter(self):
        """Write mess. Abstract/null version."""
        pass

    def writeMessage(self, message):
        """Write message to log. Abstract/null version."""
        pass


class LogFile(Log):  # Polemos, just in case...
    """Log that writes messages to file."""

    def __init__(self, out):
        self.out = out
        Log.__init__(self)

    def writeHeader(self, header):
        self.out.write("%s%s\n" % (self.indent, header))

    def writeFooter(self):
        self.out.write("%s\n" % self.indent)

    def writeMessage(self, message):  # Polemos fix
        try:
            self.out.write("%s%s\n" % (self.indent, message))
        except:
            self.out.write("%s%s\n" % (self.indent, message.encode("utf-8")))


class Progress:
    """Progress Callable: Shows progress on message change and at regular intervals."""

    def __init__(self, interval=0.5):
        self.interval = interval
        self.message = None
        self.time = 0
        self.base = 0.0
        self.scale = 1.0
        self.max = 1.0

    def setBaseScale(self, base=0.0, scale=1.0):
        if scale == 0:
            raise ArgumentError(_("Scale must not equal zero!"))
        self.base = base
        self.scale = scale

    def setMax(self, max):
        self.max = 1.0 * max or 1.0  # --Default to 1.0

    def __call__(self, rawProgress, message=None):
        if not message:
            message = self.message
        if (message != self.message) or (time.time() > (self.time + self.interval)):
            self.doProgress(self.base + self.scale * rawProgress / self.max, message)
            self.message = message
            self.time = time.time()

    def doProgress(self, progress, message):
        """Default doProgress does nothing."""
        try:
            yield progress, message
        except:
            pass


# ------------------------------------------------------------------------------


class ProgressFile(Progress):
    """Prints progress to file (stdout by default)."""

    def __init__(self, interval=0.5, out=None):
        Progress.__init__(self, interval)
        self.out = out

    def doProgress(self, progress, message):
        out = self.out or sys.stdout  # --Defaults to stdout
        out.write("%0.2f %s\n" % (progress, message))


class Flags(object):
    """Represents a flag field."""

    __slots__ = ["_names", "_field"]

    @staticmethod
    def getNames(*names):
        """Returns dictionary mapping names to indices.
        Names are either strings or (index,name) tuples.
        E.g., Flags.getNames('isQuest','isHidden',None,(4,'isDark'),(7,'hasWater'))"""
        namesDict = {}
        for index, name in enumerate(names):
            if type(name) is tuple:
                namesDict[name[1]] = name[0]
            elif name:  # --skip if "name" is 0 or None
                namesDict[name] = index
        return namesDict

    # --Generation
    def __init__(self, value=0, names=None):
        """Initialize. Attrs, if present, is mapping of attribute names to indices. See getAttrs()"""
        # object.__setattr__(self,'_field',int(value) | 0L)
        object.__setattr__(self, "_field", int(value) | 0)
        object.__setattr__(self, "_names", names or {})

    def __call__(self, newValue=None):
        """Retuns a clone of self, optionally with new value."""
        if newValue is not None:
            # return Flags(int(newValue) | 0L,self._names)
            return Flags(int(newValue) | 0, self._names)
        else:
            return Flags(self._field, self._names)

    def __deepcopy__(self, memo=None):
        if memo is None:
            memo = {}
        newFlags = Flags(self._field, self._names)
        memo[id(self)] = newFlags
        return newFlags

    # --As hex string
    def hex(self):
        """Returns hex string of value."""
        return "%08X" % (self._field,)

    def dump(self):
        """Returns value for packing"""
        return self._field

    # --As int
    def __int__(self):
        """Return as integer value for saving."""
        return self._field

    # --As list
    def __getitem__(self, index):
        """Get value by index. E.g., flags[3]"""
        return bool((self._field >> index) & 1)

    def __setitem__(self, index, value):
        """Set value by index. E.g., flags[3] = True"""
        # value = ((value or 0L) and 1L) << index
        value = ((value or 0) and 1) << index
        # mask = 1L << index
        mask = 1 << index
        self._field = (self._field & ~mask) | value

    # --As class
    def __getattr__(self, name):
        """Get value by flag name. E.g. flags.isQuestItem"""
        try:
            names = object.__getattribute__(self, "_names")
            index = names[name]
            return (object.__getattribute__(self, "_field") >> index) & 1 == 1
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        """Set value by flag name. E.g., flags.isQuestItem = False"""
        if name in ("_field", "_names"):
            object.__setattr__(self, name, value)
        else:
            self.__setitem__(self._names[name], value)

    # --Native operations
    def __eq__(self, other):
        """Logical equals."""
        if isinstance(other, Flags):
            return self._field == other._field
        else:
            return self._field == other

    def __ne__(self, other):
        """Logical not equals."""
        if isinstance(other, Flags):
            return self._field != other._field
        else:
            return self._field != other

    def __and__(self, other):
        """Bitwise and."""
        if isinstance(other, Flags):
            other = other._field
        return self(self._field & other)

    def __invert__(self):
        """Bitwise inversion."""
        return self(~self._field)

    def __or__(self, other):
        """Bitwise or."""
        if isinstance(other, Flags):
            other = other._field
        return self(self._field | other)

    def __xor__(self, other):
        """Bitwise exclusive or."""
        if isinstance(other, Flags):
            other = other._field
        return self(self._field ^ other)

    def getTrueAttrs(self):
        """Returns attributes that are true."""
        trueNames = [name for name in self._names if getattr(self, name)]
        trueNames.sort(key=lambda xxx: self._names[xxx])
        return tuple(trueNames)


class Log:
    """Log Callable. This is the abstract/null version. Useful version should
    override write functions.

    Log is divided into sections with headers. Header text is assigned (through
    setHeader), but isn't written until a message is written under it. I.e.,
    if no message are written under a given header, then the header itself is
    never written."""

    def __init__(self):
        """Initialize."""
        self.header = None
        self.prevHeader = None

    def setHeader(self, header, writeNow=False, doFooter=True):
        """Sets the header."""
        self.header = header
        if self.prevHeader:
            self.prevHeader += "x"
        self.doFooter = doFooter
        if writeNow:
            self()

    def __call__(self, message=None):
        """Callable. Writes message, and if necessary, header and footer."""
        if self.header != self.prevHeader:
            if self.prevHeader and self.doFooter:
                self.writeFooter()
            if self.header:
                self.writeHeader(self.header)
            self.prevHeader = self.header
        if message:
            self.writeMessage(message)

    # --Abstract/null writing functions...
    def writeHeader(self, header):
        """Write header. Abstract/null version."""
        pass

    def writeFooter(self):
        """Write mess. Abstract/null version."""
        pass

    def writeMessage(self, message):
        """Write message to log. Abstract/null version."""
        pass


class LogFile(Log):
    """Log that writes messages to file."""

    def __init__(self, out):
        self.out = out
        Log.__init__(self)

    def writeHeader(self, header):
        self.out.write(header + "\n")

    def writeFooter(self):
        self.out.write("\n")

    def writeMessage(self, message):
        self.out.write(message + "\n")


class Progress:
    """Progress Callable: Shows progress when called."""

    def __init__(self, full=1.0):
        if (1.0 * full) == 0:
            raise ArgumentError(_("Full must be non-zero!"))
        self.message = ""
        self.full = full
        self.state = 0
        self.debug = False

    def setFull(self, full):
        """Set's full and for convenience, returns self."""
        if (1.0 * full) == 0:
            raise ArgumentError(_("Full must be non-zero!"))
        self.full = full
        return self

    def plus(self, increment=1):
        """Increments progress by 1."""
        self.__call__(self.state + increment)

    def __call__(self, state, message=""):
        """Update progress with current state. Progress is state/full."""
        if (1.0 * self.full) == 0:
            raise ArgumentError(_("Full must be non-zero!"))
        if message:
            self.message = message
        # Old Python 2 code.
        # if self.debug: deprint('%0.3f %s' % (1.0*state/self.full, self.message))
        if self.debug:
            deprint(f"{1.0*state/self.full:.3f} {self.message}")
        self.doProgress(1.0 * state / self.full, self.message)
        self.state = state

    def doProgress(self, progress, message):
        """Default doProgress does nothing."""
        pass


class SubProgress(Progress):
    """Sub progress goes from base to ceiling."""

    def __init__(self, parent, baseFrom=0.0, baseTo="+1", full=1.0, silent=False):
        """For creating a subprogress of another progress meter.
        progress: parent (base) progress meter
        baseFrom: Base progress when this progress == 0.
        baseTo: Base progress when this progress == full
          Usually a number. But string '+1' sets it to baseFrom + 1
        full: Full meter by this progress' scale."""
        Progress.__init__(self, full)
        if baseTo == "+1":
            baseTo = baseFrom + 1
        if baseFrom < 0 or baseFrom >= baseTo:
            raise ArgumentError(
                _("BaseFrom must be >= 0 and BaseTo must be > BaseFrom")
            )
        self.parent = parent
        self.baseFrom = baseFrom
        self.scale = 1.0 * (baseTo - baseFrom)
        self.silent = silent

    def __call__(self, state, message=""):
        """Update progress with current state. Progress is state/full."""
        if self.silent:
            message = ""
        self.parent(self.baseFrom + self.scale * state / self.full, message)
        self.state = state


class ProgressFile(Progress):
    """Prints progress to file (stdout by default)."""

    def __init__(self, full=1.0, out=None):
        Progress.__init__(self, full)
        self.out = out or sys.stdout

    def doProgress(self, progress, message):
        self.out.write("%0.2f %s\n" % (progress, message))


class ReplJournalDate:
    """Callable: Adds <hr>before journal date."""

    def __init__(self):
        self.prevDate = None

    def __call__(self, mo):
        prevDate = self.prevDate
        newDate = mo.group(1)
        if newDate != prevDate:
            hr = prevDate and "<hr>" or ""
            self.prevDate = newDate
            return '%s<FONT COLOR="9F0000"><B>%s</B></FONT><BR>' % (hr, newDate)
        else:
            return ""


@mainFunction
def etxtToHtml(inFileName):
    """Generates an html file from an etxt file."""
    import time

    # --Re's
    reHead2 = re.compile(r"## *([^=]*) ?=*")
    reHead3 = re.compile(r"# *([^=]*) ?=*")
    reHead4 = re.compile(r"@ *(.*)\s+")
    reHead5 = re.compile(r"% *(.*)\s+")
    reList = re.compile(r"( *)([-!?\.\+\*o]) (.*)")
    reBlank = re.compile(r"\s+$")
    reMDash = re.compile(r"--")
    reBoldEsc = re.compile(r"\_")
    reBoldOpen = re.compile(r" _")
    reBoldClose = re.compile(r"(?<!\\)_( |$)")
    reItalicOpen = re.compile(r" ~")
    reItalicClose = re.compile(r"~( |$)")
    reBoldicOpen = re.compile(r" \*")
    reBoldicClose = re.compile(r"\*( |$)")
    reBold = re.compile(r"\*\*([^\*]+)\*\*")
    reItalic = re.compile(r"\*([^\*]+)\*")
    reLink = re.compile(r"\[\[(.*?)\]\]")
    reHttp = re.compile(r" (http://[_~a-zA-Z0-9\./%-]+)")
    reWww = re.compile(r" (www\.[_~a-zA-Z0-9\./%-]+)")
    reDate = re.compile(r"\[([0-9]+/[0-9]+/[0-9]+)\]")
    reContents = re.compile(r"\[CONTENTS=?(\d+)\]\s*$")
    reWd = re.compile(r"\W\d*")
    rePar = re.compile(r"\^(.*)")
    reFullLink = re.compile(r"(:|#|\.[a-zA-Z]{3,4}$)")
    # --Date styling (Replacement function used with reDate.)
    dateNow = time.time()

    def dateReplace(maDate):
        date = time.mktime(time.strptime(maDate.group(1), "%m/%d/%Y"))  # [1/25/2005]
        age = int((dateNow - date) / (7 * 24 * 3600))
        if age < 0:
            age = 0
        if age > 3:
            age = 3
        return "<span class=date%d>%s</span>" % (age, maDate.group(1))

    def linkReplace(maLink):
        address = text = maLink.group(1).strip()
        if "|" in text:
            (address, text) = [chunk.strip() for chunk in text.split("|", 1)]
        if not reFullLink.search(address):
            address = address + ".html"
        return '<a href="%s">%s</a>' % (address, text)

    # --Defaults
    title = ""
    level = 1
    spaces = ""
    headForm = "<h%d><a name='%s'>%s</a></h%d>\n"
    # --Open files
    inFileRoot = re.sub("\.[a-zA-Z]+$", "", inFileName)
    with open(inFileName) as inFile:
        # --Init
        outLines = []
        contents = []
        addContents = 0
        # --Read through inFile
        for line in inFile.readlines():
            maHead2 = reHead2.match(line)
            maHead3 = reHead3.match(line)
            maHead4 = reHead4.match(line)
            maHead5 = reHead5.match(line)
            maPar = rePar.match(line)
            maList = reList.match(line)
            maBlank = reBlank.match(line)
            maContents = reContents.match(line)
            # --Contents
            if maContents:
                if maContents.group(1):
                    addContents = int(maContents.group(1))
                else:
                    addContents = 100
            # --Header 2?
            if maHead2:
                text = maHead2.group(1)
                name = reWd.sub("", text)
                line = headForm % (2, name, text, 3)
                if addContents:
                    contents.append((2, name, text))
                # --Title?
                if not title:
                    title = text
            # --Header 3?
            elif maHead3:
                text = maHead3.group(1)
                name = reWd.sub("", text)
                line = headForm % (3, name, text, 3)
                if addContents:
                    contents.append((3, name, text))
                # --Title?
                if not title:
                    title = text
            # --Header 4?
            elif maHead4:
                text = maHead4.group(1)
                name = reWd.sub("", text)
                line = headForm % (4, name, text, 4)
                if addContents:
                    contents.append((4, name, text))
            # --Header 5?
            elif maHead5:
                text = maHead5.group(1)
                name = reWd.sub("", text)
                line = headForm % (5, name, text, 5)
                if addContents:
                    contents.append((5, name, text))
            # --List item
            elif maList:
                spaces = maList.group(1)
                bullet = maList.group(2)
                text = maList.group(3)
                if bullet == ".":
                    bullet = "&nbsp;"
                elif bullet == "*":
                    bullet = "&bull;"
                level = len(spaces) / 2 + 1
                # line = spaces+'<p class=list-'+`level`+'>'+bullet+'&nbsp; '
                line = f"{spaces}<p class=list-{level}>{bullet}&nbsp; "
                line = line + text + "\n"
            # --Paragraph
            elif maPar:
                line = "<p>" + maPar.group(1)
            # --Blank line
            # elif maBlank: line = spaces+'<p class=list'+`level`+'>&nbsp;</p>'
            elif maBlank:
                line = f"{spaces}<p class=list-{level}>&nbsp;</p>"
            # --Misc. Text changes
            line = reMDash.sub("&#150", line)
            line = reMDash.sub("&#150", line)
            # --New bold/italic subs
            line = reBoldOpen.sub(" <B>", line)
            line = reItalicOpen.sub(" <I>", line)
            line = reBoldicOpen.sub(" <I><B>", line)
            line = reBoldClose.sub("</B> ", line)
            line = reBoldEsc.sub("_", line)
            line = reItalicClose.sub("</I> ", line)
            line = reBoldicClose.sub("</B></I> ", line)
            # --Old style bold/italic subs
            line = reBold.sub(r"<B><I>\1</I></B>", line)
            line = reItalic.sub(r"<I>\1</I>", line)
            # --Date
            line = reDate.sub(dateReplace, line)
            # --Local links
            line = reLink.sub(linkReplace, line)
            # --Hyperlink
            line = reHttp.sub(r' <a href="\1">\1</a>', line)
            line = reWww.sub(r' <a href="http://\1">\1</a>', line)
            # --Write it
            outLines.append(line)
    # --Output file
    with open(inFileRoot + ".html", "w") as outFile:
        outFile.write(etxtHeader % (title,))
        didContents = False
        for line in outLines:
            if reContents.match(line):
                if not didContents:
                    baseLevel = min([level for (level, name, text) in contents])
                    for level, name, text in contents:
                        level = level - baseLevel + 1
                        if level <= addContents:
                            outFile.write(
                                '<p class=list-%d>&bull;&nbsp; <a href="#%s">%s</a></p>\n'
                                % (level, name, text)
                            )
                    didContents = True
            else:
                outFile.write(line)
        outFile.write("</body>\n</html>\n")  # --Done


@mainFunction
def genHtml(fileName):
    """Generate html from old style etxt file or from new style wtxt file."""
    ext = os.path.splitext(fileName)[1].lower()
    if ext == ".etxt":
        etxtToHtml(fileName)
    elif ext == ".txt":
        import wtxt

        docsDir = r"c:\program files\bethesda softworks\morrowind\data files\docs"
        wtxt.genHtml(fileName, cssDir=docsDir)
    else:
        raise "Unrecognized file type: " + ext


# Translation
@mainFunction
def getTranslatorName():
    """Prints locale."""
    import locale

    language = locale.getlocale()[0].split("_", 1)[0]
    # Old Python 2 code.
    # print "Your translator file is: Mopy\\locale\\%s.txt" % (language,)
    print(rf"Your translator file is: Mopy\locale\{langauge}.txt")


@mainFunction
def dumpTranslator():
    """Dumps new translation key file using existing key, value pairs."""
    # --Locale Path
    import locale

    language = locale.getlocale()[0].split("_", 1)[0]
    outPath = "locale\\NEW%s.txt" % (language,)
    with open(outPath, "w") as outFile:
        # --Scan for keys and dump to
        keyCount = 0
        dumpedKeys = set()
        reKey = re.compile(r"_\([\'\"](.+?)[\'\"]\)")
        for pyFile in ("mush.py", "mosh.py", "mash.py", "masher.py"):
            with open(pyFile) as pyText:
                for lineNum, line in enumerate(pyText):
                    line = re.sub("#.*", "", line)
                    for key in reKey.findall(line):
                        if key in dumpedKeys:
                            continue
                        outFile.write("=== %s, %d\n" % (pyFile, lineNum + 1))
                        outFile.write(key + "\n>>>>\n")
                        value = _(re.sub(r"\\n", "\n", key))
                        value = re.sub("\n", r"\\n", value)
                        if value != key:
                            outFile.write(value)
                        outFile.write("\n")
                        dumpedKeys.add(key)
                        keyCount += 1
    # Old Python 2 code.
    # print keyCount,'translation keys written to',outPath
    print(f"{keyCount} translation keys written to {outPath}")


@mainFunction
def fileRefs_testWrite(fileName):
    """Does a read write test on cells."""
    init(3)
    fileRefs = mosh.FileRefs(mosh.saveInfos[fileName])
    fileRefs.refresh()
    for cell in fileRefs.cells:
        cellId = cell.getId()
        oldData = cell.data
        cell.changed = True
        cell.getSize()
        # Old Python 2 code.
        # if cell.data != oldData: print cellId, 'BAD'
        if cell.data != oldData:
            print(f"{cellId} BAD")
        else:
            pass


# Information
@mainFunction
def refInfo(fileName, forMods=-1, forCellId=None):
    """Prints reference info for specified file."""
    init(3)
    forMods = int(forMods)
    fileInfo = mosh.modInfos.data.get(fileName) or mosh.saveInfos.data.get(fileName)
    if not fileInfo:
        raise "No such file: " + fileName
    masters = fileInfo.tes3.masters
    fileRefs = mosh.FileRefs(fileInfo, True)
    fileRefs.refresh()
    for cell in sorted(fileRefs.cells, cmp=lambda a, b: a.cmpId(b)):
        if forCellId and forCellId != cell.getId():
            continue
        printCell = cell.getId()
        objects = cell.getObjects().list()
        objects.sort(key=lambda a: a[1])
        for object in objects:
            if forMods != -1 and forMods != object[0]:
                continue
            if printCell:
                # Old Python 2 code.
                # print printCell
                print(printCell)
                printCell = False
            master = object[0] and masters[object[0] - 1][0]
            # Old Python 2 code.
            # print ' ', object[:3], master
            print(f" {object[:3]} master")


# Misc.
@mainFunction
def genLibrary(modName, textName):
    """Library Generator."""
    init(2)
    fileInfo = mosh.modInfos[modName]
    fileLib = mosh.FileLibrary(fileInfo)
    fileLib.loadUI()
    fileLib.doImport(textName)
    fileLib.safeSave()


@mainFunction
def genSchedule(fileName, espName=None):
    """Schedule Generator."""
    generator = mosh.ScheduleGenerator()
    generator.loadText(fileName)
    # --Write to text file?
    if not espName:
        outName = os.path.splitext(fileName)[0] + ".mws"
        generator.dumpText(outName)
    # --Write to esp file?
    else:
        init(2)
        fileInfo = mosh.modInfos.data.get(espName)
        if not fileInfo:
            raise _("No such file: ") + espName
        generator.save(fileInfo)


@mainFunction
def fixFix(fileName):  # --Fix fix operator.
    """Search and replace change on scripts and dialog scripts.
    Strips spaces from around fix (->) operator."""
    rePointer = re.compile(r" -> ?", re.M)
    init(2)
    fileInfo = mosh.modInfos[fileName]
    # --Fix scripts
    if True:
        fileRep = mosh.FileRep(fileInfo)
        fileRep.loadUI(factory={"SCPT": mosh.Scpt})
        for script in fileRep.indexed["SCPT"].values():
            oldCode = script.sctx.data
            if rePointer.search(oldCode):
                newCode = rePointer.sub("->", oldCode)
                script.setCode(newCode)
                # Old Python 2 code.
                # print script.id
                print(script.id)
        fileRep.safeSave()
    # --Fix dialog scripts
    if True:
        fileDials = mosh.FileDials(fileInfo)
        fileDials.load()
        for dial in fileDials.dials:
            for info in dial.infos:
                for record in info.records:
                    if record.name != "BNAM":
                        continue
                    if rePointer.search(record.data):
                        # Old Python 2 code.
                        # print dial.id
                        # print ' ',info.text
                        # print ' ',record.data
                        # print

                        print(dial.id)
                        print(f" {info.text}")
                        print(f" {record.data}")
                        print("")
                        record.setData(rePointer.sub("->", record.data))
                        info.setChanged()
                        break
        fileDials.safeSave()


@mainFunction
def pcLeveler(fileName):
    """TextMunch: Reads in 0/30 level settings and spits out a level setting script."""
    # --Constants
    reSpace = re.compile(r"\s+")
    charSet0 = string.Template(mush.charSet0)
    charSet1 = string.Template(mush.charSet1)
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
    statGroups = (
        ("Primary", mush.primaryAttributes),
        ("Secondary", ("Health",)),
        ("Combat Skills", mush.combatSkills),
        ("Magic Skills", mush.magicSkills),
        ("Stealth Skills", mush.stealthSkills),
    )
    # --Read file/stdin
    if fileName:
        inFile = open(fileName)
    else:
        inFile = sys.stdin
    # --Read file
    stats = {}
    className = inFile.readline().strip()
    for statName, line in zip(statNames, inFile.readlines()[:35]):
        v00, v30 = re.match("(\d+)\s+(\d+)", line).groups()
        stats[statName] = (int(v00), int(v30))
    inFile.close()
    # --Health
    str00, str30 = stats["Strength"]
    end00, end30 = stats["Endurance"]
    hea00 = (str00 + end00) / 2
    hea30 = (str30 + end30) / 2 + end30 * 29 / 10
    stats["Health"] = (hea00, hea30)
    # --Dump Script
    # print charSet0.substitute(className=className)
    print(charSet0.substitute(className=className))
    for tag, statNames in statGroups:
        # print ';--'+tag
        print(f";--{tag}")
        for statName in statNames:
            compName = reSpace.sub("", statName)
            v00, v30 = stats[statName]
            # if v00 == v30: print 'set%s %d' % (compName,v00,)
            if v00 == v30:
                print(f"set{compName:s} {v00:d}")
            else:
                # print '  set stemp to %d + ((%d - %d)*level/30)' % (v00,v30,v00)
                # print 'set%s stemp' % (compName,)
                print(f"  set stemp to {v00:d} + (({v30:d} - {v00:d})*level/30)")
                print(f"set{compName} stemp")
        # print
        print()
    # print charSet1.substitute(className=className)
    print(charSet1.substitute(className=className))


@mainFunction
def etxtToWtxt(fileName=None):
    """TextMunch: Converts etxt files to wtxt formatting."""
    if fileName:
        ins = open(fileName)
    else:
        ins = sys.stdin
    for line in ins:
        line = re.sub(r"^\^ ?", "", line)
        line = re.sub(r"^## ([^=]+) =", r"= \1 ==", line)
        line = re.sub(r"^# ([^=]+) =", r"== \1 ", line)
        line = re.sub(r"^@ ", r"=== ", line)
        line = re.sub(r"^% ", r"==== ", line)
        line = re.sub(r"\[CONTENTS=(\d+)\]", r"{{CONTENTS=\1}}", line)
        line = re.sub(r"~([^ ].+?)~", r"~~\1~~", line)
        line = re.sub(r"_([^ ].+?)_", r"__\1__", line)
        line = re.sub(r"\*([^ ].+?)\*", r"**\1**", line)
        # print line,
        print(f"{line} ")


@mainFunction
def textMunch(fileName=None):
    """TextMunch: This is a standin for EditPlus Text munching. It should just
    call whatever text muncher is currently being used."""
    etxtToWtxt(fileName)


@mainFunction
def temp(fileName):
    """ "Temp."""
    init(2)
    fileInfo = mosh.modInfos[fileName]
    fileDials = mosh.FileDials(fileInfo)
    fileDials.load(factory={"INFO": mosh.Info})
    # --Replacement defs
    repls = {
        "activator": "init",
        "allowBack": "back",
        "aShort": "s01",
        "bShort": "s02",
    }
    replKeys = set(repls.keys())
    reRepls = re.compile(r"\b(" + ("|".join(replKeys)) + r")\b")
    reStartScript = re.compile("^startScript", re.I + re.M)

    def doRepl(mo):
        return repls[mo.group(0)]

    # --Loop over dials
    for dial in fileDials.dials:
        # print dial.id
        print(dial.id)
        for info in dial.infos:
            # --Change id?
            if info.spId == "wr_mysMenu_s":
                info.spId = "wr_mysCre"
                info.setChanged()
            elif info.spId == "wr_bookMenu_s":
                info.spId = "wr_bookCre"
                info.setChanged()
            # --Change tests?
            if info.spId in ("wr_mysCre", "wr_bookCre"):
                # --Test vars
                for index, test in enumerate(info.tests):
                    if not test:
                        pass
                    elif test.text.lower() == "modder":
                        if test.value == 0 and test.oper == 0:
                            test.text = "menu"
                            test.value = -1
                            # print ' modder >> menu'
                            print(" modder >> menu")
                        else:
                            info.tests[index] = 0
                            # print ' modder X'
                            print(" modder X")
                    elif test.text in replKeys:
                        # print '',test.text,repls[test.text]
                        print(f" {test.text} {repls[test.text]}")
                        test.text = repls[test.text]
                # --Result
                if info.script:
                    newScript = reRepls.sub(doRepl, info.script)
                    newScript = reStartScript.sub("player->startScript", newScript)
                    if newScript != info.script:
                        info.script = newScript
                        # print ' script subbed'
                        print(" script subbed")
                info.setChanged()
    fileDials.safeSave()


@mainFunction
def temp2(fileName=None):
    """Temp 2."""
    init(2)
    fileName = fileName or "Wrye CharSet.esp"
    csi = mosh.CharSetImporter()
    csi.loadText("Wrye CharSets.etxt")
    csi.printMajors()
