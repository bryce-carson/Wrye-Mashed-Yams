import io
import struct
from .errors import Tes3Error
from .unimash import _


def rgbString(red, green, blue):
    """Converts red, green blue ints to rgb string."""
    return chr(red) + chr(green) + chr(blue)


class Record:
    """Generic Record."""

    def __init__(self, name, size, delFlag, recFlag, input_Stream=None, unpack=False):
        self.changed = False
        self.name = name
        self.size = size
        self.delFlag = delFlag
        self.recFlag = recFlag
        self.data = None
        self.id = None
        self.inName = input_Stream and getattr(input_Stream, "inName", None)
        if input_Stream:
            self.load(input_Stream, unpack)

    def load(self, input_Stream=None, unpack=False):
        """Load data from input_Stream stream or internal data buffer."""
        name = self.name
        # --Read, but don't analyze.
        if not unpack:
            self.data = input_Stream.read(self.size, name)
        # --Read and analyze input_Stream.
        elif input_Stream:
            inPos = input_Stream.tell()
            self.loadData(input_Stream)
            input_Stream.seek(inPos, 0, name + "_REWIND")
            self.data = input_Stream.read(self.size, name)
        # --Analyze internal buffer.
        else:
            reader = Tes3Reader(self.inName, cStringIO.StringIO(self.data))
            self.loadData(reader)
            reader.close()

    def loadData(self, input_Stream):
        """Loads data from input stream. Called by load()."""
        raise AbstractError

    def setChanged(self, value=True):
        """Sets changed attribute to value. [Default = True.]"""
        self.changed = value

    def setData(self, data):
        """Sets data and size."""
        self.data = data
        self.size = len(data)

    def getSize(self):  # Polemos: Removed duplicate.
        """Return size of self.data, after, if necessary, packing it."""
        if not self.changed:
            return self.size
        # --Pack data and return size.
        out = Tes3Writer(cStringIO.StringIO())
        self.dumpData(out)
        self.data = out.getvalue()
        out.close()
        self.size = len(self.data)
        self.setChanged(False)
        return self.size

    def dumpData(self, out):
        """Dumps state into data. Called by getSize()."""
        raise AbstractError

    def dump(self, out):
        """Dumps record header and data into output file stream."""
        if self.changed:
            raise StateError(_("Data changed: ") + self.name)
        if not self.data:
            raise StateError(_("Data undefined: ") + self.name)
        out.write(struct.pack("4s3i", self.name, self.size, self.delFlag, self.recFlag))
        out.write(self.data)

    def getId(self):
        """Get id. Doesn't work for all record types."""
        if getattr(self, "id", None):
            return self.id
        name = self.name
        # --Singleton records
        if name in frozenset(
            ("FMAP", "GAME", "JOUR", "KLST", "PCDT", "REFR", "SPLM", "TES3")
        ):
            return None
        # --Special records.
        elif name == "CELL":
            reader = self.getReader()
            srName = reader.findSubRecord("NAME", name)
            srData = reader.findSubRecord("DATA", name)
            (flags, gridX, gridY) = struct.unpack("3i", self.data)
            if flags & 1:
                self.id = cstrip(srName)
            else:
                self.id = "[%d,%d]" % (gridX, gridY)
        elif name == "INFO":
            srData = self.getReader().findSubRecord("INAM", name)
            self.id = cstrip(srData)
        elif name == "LAND":
            srData = self.getReader().findSubRecord("INTV", name)
            self.id = "[%d,%d]" % struct.unpack("2i", srData)
        elif name == "PGRD":
            reader = self.getReader()
            srData = reader.findSubRecord("DATA", name)
            srName = reader.findSubRecord("NAME", name)
            gridXY = struct.unpack("2i", srData[:8])
            if srData != (0, 0) or not srName:
                self.id = "[%d,%d]" % gridXY
            else:
                self.id = cstrip(srName)
        elif name == "SCPT":
            srData = self.getReader().findSubRecord("SCHD", name)
            self.id = cstrip(srData[:32])
        # --Most records: id in NAME record.
        else:
            srData = self.getReader().findSubRecord("NAME", name)
            self.id = srData and cstrip(srData)
        # --Done
        return self.id

    def getReader(self):
        """Returns a Tes3Reader wrapped around self.data."""
        return Tes3Reader(self.inName, cStringIO.StringIO(self.data))


class ContentRecord(Record):
    """Content record. Abstract parent for CREC, CNTC, NPCC record classes."""

    def getId(self):
        """Returns base + index id. E.g. crate_mine00000001"""
        return "%s%08X" % (self.id, self.index)


class ListRecord(Record):
    """Leveled item or creature list. Does all the work of Levc and Levi classes."""

    def __init__(self, name, size, delFlag, recFlag, input_Stream=None, unpack=False):
        """Initialize."""
        # --Record type.
        if name not in ("LEVC", "LEVI"):
            raise ArgumentError(_("Type must be either LEVC or LEVI."))
        # --Data
        self.id = None
        self.calcFromAllLevels = False
        self.calcForEachItem = False
        self.chanceNone = 0
        self.count = 0
        self.entries = []
        self.isDeleted = False
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        """Load data from stream or own data."""
        # --Read subrecords
        bytesRead = 0
        objectId = None
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader(self.name)
            bytesRead += 8 + size
            subData = input_Stream.read(size, self.name + "." + name)
            # --Id?
            if name == "NAME":
                self.id = cstrip(subData)
            # --Flags
            elif name == "DATA":
                flags = struct.unpack("i", subData)[0]
                if self.name == "LEVC":
                    self.calcFromAllLevels = (flags & 1) == 1
                else:
                    self.calcForEachItem = (flags & 1) == 1
                    self.calcFromAllLevels = (flags & 2) == 2
            # --Chance None
            elif name == "NNAM":
                self.chanceNone = struct.unpack("B", subData)[0]
            # --Count
            elif name == "INDX":
                self.count = struct.unpack("i", subData)[0]
            # --Creature/Item Id?
            elif name == "CNAM" or name == "INAM":
                objectId = cstrip(subData)
            # --PC Level
            elif name == "INTV":
                pcLevel = struct.unpack("h", subData)[0]
                self.entries.append((pcLevel, objectId))
                objectId = None
            # --Deleted?
            elif name == "DELE":
                self.isDeleted = True
            # --Else
            else:
                raise Tes3UnknownSubRecord(self.inName, name, self.name)
        # --No id?
        if not self.id:
            raise Tes3Error(self.inName, _("No id for %s record.") % (self.name,))
        # --Bad count?
        if self.count != len(self.entries):
            self.count = len(self.entries)
            self.setChanged()

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Header
        out.packSub0("NAME", self.id)
        if getattr(self, "isDeleted", False):
            out.packSub("DELE", "i", 0)
            return
        if self.name == "LEVC":
            flags = 1 * self.calcFromAllLevels
            etype = "CNAM"
        else:
            flags = 1 * self.calcForEachItem + 2 * self.calcFromAllLevels
            etype = "INAM"
        out.packSub("DATA", "i", flags)
        out.packSub("NNAM", "B", self.chanceNone)
        out.packSub("INDX", "i", len(self.entries))
        # --Entries
        for pcLevel, objectId in self.entries:
            out.packSub0(etype, objectId)
            out.packSub("INTV", "h", pcLevel)

    def mergeWith(self, newLevl):
        """Merges newLevl settings and entries with self."""
        # --Clear
        self.data = None
        self.setChanged()
        # --Merge settings
        self.isDeleted = newLevl.isDeleted
        self.chanceNone = newLevl.chanceNone
        self.calcFromAllLevels = self.calcFromAllLevels or newLevl.calcFromAllLevels
        self.calcForEachItem = self.calcForEachItem or newLevl.calcForEachItem
        # --Merge entries
        entries = self.entries
        oldEntries = set(entries)
        for entry in newLevl.entries:
            if entry not in oldEntries:
                entries.append(entry)
        # --Sort entries by pcLevel
        self.entries.sort(key=lambda a: a[0])


class SubRecord:
    """Generic Subrecord."""

    def __init__(self, name, size, input_Stream=None, unpack=False):
        self.changed = False
        self.name = name
        self.size = size
        self.data = None
        self.inName = input_Stream and getattr(input_Stream, "inName", None)
        if input_Stream:
            self.load(input_Stream, unpack)

    def load(self, input_Stream, unpack=False):
        self.data = input_Stream.read(self.size, "----.----")

    def setChanged(self, value=True):
        """Sets changed attribute to value. [Default = True.]"""
        self.changed = value

    def setData(self, data):
        """Sets data and size."""
        self.data = data
        self.size = len(data)

    def getSize(self):
        """Return size of self.data, after, if necessary, packing it."""
        if not self.changed:
            return self.size
        # --StringIO Object
        out = Tes3Writer(cStringIO.StringIO())
        self.dumpData(out)
        # --Done
        self.data = out.getvalue()
        self.data.close()
        self.size = len(self.data)
        self.setChanged(False)
        return self.size

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        raise AbstractError

    def dump(self, out):
        if self.changed:
            raise StateError(_("Data changed: ") + self.name)
        if not self.data:
            raise StateError(_("Data undefined: ") + self.name)
        out.write(struct.pack("4si", self.name, len(self.data)))
        out.write(self.data)


class Tes3(Record):
    """TES3 Record. File header."""

    def __init__(
        self, name="TES3", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialize."""
        self.hedr = None
        self.masters = []  # --(fileName,fileSize)
        self.gmdt = None
        self.others = []  # --SCRD, SCRS (Screen snapshot?)
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        MAX_SUB_SIZE = 100 * 1024
        # --Header
        (name, size) = input_Stream.unpackSubHeader("TES3", "HEDR")
        self.hedr = Tes3_Hedr(name, size, input_Stream, True)
        bytesRead = 8 + size
        # --Read Records
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("TES3")
            if size > MAX_SUB_SIZE:
                raise Tes3SizeError(self.inName, name, size, -MAX_SUB_SIZE, True)
            # --Masters
            if name == "MAST":
                # --FileName
                fileName = cstrip(input_Stream.read(size, "TES3.MAST"))
                bytesRead += 8 + size
                # --FileSize
                (name, size) = input_Stream.unpackSubHeader("TES3", "DATA", 8)
                fileSize = input_Stream.unpack("Q", 8, "TES3.DATA")[0]
                self.masters.append((fileName, fileSize))
                bytesRead += 16
            # --Game Data
            elif name == "GMDT":
                self.gmdt = Tes3_Gmdt(name, size, input_Stream, True)
                bytesRead += 8 + size
            # --Screen snapshot?
            else:
                self.others.append(SubRecord(name, size, input_Stream))
                bytesRead += 8 + size

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Get sizes and dump into dataIO
        self.hedr.getSize()
        self.hedr.dump(out)
        for name, size in self.masters:
            out.packSub0("MAST", name)
            out.packSub("DATA", "Q", size)
        if self.gmdt:
            self.gmdt.getSize()
            self.gmdt.dump(out)
        for other in self.others:
            other.getSize()
            other.dump(out)


class Tes3_Gmdt(SubRecord):
    """TES3 GMDT subrecord. Savegame data. PC name, health, cell, etc."""

    def load(self, input_Stream, unpack=False):
        self.data = input_Stream.read(self.size, "TES3.GMDT")
        if not unpack:
            return
        data = struct.unpack("3f12s64s4s32s", self.data)
        self.curHealth = data[0]
        self.maxHealth = data[1]
        self.day = data[2]
        self.unknown1 = data[3]
        self.curCell = cstrip(data[4])
        self.unknown2 = data[5]
        self.playerName = cstrip(data[6])

    def getSize(self):
        if not self.data:
            raise StateError(_("Data undefined: ") + self.name)
        if not self.changed:
            return self.size
        self.data = struct.pack(
            "3f12s64s4s32s",
            self.curHealth,
            self.maxHealth,
            self.day,
            self.unknown1,
            self.curCell,
            self.unknown2,
            self.playerName,
        )
        self.size = len(self.data)
        self.setChanged(False)
        return self.size


class Tes3_Hedr(SubRecord):
    """TES3 HEDR subrecord. File header."""

    def __init__(self, name, size, input_Stream=None, unpack=False):
        """Initialize."""
        self.version = 1.3
        self.fileType = 0  # --0: esp; 1: esm; 32: ess
        self.author = ""
        self.description = ""
        self.numRecords = 0
        SubRecord.__init__(self, name, size, input_Stream, unpack)

    def load(self, input_Stream, unpack=False):
        self.data = input_Stream.read(self.size, "TES3.HEDR")
        if not unpack:
            return
        data = struct.unpack("fi32s256si", self.data)
        self.version = data[0]
        self.fileType = data[1]
        self.author = cstrip(data[2])
        self.description = cstrip(data[3])
        self.numRecords = data[4]

    def getSize(self):  # Polemos: Fixed a struct bug here.
        if not self.data and not self.changed:
            raise StateError(_("Data undefined: %s" % self.name))
        if not self.changed:
            return self.size
        self.description = winNewLines(self.description)

        try:
            self.data = struct.pack(
                "fi32s256si",
                self.version,
                self.fileType,
                self.author,
                self.description,
                self.numRecords,
            )
        except:
            try:
                author_po = str(self.author)
                self.data = struct.pack(
                    "fi32s256si",
                    self.version,
                    self.fileType,
                    author_po,
                    self.description,
                    self.numRecords,
                )
            except:
                try:
                    description_po = str(self.description)
                    self.data = struct.pack(
                        "fi32s256si",
                        self.version,
                        self.fileType,
                        self.author,
                        description_po,
                        self.numRecords,
                    )
                except:
                    pass
        self.size = len(self.data)
        self.setChanged(False)
        return self.size


class Scpt(Record):
    """SCPT record. Script."""

    # --Class Data
    subRecordNames = ["SCVR", "SCDT", "SCTX", "SLCS", "SLSD", "SLFD", "SLLD", "RNAM"]

    def __init__(
        self, name="SCPT", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.numShorts = 0
        self.numLongs = 0
        self.numFloats = 0
        self.dataSize = 0
        self.varSize = 0
        # --Mod data
        self.scvr = None
        self.scdt = None
        self.sctx = None
        # --Save data
        self.slcs = None
        self.slsd = None
        self.slfd = None
        self.slld = None
        self.rnam = None
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Subrecords
        bytesRead = 0
        srNameSet = set(Scpt.subRecordNames)
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("SCPT")
            # --Header
            if name == "SCHD":
                (
                    self.id,
                    self.numShorts,
                    self.numLongs,
                    self.numFloats,
                    self.dataSize,
                    self.varSize,
                ) = input_Stream.unpack("32s5i", size, "SCPT.SCHD")
                self.id = cstrip(self.id)
            # --Other subrecords
            elif name in srNameSet:
                setattr(self, name.lower(), SubRecord(name, size, input_Stream))
            else:
                raise Tes3Error(self.inName, _("Unknown SCPT record: ") + name)
            bytesRead += 8 + size
        if bytesRead != self.size:
            raise Tes3Error(
                self.inName, _("SCPT %s: Unexpected subrecords") % (self.id)
            )

    def getRef(self):
        """Returns reference data for a global script."""
        rnam = self.rnam
        if not rnam or rnam.data == chr(255) * 4:
            return None
        if not settings[
            "mash.extend.pluginput_Stream"
        ]:  # MWSE compatibility != enabled
            if rnam.size != 4:
                raise Tes3Error(self.inName, (_("SCPT.RNAM"), rnam.size, 4, True))
        # MWSE adds an 8-byte variant for supporting more than 255 mods.
        if rnam.size == 4:
            iMod = struct.unpack("3xB", rnam.data)[0]
            iObj = struct.unpack("i", rnam.data[:3] + "\x00")[0]
            return (iMod, iObj)
        elif rnam.size == 8:
            return struct.unpack("2i", rnam.data)
        else:
            raise Tes3Error(
                self.inName, (_("SCPT.RNAM"), rnam.size, 4, True)
            )  # Why the _ ???

    def setRef(self, reference):
        """Set reference data for a global script."""
        (iMod, iObj) = reference
        if (
            iMod > 255 and settings["mash.extend.pluginput_Stream"]
        ):  # MWSE compatibility == enabled
            self.rnam.setData(struct.pack("2i", iMod, iObj))
        else:
            self.rnam.setData(struct.pack("i", iObj)[:3] + struct.pack("B", iMod))
        self.setChanged()

    def setCode(self, code):
        # --SCHD
        self.dataSize = 2
        # --SCDT
        if not self.scdt:
            self.scdt = SubRecord("SCDT", 0)
        self.scdt.setData(struct.pack("BB", 1, 1))  # --Uncompiled
        # --SCVR
        # self.scvr = None
        # --SCTX (Code)
        if not self.sctx:
            self.sctx = SubRecord("SCTX", 0)
        self.sctx.setData(winNewLines(code))
        # --Done
        self.setChanged()
        self.getSize()

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Header
        out.packSub(
            "SCHD",
            "32s5i",
            self.id,
            self.numShorts,
            self.numLongs,
            self.numFloats,
            self.dataSize,
            self.varSize,
        )
        # --Others
        for record in [
            getattr(self, srName.lower(), None) for srName in Scpt.subRecordNames
        ]:
            if not record:
                continue
            record.size = len(record.data)
            record.dump(out)


class Npcc(ContentRecord):
    """NPCC record. NPC contents/change."""

    def __init__(
        self, name="NPCC", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.index = 0
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Name
        (name, size) = input_Stream.unpackSubHeader("NPCC", "NAME")
        self.id = cstrip(input_Stream.read(size, "CELL.NAME"))
        # --Index
        (name, size) = input_Stream.unpackSubHeader("NPCC", "NPDT", 8)
        (unknown, self.index) = input_Stream.unpack("ii", size, "CELL.NPDT")


class Levc(ListRecord):
    """LEVC record. Leveled list for creatures."""

    pass


class Levi(ListRecord):
    """LEVI record. Leveled list for items."""

    pass


class Land(Record):
    """LAND record. Landscape: heights, vertices, texture references, etc."""

    def __init__(
        self, name="LAND", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialize."""
        self.id = None
        # self.gridX = 0
        # self.gridY = 0
        self.heights = None
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def getId(self):
        """Return id. Also, extract gridX and gridY."""
        if self.id:
            return self.id
        reader = self.getReader()
        subData = reader.findSubRecord("INTV", "LAND")
        (self.gridX, self.gridY) = struct.unpack("ii", subData)
        self.id = "[%d,%d]" % (self.gridX, self.gridY)
        return self.id

    def getHeights(self):
        """Returns len(65x65) array of vertex heights."""
        if self.heights:
            return self.heights
        reader = self.getReader()
        subData = reader.findSubRecord("VHGT", "LAND")
        if not subData:
            return None
        height0 = struct.unpack("f", subData[:4])[0]
        import array

        deltas = array.array("b", subData[4 : 4 + 65 * 65])
        iheights = array.array("i")
        iheights.append(0)
        for index in xrange(1, 65 * 65):
            if index % 65:
                iheights.append(iheights[-1] + deltas[index])
            else:
                iheights.append(iheights[-65] + deltas[index])
        heights = self.heights = array.array("f")
        for index in xrange(65 * 65):
            heights.append(8 * (height0 + iheights[index]))
        return self.heights


class Cell(Record):
    """Cell record. Name, region, objects in cell, etc."""

    def __init__(
        self,
        name="CELL",
        size=0,
        delFlag=0,
        recFlag=0,
        input_Stream=None,
        unpack=False,
        skipObjRecords=False,
    ):
        # --Arrays
        self.skipObjRecords = skipObjRecords
        self.records = []  # --Initial records
        self.objects = []
        self.tempObjects = []
        self.endRecords = []  # --End records (map notes)
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        skipObjRecords = self.skipObjRecords
        # --Name
        (name, size) = input_Stream.unpackSubHeader("CELL", "NAME")
        self.cellName = cstrip(input_Stream.read(size, "CELL.NAME"))
        bytesRead = 8 + size
        # --Other Records
        subGroup = 0  # --0:(start) records; 10: (early) objects; 20: temp objects; 30:end records
        nam0 = 0  # --Temp record count from file
        printCell = 0
        objRecords = None
        isMoved = False
        isSpawned = False
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("CELL")
            # --New reference?
            if name == "FRMR":
                if not subGroup:
                    subGroup = 10
                # --Spawned? Then just another subrecord.
                if isSpawned:
                    isSpawned = False
                    if skipObjRecords:
                        input_Stream.seek(size, 1, "CELL.FRMR")
                    else:
                        objRecords.append(SubRecord(name, size, input_Stream))
                    bytesRead += 8 + size
                # --New Record?
                else:
                    # MWSE compatibility != enabled
                    if not settings["mash.extend.pluginput_Stream"]:
                        if size != 4:
                            raise Tes3SizeError(self.inName, "CELL.FRMR", size, 4, True)
                    # MWSE can change the size of this field to 8 bytes for more than 255 mods.
                    iMod = 0
                    iObj = 0
                    if size == 4:
                        rawData = input_Stream.read(4, "CELL.FRMR")
                        iMod = struct.unpack("3xB", rawData)[0]
                        iObj = struct.unpack("i", rawData[:3] + "\x00")[0]
                        bytesRead += 12
                    elif size == 8:
                        rawData = input_Stream.read(8, "CELL.FRMR")
                        (iMod, iObj) = struct.unpack("2i", rawData)
                        bytesRead += 16
                    else:
                        raise Tes3SizeError(self.inName, "CELL.FRMR", size, 4, True)
                    (name, size) = input_Stream.unpackSubHeader("CELL", "NAME")
                    objId = cstrip(input_Stream.read(size, "CELL.NAME_NEXT"))
                    bytesRead += 8 + size
                    if skipObjRecords:
                        pass
                    elif isMoved:
                        isMoved = False
                        objRecords.append(Cell_Frmr())
                    else:
                        objRecords = [Cell_Frmr()]
                    # --Save Object
                    object = (iMod, iObj, objId, objRecords)
                    if subGroup == 10:
                        self.objects.append(object)
                    else:
                        self.tempObjects.append(object)
            # --Leveled Creature? (Ninja Monkey)
            elif name == "LVCR":
                isSpawned = True
                if skipObjRecords:
                    input_Stream.seek(size, 1, "CELL.LVCR")
                else:
                    objRecords.append(SubRecord(name, size, input_Stream))
                bytesRead += 8 + size
            # --Map Note?
            elif name == "MPCD":
                subGroup = 30
                self.endRecords.append(SubRecord(name, size, input_Stream))
                bytesRead += 8 + size
            # --Move Ref?
            elif name == "MVRF" and not isSpawned:
                if not subGroup:
                    subGroup = 10
                isMoved = True
                if skipObjRecords:
                    input_Stream.seek(size, 1, "CELL.MVRF")
                else:
                    objRecords = [SubRecord(name, size, input_Stream)]
                bytesRead += 8 + size
            # --Map Note?
            elif name == "NAM0":
                if subGroup >= 20:
                    raise Tes3Error(
                        self.input_Stream, self.getId() + _(": Second NAM0 subrecord.")
                    )
                subGroup = 20
                if size != 4:
                    raise Tes3SizeError(self.inName, "CELL.NAM0", size, 4, True)
                if size != 4:
                    raise Tes3SizeError(self.inName, "CELL.NAM0", size, 4, True)
                nam0 = input_Stream.unpack("i", 4, "CELL.NAM0")[0]
                bytesRead += 8 + size
            # --Start subrecord?
            elif not subGroup:
                record = SubRecord(name, size, input_Stream)
                self.records.append(record)
                if name == "DATA":
                    (self.flags, self.gridX, self.gridY) = struct.unpack(
                        "3i", record.data
                    )
                bytesRead += 8 + size
            # --Object sub-record?
            elif subGroup < 30:
                # if isSpawned:
                if skipObjRecords:
                    input_Stream.seek(size, 1, "CELL.SubRecord")
                else:
                    objRecords.append(SubRecord(name, size, input_Stream))
                bytesRead += 8 + size
            # --End subrecord?
            elif subGroup == 30:
                self.endRecords.append(SubRecord(name, size, input_Stream))
                bytesRead += 8 + size
        # --Nam0 miscount?
        if nam0 != len(self.tempObjects):
            self.setChanged()

    def getObjects(self):
        """Return a Cell_Objects input_Streamtance."""
        return Cell_Objects(self)

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Get sizes and dump into dataIO
        out.packSub0("NAME", self.cellName)
        # --Hack: input_Streamert data record if necessary
        for record in self.records:
            if record.name == "DATA":
                break
        else:
            self.records.input_Streamert(0, SubRecord("DATA", 0))
        # --Top Records
        for record in self.records:
            if record.name == "DATA":
                record.setData(struct.pack("3i", self.flags, self.gridX, self.gridY))
            record.getSize()
            record.dump(out)
        # --Objects
        inTempObjects = False
        for object in self.getObjects().list():
            # --Begin temp objects?
            if not inTempObjects and (object in self.tempObjects):
                out.packSub("NAM0", "i", len(self.tempObjects))
                inTempObjects = True
            (iMod, iObj, objId, objRecords) = object
            for record in objRecords:
                # --FRMR/NAME placeholder?
                if isinput_Streamtance(record, Cell_Frmr):
                    if (
                        iMod > 255 and settings["mash.extend.pluginput_Stream"]
                    ):  # MWSE compatibility == enabled
                        out.pack("4si", "FRMR", 8)
                        out.write(struct.pack("2i", iMod, iObj))
                    else:
                        out.pack("4si", "FRMR", 4)
                        out.write(struct.pack("i", iObj)[:3])
                        out.pack("B", iMod)
                    out.packSub0("NAME", objId)
                else:
                    record.getSize()
                    record.dump(out)
        # --End Records
        for endRecord in self.endRecords:
            endRecord.getSize()
            endRecord.dump(out)

    def getId(self):
        # --Interior Cell?
        if self.flags & 1:
            return self.cellName
        else:
            return "[%d,%d]" % (self.gridX, self.gridY)

    def cmpId(self, other):
        """Return cmp value compared to other cell for sorting."""
        selfIsInterior = self.flags & 1
        otherIsInterior = other.flags & 1
        # --Compare exterior/interior. (Exterior cells sort to top.)
        if selfIsInterior != otherIsInterior:
            # --Return -1 if self is exterior
            return -1 + 2 * (selfIsInterior)
        # --Interior cells?
        elif selfIsInterior:
            return cmp(self.cellName, other.cellName)
        # --Exterior cells?
        elif self.gridX != other.gridX:
            return cmp(self.gridX, other.gridX)
        else:
            return cmp(self.gridY, other.gridY)


class Crec(ContentRecord):
    """CREC record. Creature contents."""

    def __init__(
        self, name="CREC", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.index = 0
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Name
        (name, size) = input_Stream.unpackSubHeader("CREC", "NAME")
        self.id = cstrip(input_Stream.read(size, "CREC.NAME"))
        # --Index
        (name, size) = input_Stream.unpackSubHeader("CELL", "INDX")
        self.index = input_Stream.unpack("i", size, "CREC.INDX")[0]


class Cntc(ContentRecord):
    """CNTC record. Container contents."""

    def __init__(
        self, name="CNTC", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.index = 0
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Name
        (name, size) = input_Stream.unpackSubHeader("CNTC", "NAME")
        self.id = cstrip(input_Stream.read(size, "CNTC.NAME"))
        # --Index
        (name, size) = input_Stream.unpackSubHeader("CNTC", "INDX")
        self.index = input_Stream.unpack("i", size, "CTNC.INDX")[0]


class Dial(Record):
    """DIAL record. Name of dialog topic/greeting/journal name, etc."""

    def __init__(
        self, name="DIAL", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.type = 0
        self.unknown1 = None
        self.dele = None
        self.data = None
        self.infos = []
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Id
        (name, size) = input_Stream.unpackSubHeader("DIAL", "NAME")
        self.id = cstrip(input_Stream.read(size, "DIAL.NAME"))
        bytesRead = 8 + size
        # --Type
        (name, size) = input_Stream.unpackSubHeader("DIAL", "DATA")
        if size == 1:
            self.type = input_Stream.unpack("B", size, "DIAL.DATA")[0]
        elif size == 4:
            (self.type, self.unknown1) = input_Stream.unpack("B3s", size, "DIAL.DATA")
        else:
            raise Tes3SizeError(self.inName, "DIAL.DATA", size, 4, False)
        bytesRead += 8 + size
        # --Dele?
        if size == 4:
            (name, size) = input_Stream.unpackSubHeader("DIAL", "DELE")
            self.dele = input_Stream.read(size, "DIAL.DELE")
            bytesRead += 8 + size
        if bytesRead != self.size:
            raise Tes3Error(
                self.inName,
                _("DIAL %d %s: Unexpected subrecords") % (self.type, self.id),
            )

    def sortInfos(self):
        """Sorts infos by link order."""
        # --Build infosById
        infosById = {}
        for info in self.infos:
            if info.id is None:
                raise Tes3Error(
                    self.inName, _("Dialog %s: info with missing id.") % (self.id,)
                )
            infosById[info.id] = info
        # --Heads
        heads = []
        for info in self.infos:
            if info.prevId not in infosById:
                heads.append(info)
        # --Heads plus their next chainput_Stream
        newInfos = []
        for head in heads:
            nextInfo = head
            while nextInfo:
                newInfos.append(nextInfo)
                nextInfo = infosById.get(nextInfo.nextId)
        # --Anything left?
        for info in self.infos:
            if info not in newInfos:
                newInfos.append(info)
        # --Replace existing list
        self.infos = newInfos


class Fmap(Record):
    """FMAP record. Worldmap for savegame."""

    # --Class data
    DEEP = rgbString(25, 36, 33)
    SHALLOW = rgbString(37, 55, 50)
    LAND = rgbString(62, 45, 31)
    GRID = rgbString(27, 40, 37)
    BORDER = SHALLOW
    MARKED = rgbString(202, 165, 96)

    def __init__(
        self, name="FMAP", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialize."""
        self.mapd = None  # --Array of 3 byte strings when expanded (512x512)
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Header
        out.packSub("MAPH", "ii", 512, 9)
        # --Data
        out.pack("4si", "MAPD", 512 * 512 * 3)
        out.write("".join(self.mapd))

    def edit(self):
        """Prepare data for editing."""
        wmap = 512
        if not self.mapd:
            data = self.data[24:]
            mapd = self.mapd = []
            for index in xrange(0, 3 * wmap * wmap, 3):
                mapd.append(data[index : index + 3])
        self.setChanged()

    def drawRect(self, color, x1, y1, x2, y2):
        """Draw rectangle of specified color."""
        if not self.changed:
            self.edit()
        wmap = 512
        mapd = self.mapd
        for y in xrange(y1, y2):
            ymoff = wmap * y
            for x in xrange(x1, x2):
                mapd[x + ymoff] = color

    def drawBorder(self, color, x1, y1, x2, y2, thick):
        """Draw's a border rectangle of specified thickness."""
        self.drawRect(color, x1, y1, x2, y1 + thick)
        self.drawRect(color, x1, y1, x1 + thick, y2)
        self.drawRect(color, x2 - thick, y1, x2, y2)
        self.drawRect(color, x1, y2 - thick, x2, y2)

    def drawGrid(self, gridLines=True):
        """Draw grid for visible map."""
        if not self.changed:
            self.edit()
        cGrid = Fmap.GRID
        cBorder = Fmap.BORDER
        if gridLines:  # --Some fools don't want the grid!
            # --Grid
            for uv in xrange(-25, 26, 5):
                xy = 512 / 2 - 9 * uv + 4
                self.drawRect(cGrid, 0, xy, 512, xy + 1)
                self.drawRect(cGrid, xy, 0, xy + 1, 512)
            # --Grid axes
            xy = 512 / 2 + 4
            self.drawRect(cBorder, 0, xy, 512, xy + 1)
            self.drawRect(cBorder, xy, 0, xy + 1, 512)
        # --Border
        self.drawBorder(cBorder, 0, 0, 512, 512, 4)

    def drawCell(self, land, uland, vland, marked):
        """Draw a cell from landscape record."""
        from math import sqrt, pow

        # --Tranlate grid point (u,v) to pixel point
        if not self.changed:
            self.edit()
        # --u/v max/min are grid range of visible map.
        # --wcell is bit width of cell. 512 is bit width of visible map.
        if not settings["mash.mcp.extend.map"]:  # Regular Morrowind map
            (umin, umax, vmin, vmax, wcell, wmap) = (-28, 27, -27, 28, 9, 512)
        else:  # MCP extended Morrowind map
            (umin, umax, vmin, vmax, wcell, wmap) = (-51, 50, -63, 38, 4, 512)
        if not ((umin <= uland <= umax) and (vmin <= vland <= vmax)):
            return
        # --x0,y0 is bitmap coordinates of top left of cell in visible map.
        (x0, y0) = (4 + wcell * (uland - umin), 4 + wcell * (vmax - vland))
        # --Default to deep
        mapc = [Fmap.DEEP] * (9 * 9)
        heights = land and land.getHeights()
        if heights:
            # --Land heights are in 65*65 array, starting from bottom left.
            # --Coordinate conversion. Subtract one extra from height array because it's edge to edge.
            converter = [(65 - 2) * px / (wcell - 1) for px in range(wcell)]
            for yc in xrange(wcell):
                ycoff = wcell * yc
                yhoff = (65 - 1 - converter[yc]) * 65
                for xc in xrange(wcell):
                    height = heights[converter[xc] + yhoff]
                    if height >= 0:  # --Land
                        (r0, g0, b0, r1, g1, b1, scale) = (
                            66,
                            48,
                            33,
                            32,
                            23,
                            16,
                            sqrt(height / 3000.0),
                        )
                        scale = int(scale * 10) / 10.0  # --Make boundaries sharper.
                        r = chr(max(0, int(r0 - r1 * scale)) & ~1)
                    else:  # --Sea
                        # --Scale color from shallow to deep color.
                        (r0, g0, b0, r1, g1, b1, scale) = (
                            37,
                            55,
                            50,
                            12,
                            19,
                            17,
                            -height / 2048.0,
                        )
                        r = chr(max(0, int(r0 - r1 * scale)) | 1)
                    g = chr(max(0, int(g0 - g1 * scale)))
                    b = chr(max(0, int(b0 - b1 * scale)))
                    mapc[xc + ycoff] = r + g + b
        # --Draw it
        mapd = self.mapd
        for yc in xrange(wcell):
            ycoff = wcell * yc
            ymoff = wmap * (y0 + yc)
            for xc in xrange(wcell):
                cOld = mapd[x0 + xc + ymoff]
                cNew = mapc[xc + ycoff]
                rOld = ord(cOld[0])
                # --New or old is sea.
                if (ord(cNew[0]) & 1) or (
                    (rOld & 1)
                    and (-2 < (1.467742 * rOld - ord(cOld[1])) < 2)
                    and (-2 < (1.338710 * rOld - ord(cOld[2])) < 2)
                ):
                    mapd[x0 + xc + ymoff] = cNew
        if marked:
            self.drawBorder(Fmap.MARKED, x0 + 2, y0 + 2, x0 + 7, y0 + 7, 1)
            pass


class Glob(Record):
    """Global record. Note that global values are stored as floats regardless of type."""

    def __init__(
        self, name="GLOB", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialization."""
        self.type = "l"
        self.value = 0
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        """Loads from input_Stream/internal data."""
        # --Read subrecords
        bytesRead = 0
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("GLOB")
            srData = input_Stream.read(size, "GLOB." + name)
            bytesRead += 8 + size
            if name == "NAME":
                self.id = cstrip(srData)
            elif name == "FNAM":
                self.type = srData
            elif name == "FLTV":
                self.value = struct.unpack("f", srData)
            # --Deleted?
            elif name == "DELE":
                self.isDeleted = True
            # --Bad record?
            else:
                raise Tes3UnknownSubRecord(self.inName, name, self.name)

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        out.packSub0("NAME", self.id)
        if getattr(self, "isDeleted", False):
            out.packSub("DELE", "i", 0)
            return
        out.packSub("FNAM", self.type)
        out.packSub("FLTV", "f", self.value)


class Info_Test:
    """INFO function/variable test. Equates to SCVR + INTV/FLTV."""

    def __init__(self, type, func, oper, text="", value=0):
        """Initialization."""
        self.type = type
        self.func = func
        self.oper = oper
        self.text = text
        self.value = value

    def dumpData(self, out, index):
        """Dumps self into specified out stream with specified SCVR index value."""
        # --SCVR
        out.pack(
            "4siBB2sB",
            "SCVR",
            5 + len(self.text),
            index + 48,
            self.type,
            self.func,
            self.oper,
        )
        if self.text:
            out.write(self.text)
        # --Value
        if type(self.value) is int:
            out.packSub("INTV", "i", self.value)
        else:
            out.packSub("FLTV", "f", self.value)


class Info(Record):
    """INFO record. Dialog/journal entry. This version is complete."""

    def __init__(
        self, name="INFO", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialization."""
        # --Info Id
        self.id = ""
        self.nextId = ""
        self.prevId = ""
        # --Text/Script
        self.text = None
        self.script = None
        self.speak = None
        self.qflag = 0  # 0 nothing, 1 name, 2 finished, 3 restart.
        # --Unknown
        self.type = 0  # --Same as for dial.
        self.unk02 = 0
        # --Speaker Tests
        self.spDisp = 0
        self.spSex = -1
        self.spRank = -1
        self.spId = None
        self.spRace = None
        self.spClass = None
        self.spFaction = None
        # --Cell, PC
        self.cell = None
        self.pcRank = -1
        self.pcFaction = None
        # --Other Tests
        self.tests = [0, 0, 0, 0, 0, 0]
        # --Deleted?
        self.isDeleted = False
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        """Loads from input_Stream/internal data."""
        # --Read subrecords
        bytesRead = 0
        curTest = None
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("INFO")
            srData = input_Stream.read(size, "INFO." + name)
            bytesRead += 8 + size
            # --Ids
            if name == "INAM":
                self.id = cstrip(srData)
            elif name == "PNAM":
                self.prevId = cstrip(srData)
            elif name == "NNAM":
                self.nextId = cstrip(srData)
            # --Text/Script
            elif name == "NAME":
                self.text = srData
            elif name == "BNAM":
                self.script = srData
            elif name == "SNAM":
                self.speak = srData
            # --Quest flags
            elif name == "QSTN":
                self.qflag = 1
            elif name == "QSTF":
                self.qflag = 2
            elif name == "QSTR":
                self.qflag = 3
            # --String/Value Tests
            elif name == "DATA":
                (
                    self.type,
                    self.spDisp,
                    self.spRank,
                    self.spSex,
                    self.pcRank,
                    self.unk02,
                ) = struct.unpack("2i4B", srData)
            elif name == "ONAM":
                self.spId = cstrip(srData)
            elif name == "RNAM":
                self.spRace = cstrip(srData)
            elif name == "CNAM":
                self.spClass = cstrip(srData)
            elif name == "FNAM":
                self.spFaction = cstrip(srData)
            elif name == "ANAM":
                self.cell = cstrip(srData)
            elif name == "DNAM":
                self.pcFaction = cstrip(srData)
            # --Function/Value Tests
            elif name == "SCVR":
                (index, type, func, oper) = struct.unpack("BB2sB", srData[:5])
                text = srData[5:]
                curTest = Info_Test(type, func, oper, text)
                self.tests[index - 48] = curTest
            elif name == "INTV":
                (curTest.value,) = struct.unpack("i", srData)
            elif name == "FLTV":
                (curTest.value,) = struct.unpack("f", srData)
            # --Deleted?
            elif name == "DELE":
                self.isDeleted = True
            # --Bad record?
            else:
                raise Tes3UnknownSubRecord(self.inName, name, self.name)

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        out.packSub0("INAM", self.id)
        out.packSub0("PNAM", self.prevId)
        out.packSub0("NNAM", self.nextId)
        if not self.isDeleted:
            out.packSub(
                "DATA",
                "2i4B",
                self.type,
                self.spDisp,
                self.spRank,
                self.spSex,
                self.pcRank,
                self.unk02,
            )
        if self.spId:
            out.packSub0("ONAM", self.spId)
        if self.spRace:
            out.packSub0("RNAM", self.spRace)
        if self.spClass:
            out.packSub0("CNAM", self.spClass)
        if self.spFaction:
            out.packSub0("FNAM", self.spFaction)
        if self.cell:
            out.packSub0("ANAM", self.cell)
        if self.pcFaction:
            out.packSub0("DNAM", self.pcFaction)
        if self.speak:
            out.packSub0("SNAM", self.speak)
        if self.text:
            out.packSub("NAME", self.text)
        if self.qflag == 0:
            pass
        if self.qflag == 1:
            out.packSub("QSTN", "\x01")
        if self.qflag == 2:
            out.packSub("QSTF", "\x01")
        if self.qflag == 3:
            out.packSub("QSTR", "\x01")
        for index, test in enumerate(self.tests):
            if test:
                test.dumpData(out, index)
        if self.script:
            out.packSub("BNAM", self.script)
        if self.isDeleted:
            out.pack("DELE", "i", 0)

    def compactTests(self, mode="TOP"):
        """Compacts test array. I.e., moves test up into any empty slots if present.
        mode: 'TOP' Eliminate only leading empty tests. [0,0,1,0,1] >> [1,0,1]
        mode: 'ALL' Eliminat all empty tests. [0,0,1,0,1] >> [1,1]"""
        if tuple(self.tests) == (0, 0, 0, 0, 0, 0):
            return False
        if mode == "TOP":
            newTests = self.tests[:]
            while newTests and not newTests[0]:
                del newTests[0]
        else:
            newTests = [test for test in self.tests if test]
        while len(newTests) < 6:
            newTests.append(0)
        if tuple(self.tests) != tuple(newTests):
            self.tests = newTests
            self.setChanged()
            return True


class InfoS(Record):
    """INFO record. Dialog/journal entry.
    This is a simpler version of the info record. It expands just enough for
    dialog import/export."""

    def __init__(
        self, name="INFO", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        # --Arrays
        self.id = None
        self.nextId = None
        self.prevId = None
        self.spId = None
        self.text = None
        self.records = []  # --Subrecords, of course
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        # --Read subrecords
        bytesRead = 0
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("INFO")
            bytesRead += 8 + size
            record = SubRecord(name, size, input_Stream)
            self.records.append(record)
            # --Info Id?
            if name == "INAM":
                self.id = cstrip(record.data)
            elif name == "PNAM":
                self.prevId = cstrip(record.data)
            elif name == "NNAM":
                self.nextId = cstrip(record.data)
            # --Speaker?
            elif name == "ONAM":
                self.spId = cstrip(record.data)
            # --Text?
            elif name == "NAME":
                self.text = record.data

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        # --Get sizes
        for record in self.records:
            # --Text
            if record.name == "NAME":
                # --Truncate text?
                if len(self.text) > 511:
                    self.text = self.text[:511]
                record.data = self.text
                record.size = len(self.text)
            # --Speaker
            elif record.name == "ONAM":
                record.data = self.spId + "\x00"
                record.size = len(self.spId) + 1
            record.getSize()
            record.dump(out)


class Cell_Acdt(SubRecord):
    """In-game character attributes sub-record."""

    pass


class Cell_Chrd(SubRecord):
    """In-game character skill sub-record."""

    pass


class Cell_Frmr:
    """Proxy for FRMR/NAME record combo. Exists only to keep other functions from getting confused."""

    def __init__(self):
        self.name = "FRMR_PROXY"


class Cell_Objects:
    """Objects in cell. Combines both early and temp objects."""

    def __init__(self, cell):
        self.cell = cell

    def list(self):
        """Return combined list of early and temp objects."""
        return self.cell.objects + self.cell.tempObjects

    def remove(self, object):
        """Remove specified object from appropriate list."""
        if object in self.cell.objects:
            self.cell.objects.remove(object)
        else:
            self.cell.tempObjects.remove(object)
        self.cell.setChanged()

    def replace(self, object, newObject):
        """Replace old object with new object."""
        if object in self.cell.objects:
            objIndex = self.cell.objects.index(object)
            self.cell.objects[objIndex] = newObject
        else:
            objIndex = self.cell.tempObjects.index(object)
            self.cell.tempObjects[objIndex] = newObject
        self.cell.setChanged()

    def isTemp(self, object):
        """Return True if object is a temp object."""
        return object in self.tempObjects


class Book(Record):
    """BOOK record."""

    def __init__(
        self, name="BOOK", size=0, delFlag=0, recFlag=0, input_Stream=None, unpack=False
    ):
        """Initialization."""
        self.model = "Add Art File"
        self.teaches = -1
        self.weight = self.value = self.isScroll = self.enchantPoints = 0
        self.title = self.script = self.icon = self.text = self.enchant = None
        Record.__init__(self, name, size, delFlag, recFlag, input_Stream, unpack)

    def loadData(self, input_Stream):
        """Loads from input_Stream/internal data."""
        self.isDeleted = False
        # --Read subrecords
        bytesRead = 0
        while bytesRead < self.size:
            (name, size) = input_Stream.unpackSubHeader("BOOK")
            srData = input_Stream.read(size, "BOOK." + name)
            bytesRead += 8 + size
            if name == "NAME":
                self.id = cstrip(srData)
            elif name == "MODL":
                self.model = cstrip(srData)
            elif name == "FNAM":
                self.title = cstrip(srData)
            elif name == "BKDT":
                (
                    self.weight,
                    self.value,
                    self.isScroll,
                    self.teaches,
                    self.enchantPoints,
                ) = struct.unpack("f4i", srData)
            elif name == "SCRI":
                self.script = cstrip(srData)
            elif name == "ITEX":
                self.icon = cstrip(srData)
            elif name == "TEXT":
                self.text = cstrip(srData)
            elif name == "ENAM":
                self.enchant = cstrip(srData)
            # --Deleted?
            elif name == "DELE":
                self.isDeleted = True
            # --Bad record?
            else:
                raise Tes3Error(
                    self.inName,
                    _("Extraneous subrecord (%s) in %s record.") % (name, self.name),
                )

    def dumpData(self, out):
        """Dumps state into out. Called by getSize()."""
        out.packSub0("NAME", self.id)
        if getattr(self, "isDeleted", False):
            out.packSub("DELE", "i", 0)
            return
        out.packSub0("MODL", self.model)
        if self.title:
            out.packSub0("FNAM", self.title)
        out.packSub(
            "BKDT",
            "f4i",
            self.weight,
            self.value,
            self.isScroll,
            self.teaches,
            self.enchantPoints,
        )
        if self.script:
            out.packSub0("SCRI", self.script)
        if self.icon:
            out.packSub0("ITEX", self.icon)
        if self.text:
            out.packSub0("TEXT", self.text)
        if self.enchant:
            out.packSub0("TEXT", self.enchant)


class Tes3Writer:
    """Wrapper around an TES3 output stream. Adds utility functions."""

    def __init__(self, out):
        """Initialize."""
        self.out = out

    # --Stream Wrapping
    def write(self, data):
        self.out.write(data)

    def getvalue(self):
        return self.out.getvalue()

    def close(self):
        self.out.close()

    # --Additional functions.
    def pack(self, format, *data):
        self.out.write(struct.pack(format, *data))

    def packSub(self, type, data, *values):
        """Write subrecord header and data to output stream.
        Call using either packSub(type,data), or packSub(type,format,values)."""
        if values:
            data = struct.pack(data, *values)
        self.out.write(struct.pack("4si", type, len(data)))
        self.out.write(data)

    def packSub0(
        self, type, data
    ):  # Polemos: todo: Are unicode chars allowed in a saved game?
        """Write subrecord header and data + null terminator to output stream."""
        self.out.write(struct.pack("4si", type, len(data) + 1))
        self.out.write(data)
        self.out.write("\x00")


class Tes3Reader:
    """Wrapper around an TES3 file in read mode.
    Will throw a Tes3ReadError if read operation fails to return correct size."""

    def __init__(self, inName, input_Stream):
        """Initialize."""
        self.inName = inName
        self.input_Stream = input_Stream
        # --Get input_Stream size
        curPos = input_Stream.tell()
        input_Stream.seek(0, 2)
        self.size = input_Stream.tell()
        input_Stream.seek(curPos)

    # --IO Stream ------------------------------------------
    def seek(self, offset, whence=0, recType="----"):
        """File seek."""
        if whence == 1:
            newPos = self.input_Stream.tell() + offset
        elif whence == 2:
            newPos = self.size + offset
        else:
            newPos = offset
        if newPos < 0 or newPos > self.size:
            raise Tes3ReadError(self.inName, recType, newPos, self.size)
        self.input_Stream.seek(offset, whence)

    def tell(self):
        """File tell."""
        return self.input_Stream.tell()

    def close(self):
        """Close file."""
        self.input_Stream.close()

    def atEnd(self):
        """Return True if current read position is at EOF."""
        return self.input_Stream.tell() == self.size

    # --Read/unpack ----------------------------------------
    def read(self, size, recType="----"):
        """Read from file."""
        endPos = self.input_Stream.tell() + size
        if endPos > self.size:
            raise Tes3SizeError(self.inName, recType, endPos, self.size)
        return self.input_Stream.read(size)

    def unpack(self, format, size, recType="-----"):
        """Read file and unpack according to struct format."""
        endPos = self.input_Stream.tell() + size
        if endPos > self.size:
            raise Tes3ReadError(self.inName, recType, endPos, self.size)
        return struct.unpack(format, self.input_Stream.read(size))

    def unpackRecHeader(self):
        """Unpack a record header."""
        return self.unpack("4s3i", 16, "REC_HEAD")

    def unpackSubHeader(self, recType="----", expName=None, expSize=0):
        """Unpack a subrecord header. Optionally checks for match with expected name and size."""
        (name, size) = self.unpack("4si", 8, recType + ".SUB_HEAD")
        # --Match expected name?
        if expName and expName != name:
            raise Tes3Error(
                self.inName,
                _(
                    f"{recType}: Expected {expName} sub-record, but found {name} input_Streamtead."
                ),
            )
        # --Match expected size?
        if expSize and expSize != size:
            raise Tes3SizeError(self.inName, recType + "." + name, size, expSize, True)
        return (name, size)

    # --Find data ------------------------------------------
    def findSubRecord(self, subName, recType="----"):
        """Finds subrecord with specified name."""
        while not self.atEnd():
            (name, size) = self.unpack("4si", 8, recType + ".SUB_HEAD")
            if name == subName:
                return self.read(size, recType + "." + subName)
            else:
                self.seek(size, 1, recType + "." + name)
        # --Didn't find it?
        else:
            return None


class FileInfo:  # Polemos: OpenMW/TES3mp support
    """Abstract TES3 File."""

    def __init__(self, directory, name):
        """Init."""
        self.openMW = settings["openmw"]
        if not self.openMW:  # Morrowind support
            path = os.path.join(directory, name)
        if self.openMW:  # OpenMW/TES3mp support
            directory = [
                x
                for x in MWIniFile.openmw_data_files(
                    MWIniFile(settings["openmwprofile"])
                )[:]
                if os.path.isfile(os.path.join(x, name))
            ][0]
            path = os.path.join(directory, name)
        self.name = name
        self.dir = directory
        if os.path.exists(path):
            self.ctime = os.path.getctime(path)
            self.mtime = getmtime(path)
            self.size = os.path.getsize(path)
        else:
            self.ctime = time.time()
            self.mtime = time.time()
            self.size = 0
        self.tes3 = 0
        self.masterNames = tuple()
        self.masterOrder = tuple()
        self.masterSizes = {}
        self.madeBackup = False
        # --Ancillary storage
        self.extras = {}

    # --File type tests
    def isMod(self):
        if not self.openMW:
            return self.isEsp() or self.isEsm()
        else:
            return self.isEsp() or self.isEsm() or self.isOmwgame() or self.isOmwaddon()

    def isEsp(self):
        return self.name[-3:].lower() == "esp"

    def isEsm(self):
        return self.name[-3:].lower() == "esm"

    def isEss(self):
        return self.name[-3:].lower() == "ess"

    def isOmwgame(self):
        return self.name[-7:].lower() == "omwgame"

    def isOmwaddon(self):
        return self.name[-8:].lower() == "omwaddon"

    def isOmwsave(self):
        return self.name[-7:].lower() == "omwsave"

    def sameAs(self, fileInfo):
        return (
            (self.size == fileInfo.size)
            and (self.mtime == fileInfo.mtime)
            and (self.ctime == fileInfo.ctime)
            and (self.name == fileInfo.name)
        )

    def refresh(self):
        path = os.path.join(self.dir, self.name)
        self.ctime = os.path.getctime(path)
        self.mtime = getmtime(path)
        self.size = os.path.getsize(path)
        if self.tes3:
            self.getHeader()

    def setType(self, type):
        self.getHeader()
        if type == "esm":
            self.tes3.hedr.fileType = 1
        elif type == "esp":
            self.tes3.hedr.fileType = 0
        elif type == "ess":
            self.tes3.hedr.fileType = 32
        elif self.openMW:
            if type == "omwgame":
                self.tes3.hedr.fileType = 1
            elif type == "omwaddon":
                self.tes3.hedr.fileType = 0
            elif type == "omwsave":  # todo: fix for OpenMW
                self.tes3.hedr.fileType = 32
        self.tes3.hedr.setChanged()
        self.writeHedr()

    def getHeader(self):
        path = os.path.join(self.dir, self.name)
        try:
            input_Stream = Tes3Reader(self.name, file(path, "rb"))
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            if name != "TES3":
                raise Tes3Error(self.name, _("Expected TES3, but got ") + name)
            self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        except (struct.error, rex):
            input_Stream.close()
            raise Tes3Error(self.name, f"Struct.error: {rex}")
        except (Tes3Error, error):
            input_Stream.close()
            error.inName = self.name
            raise
        # --Master sizes (for getMasterStatus)
        masterNames = []
        self.masterSizes.clear()
        for master, size in self.tes3.masters:
            self.masterSizes[master] = size
            masterNames.append(master)
        self.masterNames = tuple(masterNames)
        self.masterOrder = tuple()  # --Reset to empty for now
        # --Free some memory
        self.tes3.data = None
        self.tes3.others = None
        # --Done
        input_Stream.close()

    def getMasterStatus(self, masterName):
        # --Exists?
        if not modInfos.has_key(masterName):
            return 30
        # --Sizes differ?
        elif (masterName in self.masterSizes) and (
            self.masterSizes[masterName] != modInfos[masterName].size
        ):
            return 10
        # --Okay?
        else:
            return 0

    def getStatus(self):
        status = 0
        # --Worst status from masters
        for masterName in self.masterSizes.keys():
            status = max(status, self.getMasterStatus(masterName))
        # --Missing files?
        if status == 30:
            return status
        # --Natural misordering?
        self.masterOrder = modInfos.getLoadOrder(self.masterNames)
        if self.masterOrder != self.masterNames:
            return 20
        else:
            return status

    # --New File
    def writeNew(self, masters=[], mtime=0):
        """Creates a new file with the given name, masters and mtime."""
        tes3 = Tes3()
        tes3.hedr = Tes3_Hedr("HEDR", 0)
        if self.isEsp():
            tes3.hedr.fileType = 0
        elif self.isEsm():
            tes3.hedr.fileType = 1
        elif self.isEss():
            tes3.hedr.fileType = 32
        for master in masters:
            tes3.masters.append((master, modInfos[master].size))
        tes3.hedr.setChanged()
        tes3.setChanged()
        # --Write it
        path = os.path.join(self.dir, self.name)
        out = file(path, "wb")
        tes3.getSize()
        tes3.dump(out)
        out.close()
        self.setMTime(mtime)

    def writeHedr(self):
        """Writes hedr subrecord to file, overwriting old hedr."""
        path = os.path.join(self.dir, self.name)
        out = file(path, "r+b")
        out.seek(16)  # --Skip to Hedr record data
        self.tes3.hedr.getSize()
        self.tes3.hedr.dump(out)
        out.close()
        # --Done
        self.getHeader()
        self.setMTime()

    def writeDescription(self, description):
        """Sets description to specified text and then writes hedr."""
        description = description[: min(255, len(description))]
        self.tes3.hedr.description = description
        self.tes3.hedr.setChanged()
        self.writeHedr()

    def writeAuthor(self, author):
        """Sets author to specified text and then writes hedr."""
        author = author[: min(32, len(author))]
        self.tes3.hedr.author = author
        self.tes3.hedr.setChanged()
        self.writeHedr()

    def writeAuthorWM(self):
        """Marks author field with " [wm]" to indicate Mash modification."""
        author = self.tes3.hedr.author
        if "[wm]" not in author and len(author) <= 27:
            self.writeAuthor(author + " [wm]")

    def setMTime(self, mtime=0):
        """Sets mtime. Defaults to current value (i.e. reset)."""
        mtime = mtime or self.mtime
        path = os.path.join(self.dir, self.name)
        os.utime(path, (time.time(), mtime))
        self.mtime = getmtime(path)

    def makeBackup(self, forceBackup=False):
        if self.madeBackup and not forceBackup:
            return
        # --Backup Directory
        backupDir = os.path.join(self.dir, settings["mosh.fileInfo.backupDir"])
        if not os.path.exists(backupDir):
            os.makedirs(backupDir)
        # --File Path
        original = os.path.join(self.dir, self.name)
        # --Backup
        backup = os.path.join(backupDir, self.name)
        shutil.copy(original, backup)
        # --First backup
        firstBackup = backup + "f"
        if not os.path.exists(firstBackup):
            shutil.copy(original, firstBackup)
        # --Done
        self.madeBackup = True

    def getStats(self):
        stats = self.stats = {}
        path = os.path.join(self.dir, self.name)
        input_Stream = Tes3Reader(self.name, file(path, "rb"))
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (type, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            if type not in stats:
                stats[type] = (1, size)
            else:
                count, cumSize = stats[type]
                stats[type] = (count + 1, cumSize + size + 16)  # --16B in header
            # --Seek to next record
            input_Stream.seek(size, 1, "Record")
        # --Done
        input_Stream.close()

    # --Snapshot Parameters
    def getNextSnapshot(
        self,
    ):  # Polemos: Unicode fix. Strange one. Was it mine? Questions, questions, questions... (b)
        destDir = os.path.join(
            self.dir, settings["mosh.fileInfo.snapshotDir"]
        )  # .encode('utf8')
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        (root, ext) = os.path.splitext(self.name)
        destName = root + "-00" + ext
        separator = "-"
        snapLast = ["00"]
        # --Look for old snapshots.
        reSnap = re.compile("^" + root + r"-([0-9\.]*[0-9]+)" + ext + "$")
        for fileName in scandir.listdir(destDir):
            maSnap = reSnap.match(fileName)
            if not maSnap:
                continue
            snapNew = maSnap.group(1).split(".")
            # --Compare shared version numbers
            sharedNums = min(len(snapNew), len(snapLast))
            for index in xrange(sharedNums):
                (numNew, numLast) = (int(snapNew[index]), int(snapLast[index]))
                if numNew > numLast:
                    snapLast = snapNew
                    continue
            # --Compare length of numbers
            if len(snapNew) > len(snapLast):
                snapLast = snapNew
                continue
        # --New
        # snapLast[-1] = ('%0'+`len(snapLast[-1])`+'d') % (int(snapLast[-1])+1,)
        snapLast[-1] = f"{int(snapLast[-1])+1:0{len(snapLast[-1])}d}"
        destName = root + separator + (".".join(snapLast)) + ext
        wildcard = root + "*" + ext
        wildcard = _("%s Snapshots|%s|All Snapshots|*.esp;*.esm;*.ess") % (
            root,
            wildcard,
        )
        return (destDir, destName, wildcard)


class FileInfos:  # + OpenMW/TES3mp support

    def __init__(self, dir, factory=FileInfo):
        """Init with specified directory and specified factory type."""
        self.OpenMW = settings["openmw"]
        self.dir = dir
        self.factory = factory
        self.data = {}
        if not self.OpenMW:  # Morrowind support
            self.table = Table(os.path.join(self.dir, "Mash", "Table.pkl"))
        if self.OpenMW:  # OpenMW/TES3mp support
            self.table = Table(os.path.join(MashDir, "openmw", "Table.pkl"))
        self.corrupted = {}  # --errorMessage = corrupted[fileName]

    # --Dictionary Emulation
    def __containput_Stream__(self, key):
        """Dictionary emulation."""
        return key in self.data

    def __getitem__(self, key):
        """Dictionary emulation."""
        try:
            return self.data[key]  # Polemos: Hack' a doro, In case the file where
        except:
            pass  # the key is pointing is missing.Be Exceptional!

    def __setitem__(self, key, value):
        """Dictionary emulation."""
        self.data[key] = value

    def __delitem__(self, key):
        """Dictionary emulation."""
        del self.data[key]

    def keys(self):
        """Dictionary emulation."""
        return self.data.keys()

    def has_key(self, key):
        """Dictionary emulation."""
        return self.data.has_key(key)

    def get(self, key, default):
        """Dictionary emulation."""
        return self.data.get(key, default)

    # --Refresh File
    def refreshFile(self, fileName):
        try:
            fileInfo = self.factory(self.dir, fileName)
            fileInfo.getHeader()
            self.data[fileName] = fileInfo
        except (Tes3Error, error):
            self.corrupted[fileName] = error.message
            if fileName in self.data:
                del self.data[fileName]
            raise

    def refresh(self):
        """Morrowind - OpenMW/TES3mp junction."""
        if not self.OpenMW:  # Morrowind support
            return self.refresh_Morrowind()
        if self.OpenMW:  # OpenMW/TES3mp support
            return self.refresh_OpenMW()

    def refresh_OpenMW(self):
        data = self.data
        oldList = data.keys()
        newList = []
        added = []
        updated = []
        deleted = []
        if self.dir == os.path.join(settings["openmwprofile"], "Saves"):
            if not os.path.exists(self.dir):
                os.makedirs(self.dir)
            contents = scandir.listdir(self.dir)
            type_po = "saves"
        else:
            contents = MWIniFile(settings["openmwprofile"]).openmw_data_files()
            type_po = "mods"
        for dir in contents:  # --Loop over files in directory
            if type_po == "mods":
                if os.path.exists(dir):
                    self.dir = dir
            for fileName in scandir.listdir(self.dir):
                fileName = fileName
                # --Right file type?
                filePath = os.path.join(self.dir, fileName)
                if not os.path.isfile(filePath) or not self.rightFileType(fileName):
                    continue
                fileInfo = self.factory(self.dir, fileName)
                if fileName not in oldList:  # --New file?
                    try:
                        fileInfo.getHeader()
                    except (Tes3Error, error):  # --Bad header?
                        self.corrupted[fileName] = error.message
                        continue
                    else:  # --Good header?
                        if fileName in self.corrupted:
                            del self.corrupted[fileName]
                        added.append(fileName)
                        data[fileName] = fileInfo
                elif not fileInfo.sameAs(data[fileName]):  # --Updated file?
                    try:
                        fileInfo.getHeader()
                        data[fileName] = fileInfo
                    except (Tes3Error, error):  # --Bad header?
                        self.corrupted[fileName] = error.message
                        del self.data[fileName]
                        continue
                    else:  # --Good header?
                        if fileName in self.corrupted:
                            del self.corrupted[fileName]
                        updated.append(fileName)
                # --No change?
                newList.append(fileName)
        for fileName in oldList:  # --Any files deleted?
            if fileName not in newList:
                deleted.append(fileName)
                del self.data[fileName]
        return len(added) or len(updated) or len(deleted)

    def refresh_Morrowind(self):
        data = self.data
        oldList = data.keys()
        newList = []
        added = []
        updated = []
        deleted = []
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
        for fileName in scandir.listdir(self.dir):  # --Loop over files in directory
            fileName = fileName
            # --Right file type?
            filePath = os.path.join(self.dir, fileName)
            if not os.path.isfile(filePath) or not self.rightFileType(fileName):
                continue
            fileInfo = self.factory(self.dir, fileName)
            if fileName not in oldList:  # --New file?
                try:
                    fileInfo.getHeader()
                except (Tes3Error, error):  # --Bad header?
                    self.corrupted[fileName] = error.message
                    continue
                else:  # --Good header?
                    if fileName in self.corrupted:
                        del self.corrupted[fileName]
                    added.append(fileName)
                    data[fileName] = fileInfo
            elif not fileInfo.sameAs(data[fileName]):  # --Updated file?
                try:
                    fileInfo.getHeader()
                    data[fileName] = fileInfo
                except (Tes3Error, error):  # --Bad header?
                    self.corrupted[fileName] = error.message
                    del self.data[fileName]
                    continue
                else:  # --Good header?
                    if fileName in self.corrupted:
                        del self.corrupted[fileName]
                    updated.append(fileName)
            # --No change?
            newList.append(fileName)
        for fileName in oldList:  # --Any files deleted?
            if fileName not in newList:
                deleted.append(fileName)
                del self.data[fileName]
        return len(added) or len(updated) or len(deleted)

    def rightFileType(self, fileName):  # --Right File Type? [ABSTRACT]
        """Bool: filetype (extension) is correct for subclass. [ABSTRACT]"""
        raise AbstractError

    def rename(self, oldName, newName):  # --Rename
        """Renames member file from oldName to newName."""
        # --Update references
        fileInfo = self[oldName]
        self[newName] = self[oldName]
        del self[oldName]
        self.table.moveRow(oldName, newName)
        # --FileInfo
        fileInfo.name = newName
        # --File system
        newPath = os.path.join(fileInfo.dir, newName)
        oldPath = os.path.join(fileInfo.dir, oldName)
        renameFile(oldPath, newPath)
        # --Done
        fileInfo.madeBackup = False

    def delete(self, fileName):  # --Delete
        """Deletes member file."""
        fileInfo = self[fileName]
        # --File
        filePath = os.path.join(fileInfo.dir, fileInfo.name)
        os.remove(filePath)
        # --Table
        self.table.delRow(fileName)
        # --Misc. Editor backups
        for ext in (".bak", ".tmp", ".old"):
            backPath = filePath + ext
            if os.path.exists(backPath):
                os.remove(backPath)
        # --Backups
        backRoot = os.path.join(
            fileInfo.dir, settings["mosh.fileInfo.backupDir"], fileInfo.name
        )
        for backPath in (backRoot, backRoot + "f"):
            if os.path.exists(backPath):
                os.remove(backPath)
        self.refresh()

    def moveIsSafe(self, fileName, destDir):  # --Move Exists
        """Bool: Safe to move file to destDir."""
        return not os.path.exists(os.path.join(destDir, fileName))

    def move(self, fileName, destDir):  # --Move
        """Moves member file to destDir. Will overwrite!"""
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        srcPath = os.path.join(self.dir, fileName)
        destPath = os.path.join(destDir, fileName)
        renameFile(srcPath, destPath)
        self.refresh()

    def copy(self, fileName, destDir, destName=None, setMTime=False):  # --Copy
        """Copies member file to destDir. Will overwrite!"""
        if not os.path.exists(destDir):
            os.makedirs(destDir)
        if not destName:
            destName = fileName
        srcPath = os.path.join(self.dir, fileName)
        destPath = os.path.join(destDir, destName)
        if os.path.exists(destPath):
            os.remove(destPath)
        shutil.copyfile(srcPath, destPath)
        if setMTime:
            mtime = getmtime(srcPath)
            os.utime(destPath, (time.time(), mtime))
        self.refresh()


class ModInfo(FileInfo):
    """Return mod status."""

    def isWellOrdered(self):
        """True if it is ordered correctly by datetime."""
        try:
            return not modInfos.doubleTime[self.mtime]  # Happens...
        except:
            pass

    def isExOverLoaded(self):
        """True if it belongs to an exclusion group that is overloaded."""
        maExGroup = reExGroup.match(self.name)
        if not (mwIniFile.isLoaded(self.name) and maExGroup):
            return False
        else:
            return maExGroup.group(1) in mwIniFile.exOverLoaded

    def setMTime(self, mtime=0):
        """Sets mtime. Defaults to current value (i.e. reset)."""
        mtime = mtime or self.mtime
        FileInfo.setMTime(self, mtime)
        modInfos.mtimes[self.name] = mtime


class ModInfos(FileInfos):

    def __init__(self, dir, factory=ModInfo):
        """Init."""
        FileInfos.__init__(self, dir, factory)
        self.OpenMW = settings["openmw"]
        self.resetMTimes = settings["mosh.modInfos.resetMTimes"]
        self.mtimes = self.table.getColumn("mtime")
        self.mtimesReset = []  # --Files whose mtimes have been reset.
        self.doubleTime = {}
        self.objectMaps = None

    def refreshFile(self, fileName):
        """Refresh File."""
        try:
            FileInfos.refreshFile(self, fileName)
        finally:
            self.refreshDoubleTime()

    def refresh(self):
        """Refresh."""
        hasChanged = FileInfos.refresh(self)
        if hasChanged:
            # --Reset MTimes?
            if self.resetMTimes:
                self.refreshMTimes()
            # --Any load files disappeared?
            for loadFile in mwIniFile.loadFiles[:]:
                if loadFile not in self.data:
                    self.unload(loadFile)
            self.refreshDoubleTime()
        # --Update mwIniLoadOrder
        mwIniFile.loadOrder = modInfos.getLoadOrder(mwIniFile.loadFiles)
        if self.OpenMW:
            mwIniFile.safeSave()
        return hasChanged

    def refreshMTimes(self):
        """Remember/reset mtimes of member files."""
        del self.mtimesReset[:]
        for fileName, fileInfo in self.data.items():
            oldMTime = self.mtimes.get(fileName, fileInfo.mtime)
            self.mtimes[fileName] = oldMTime
            # --Reset mtime?
            if fileInfo.mtime != oldMTime and oldMTime != -1:
                fileInfo.setMTime(oldMTime)
                self.mtimesReset.append(fileName)

    def refreshDoubleTime(self):
        """Refresh doubletime dictionary."""
        doubleTime = self.doubleTime
        doubleTime.clear()
        for modInfo in self.data.values():
            mtime = modInfo.mtime
            doubleTime[mtime] = doubleTime.has_key(mtime)
        # --Refresh MWIni File too
        mwIniFile.refreshDoubleTime()

    def rightFileType(self, fileName):
        """Bool: File is a mod."""
        if not self.OpenMW:
            fileExt = fileName[-4:].lower()
            return fileExt == ".esp" or fileExt == ".esm"
        else:
            fileExt0 = fileName[-4:].lower()
            fileExt1 = fileName[-9:].lower()
            fileExt2 = fileName[-8:].lower()
            return (
                fileExt0 == ".esp"
                or fileExt0 == ".esm"
                or fileExt1 == ".omwaddon"
                or fileExt2 == ".omwgame"
            )

    def getVersion(self, fileName):
        """Extracts and returns version number for fileName from tes3.hedr.description."""
        if not fileName in self.data or not self.data[fileName].tes3:
            return ""
        maVersion = reVersion.search(self.data[fileName].tes3.hedr.description)
        return (maVersion and maVersion.group(2)) or ""

    def circularMasters(self, stack, masters=None):
        """Circular Masters."""
        stackTop = stack[-1]
        masters = masters or (stackTop in self.data and self.data[stackTop].masterNames)
        if not masters:
            return False
        for master in masters:
            if master in stack:
                return True
            if self.circularMasters(stack + [master]):
                return True
        return False

    def getLoadOrder(self, modNames, asTuple=True):  # --Get load order
        """Sort list of mod names into their load order. ASSUMES MODNAMES ARE UNIQUE!!!"""
        data = self.data
        modNames = list(modNames)  # --Don't do an in-place sort.
        modNames.sort(key=lambda a: (a in data) and data[a].mtime)  # --Sort on modified
        if not self.OpenMW:
            modNames.sort(key=lambda a: a[-1].lower())  # --Sort on esm/esp
        elif self.OpenMW:
            tmp_modNamesESM = [x for x in modNames if x[len(x) - 3 :] in ("esm", "ame")]
            tmp_modNamesESP = [x for x in modNames if x[len(x) - 3 :] in ("esp", "don")]
            modNames = tmp_modNamesESM + tmp_modNamesESP

        # --Match Bethesda's esm sort order
        #  - Start with masters in chronological order.
        #  - For each master, if it's masters (mm's) are not already in list,
        #    then place them ahead of master... but in REVERSE order. E.g., last
        #    grandmaster will be first to be added.
        def preMaster(modName, modDex):
            """If necessary, move grandmasters in front of master -- but in reverse order."""
            if self.data.has_key(modName):
                mmNames = list(self.data[modName].masterNames[:])
                mmNames.reverse()
                for mmName in mmNames:
                    if mmName in modNames:
                        mmDex = modNames.index(mmName)
                        # --Move master in front and pre-master it too.
                        if mmDex > modDex:
                            del modNames[mmDex]
                            modNames.input_Streamert(modDex, mmName)
                            modDex = 1 + preMaster(mmName, modDex)
            return modDex

        # --Read through modNames.
        modDex = 1
        while modDex < len(modNames):
            modName = modNames[modDex]
            if not self.OpenMW:
                if modName[-1].lower() != "m":
                    break
            elif self.OpenMW:
                if modName[len(modName) - 3 :] in ("esp", "don"):
                    break
            if self.circularMasters([modName]):
                modDex += 1
            else:
                modDex = 1 + preMaster(modName, modDex)
        # --Convert? and return
        if asTuple:
            return tuple(modNames)
        else:
            return modNames

    def isLoaded(self, fileName):  # --Loading
        """True if fileName is in the load list."""
        return mwIniFile.isLoaded(fileName)

    def load(self, fileNames, doSave=True):  # Polemos: Speed up
        """Adds file to load list."""
        if type(fileNames) in [str, unicode]:
            fileNames = [fileNames]
        # --Load masters
        modFileNames = self.keys()
        for x in fileNames:
            if x not in self.data:
                continue  # Polemos fix: In case a mod is missing
            for master, size in self[x].tes3.masters:
                if master in modFileNames and master != x:
                    self.load(master, False)
        # --Load self
        mwIniFile.load(fileNames, doSave)

    def unload(self, fileNames, doSave=True):  # Polemos: Speed up
        """Removes file from load list."""
        if type(fileNames) in [str, unicode]:
            fileNames = [fileNames]
        # --Unload fileName
        mwIniFile.unload(fileNames, False)
        # --Unload fileName's children
        loadFiles = mwIniFile.loadFiles[:]
        for loadFile in loadFiles:
            # --Already unloaded? (E.g., grandchild)
            if not mwIniFile.isLoaded(loadFile):
                continue
            # --Can happen if user does an external delete.
            if loadFile not in self.data:
                continue
            for x in fileNames:  # --One of loadFile's masters?
                for master in self[loadFile].tes3.masters:
                    if master[0] == x:
                        self.unload(loadFile, False)
                        break
        # --Save
        if doSave:
            mwIniFile.safeSave()

    def rename(self, oldName, newName):
        """Renames member file from oldName to newName."""
        isLoaded = self.isLoaded(oldName)
        if isLoaded:
            self.unload(oldName)
        FileInfos.rename(self, oldName, newName)
        self.refreshDoubleTime()
        if isLoaded:
            self.load(newName)

    def delete(self, fileName):
        """Deletes member file."""
        self.unload(fileName)
        FileInfos.delete(self, fileName)

    def move(self, fileName, destDir):
        """Moves member file to destDir."""
        self.unload(fileName)
        FileInfos.move(self, fileName, destDir)

    def getResourceReplacers(self):
        """Returns list of ResourceReplacer objects for subdirectories of Replacers directory."""
        replacers = {}
        replacerDir = os.path.join(self.dir, "Replacers")
        if not os.path.exists(replacerDir):
            return replacers
        if "mosh.resourceReplacer.applied" not in settings:
            settings["mosh.resourceReplacer.applied"] = []
        for name in scandir.listdir(replacerDir):
            path = os.path.join(replacerDir, name)
            if os.path.isdir(path):
                replacers[name] = ResourceReplacer(replacerDir, name)
        return replacers

    def addObjectMap(self, fromMod, toMod, objectMap):
        """Add an objectMap with key(fromMod,toMod)."""
        if self.objectMaps is None:
            self.loadObjectMaps()
        self.objectMaps[(fromMod, toMod)] = objectMap

    def removeObjectMap(self, fromMod, toMod):
        """Deletes objectMap with key(fromMod,toMod)."""
        if self.objectMaps is None:
            self.loadObjectMaps()
        del self.objectMaps[(fromMod, toMod)]

    def getObjectMap(self, fromMod, toMod):
        """Returns objectMap with key(fromMod,toMod)."""
        if self.objectMaps is None:
            self.loadObjectMaps()
        return self.objectMaps.get((fromMod, toMod), None)

    def getObjectMaps(self, toMod):
        """Return a dictionary of ObjectMaps with fromMod key for toMod."""
        if self.objectMaps is None:
            self.loadObjectMaps()
        subset = {}
        for key in self.objectMaps.keys():
            if key[1] == toMod:
                subset[key[0]] = self.objectMaps[key]
        return subset

    def loadObjectMaps(self):
        """Load ObjectMaps from file."""
        path = os.path.join(self.dir, settings["mosh.modInfos.objectMaps"])
        try:
            if os.path.exists(path):
                self.objectMaps = compat.uncpickle(path)
            else:
                self.objectMaps = {}
        except EOFError:  # Polemos: Fix for corrupted Updaters pkl
            import gui.dialog, wx

            if (
                gui.dialog.ErrorQuery(
                    None,
                    _(
                        "Updaters data has been corrupted and needs to be reset.\n\nClick "
                        "Yes to automatically delete the updaters data file.\n(This will make Wrye Mash forget which mods it has updated "
                        "but it will not affect your updated saves - an inconvenience really).\n\nClick No if you wish to do it "
                        "manually by deleting the following file:\n%s"
                    )
                    % path,
                )
                == wx.ID_YES
            ):
                try:
                    os.remove(path)
                except:
                    gui.dialog.ErrorMessage(
                        None,
                        _(
                            "Wrye Mash was unable to delete the file which "
                            'holds the Updaters data. You need to manually delete the following file:\n\n"%s"'
                            % path
                        ),
                    )

    def saveObjectMaps(self):
        """Save ObjectMaps to file."""
        if self.objectMaps is None:
            return
        path = os.path.join(self.dir, settings["mosh.modInfos.objectMaps"])
        outDir = os.path.split(path)[0]
        if not os.path.exists(outDir):
            os.makedirs(outDir)
        cPickle.dump(self.objectMaps, open(path, "wb"), -1)


class SaveInfo(
    FileInfo
):  # Polemos: Fixed a small (ancient again) bug with the journal.
    """Representation of a savegame file."""

    def getStatus(self):
        """Returns the status, i.e., "health" level of the savegame. Based on
        status/health of masters, plus synchronization with current load list."""
        status = FileInfo.getStatus(self)
        masterOrder = self.masterOrder
        # --File size?
        if status > 0 or len(masterOrder) > len(mwIniFile.loadOrder):
            return status
        # --Current ordering?
        if masterOrder != mwIniFile.loadOrder[: len(masterOrder)]:
            return status
        elif masterOrder == mwIniFile.loadOrder:
            return -20
        else:
            return -10

    def getJournal(self):
        """Returns the text of the journal from the savegame in slightly
        modified html format."""
        if "journal" in self.extras:
            return self.extras["journal"]
        # --Default
        self.extras["journal"] = _("[No Journal Record Found.]")
        # --Open save file and look for journal entry
        inPath = os.path.join(self.dir, self.name)
        input_Stream = Tes3Reader(self.name, file(inPath, "rb"))
        # --Raw data read
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            if name != "JOUR":
                input_Stream.seek(size, 1, name)
            # --Journal
            else:
                (subName, subSize) = input_Stream.unpackSubHeader("JOUR")
                if subName != "NAME":
                    self.extras["journal"] = _(
                        "[Error reading file.]"
                    )  # Polemos fix: removed double '='
                else:
                    reDate = re.compile(r'<FONT COLOR="9F0000">(.+?)</FONT><BR>')
                    reTopic = re.compile(r"@(.*?)#")
                    data = input_Stream.read(subSize)
                    data = reDate.sub(ReplJournalDate(), data)
                    data = reTopic.sub(r"\1", data)
                    self.extras["journal"] = cstrip(data)
                break
        # --Done
        input_Stream.close()
        # print self.extras['journal']  <== Polemos: the journal bug (easy to happen),
        # it was present at least since Melchior's version up to Yakoby's.
        return self.extras["journal"]

    def getScreenshot(self):  # Polemos fixes
        """Returns screenshot data with alpha info stripped out. If screenshot data isn't available, returns None."""
        # --Used cached screenshot, if have it.
        if "screenshot" in self.extras:
            return self.extras["screenshot"]
        # --Gets tes3 header
        path = os.path.join(self.dir, self.name)
        try:
            input_Stream = Tes3Reader(self.name, file(path, "rb"))
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            if name != "TES3":
                raise Tes3Error(self.name, _("Expected TES3, but got %s" % name))
            self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        except (struct.error, rex):
            input_Stream.close()
            raise Tes3Error(self.name, _("Struct.error: %s" % rex))
        except (Tes3Error, error):
            input_Stream.close()
            error.inName = self.name
            raise
        input_Stream.close()
        # --Get screenshot data subrecord
        for subrecord in self.tes3.others:
            if subrecord.name == "SCRS":
                # --Convert bgra array to rgb array
                buff = cStringIO.StringIO()
                for num in xrange(len(subrecord.data) / 4):
                    bb, gg, rr = struct.unpack(
                        "3B", subrecord.data[num * 4 : num * 4 + 3]
                    )
                    buff.write(struct.pack("3B", rr, gg, bb))
                rgbString = buff.getvalue()
                try:  # --Image processing (brighten, increase range)
                    rgbArray = array.array("B", rgbString)
                    rgbAvg = float(sum(rgbArray)) / len(rgbArray)
                    rgbSqAvg = float(sum(xx * xx for xx in rgbArray)) / len(rgbArray)
                    rgbSigma = math.sqrt(rgbSqAvg - rgbAvg * rgbAvg)
                    rgbScale = max(1.0, 80 / rgbSigma)

                    def remap(color):
                        color = color - rgbAvg
                        color = color * rgbScale
                        return max(0, min(255, int(color + 128)))

                except:
                    pass
                buff.seek(0)
                try:
                    [
                        buff.write(struct.pack("B", remap(ord(char))))
                        for num, char in enumerate(rgbString)
                    ]
                except:
                    pass
                screenshot = buff.getvalue()
                buff.close()
                break
        else:  # --No SCRS data
            screenshot = None
        # --Cache and return
        self.extras["screenshot"] = screenshot
        return screenshot


class SaveInfos(FileInfos):
    """Collection of saveInfos for savefiles in the saves directory."""

    # --Init
    def __init__(self, dir, factory=SaveInfo):
        FileInfos.__init__(self, dir, factory)

    # --Right File Type (Used by Refresh)
    def rightFileType(self, fileName):
        return fileName[-4:].lower() == ".ess"


class ResPack:
    """Resource package (BSA or resource replacer). This is the abstract supertype."""

    def getOrder(self):
        """Returns load order number or None if not loaded."""
        raise AbstractError

    def rename(self, newName):
        """Renames respack."""
        raise AbstractError

    def duplicate(self, newName):
        """Duplicates self with newName."""
        raise AbstractError

    def select(self):
        """Selects package."""
        raise AbstractError

    def unselect(self):
        """Unselects package."""
        raise AbstractError

    def isSelected(self):
        """Returns True if is currently selected."""
        raise AbstractError


class BSAPack(ResPack):
    """BSA file resource package."""

    pass


class ResReplacerPack(ResPack):
    """Resource replacer directory."""

    pass


class ResPacks:
    """Collection of Res Packs (BSAs and Resource Replacers)."""

    def __init__(self):
        """Initialize. Get BSA and resource replacers."""
        self.data = {}
        self.refresh()

    def refresh(self):
        """Refreshes BSA and resource replacers."""
        raise UncodedError


class RefReplacer:
    """Used by FileRefs to replace references."""

    def __init__(self, filePath=None):
        """Initialize."""
        self.srcModName = None  # --Name of mod to import records from.
        self.srcDepends = {}  # --Source mod object dependencies.
        self.newIds = {}  # --newIds[oldId] = (newId1,newId2...)
        self.newIndex = {}  # --newIndex[oldId] = Index of next newIds[oldId]
        self.usedIds = set()  # --Records to import
        if filePath:
            self.loadText(filePath)

    def loadText(self, filePath):
        """Loads replacer information from file."""
        input_Stream = file(filePath, "r")
        reComment = re.compile(r"#.*")
        reSection = re.compile(r"@ +(srcmod|replace)", re.M)
        reReplace = re.compile(r"(\w[-\w ']+)\s*:\s*(.+)")
        reNewIds = re.compile(r",\s*")
        mode = None
        for line in input_Stream:
            line = reComment.sub("", line.strip())
            maSection = reSection.match(line)
            if maSection:
                mode = maSection.group(1)
            elif not line:  # --Empty/comment line
                pass
            elif mode == "srcmod":
                self.srcModName = line
            elif mode == "replace":
                maReplace = reReplace.match(line)
                if not maReplace:
                    continue
                oldId = maReplace.group(1)
                self.newIds[oldId.lower()] = reNewIds.split(maReplace.group(2))
        input_Stream.close()

    def getNewId(self, oldId):
        """Returns newId replacement for old id."""
        oldId = oldId.lower()
        newIds = self.newIds[oldId]
        if len(newIds) == 1:
            newId = newIds[0]
        else:
            index = self.newIndex.get(oldId, 0)
            self.newIndex[oldId] = (index + 1) % len(newIds)
            newId = newIds[index]
        self.usedIds.add(newId.lower())
        return newId

    def getSrcRecords(self):
        """Returns list of records to input_Streamert into mod."""
        srcRecords = {}
        if self.srcModName and self.usedIds:
            # --Get FileRep
            srcInfo = modInfos[self.srcModName]
            fullRep = srcInfo.extras.get("FullRep")
            if not fullRep:
                fullRep = FileRep(srcInfo)
                fullRep.load()
                srcInfo.extras["FullRep"] = fullRep
            for record in fullRep.records:
                id = record.getId().lower()
                if id in self.usedIds:
                    srcRecords[id] = copy.copy(record)
        return srcRecords

    def clearUsage(self):
        """Clears usage state."""
        self.newIndex.clear()
        del self.usedIds[:]


class FileRep:
    """Abstract TES3 file representation."""

    def __init__(self, fileInfo, canSave=True, log=None, progress=None):
        """Initialize."""
        self.progress = progress or Progress()
        self.log = log or Log()
        self.fileInfo = fileInfo
        self.canSave = canSave
        self.tes3 = None
        self.records = []
        self.indexed = {}  # --record = indexed[type][id]

    def load(self, keepTypes="ALL", factory={}):
        """Load file. If keepTypes, then only keep records of type in keepTypes or factory.
        factory: dictionary mapping record type to record class. For record types
        in factory, specified class will be used and data will be kept."""
        keepAll = keepTypes == "ALL"
        keepTypes = keepTypes or set()  # --Turns None or 0 into an empty set.
        # --Header
        inPath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        input_Stream = Tes3Reader(self.fileInfo.name, file(inPath, "rb"))
        (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
        self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        # --Raw data read
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            if name in factory:
                record = factory[name](name, size, delFlag, recFlag, input_Stream)
                self.records.append(record)
            elif keepAll or name in keepTypes:
                record = Record(name, size, delFlag, recFlag, input_Stream)
                self.records.append(record)
            else:
                input_Stream.seek(size, 1, name)
        # --Done Reading
        input_Stream.close()

    def unpackRecords(self, unpackTypes):
        """Unpacks records of specified types"""
        for record in self.records:
            if record.name in unpackTypes:
                record.load(unpack=True)

    def indexRecords(self, indexTypes):
        """Indexes records of specified types."""
        indexed = self.indexed = {}
        for type in indexTypes:
            indexed[type] = {}
        for record in self.records:
            type = record.name
            if type in indexTypes:
                indexed[type][record.getId().lower()] = record

    def loadUI(self, factory={}):
        """Convenience function. Loads, then unpacks, then indexes."""
        keepTypes = self.canSave and "ALL" or tuple()
        self.load(keepTypes=keepTypes, factory=factory)
        uiTypes = set(factory.keys())
        self.unpackRecords(uiTypes)
        self.indexRecords(uiTypes)

    def getRecord(self, type, id, Class=None):
        """Gets record with corresponding type and id.
        If record doesn't exist and Class is provided, then a new input_Streamtance
        with given id is created, added to record list and indexed and then
        returned to the caller."""
        idLower = id.lower()
        typeIds = self.indexed[type]
        if idLower in typeIds:
            return typeIds[idLower]
        elif Class:
            record = Class()
            record.id = id
            self.records.append(record)
            typeIds[idLower] = record
            return record
        else:
            return None

    def setRecord(self, record):
        """Adds record to record list and indexed."""
        idLower = record.getId().lower()
        type = record.name
        typeIds = self.indexed[type]
        if idLower in typeIds:
            oldRecord = typeIds[idLower]
            index = self.records.index(oldRecord)
            self.records[index] = record
        else:
            self.records.append(record)
        typeIds[idLower] = record

    def safeSave(self):
        """Save data to file safely."""
        self.fileInfo.makeBackup()
        filePath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        tempPath = filePath + ".tmp"
        self.save(tempPath)
        renameFile(tempPath, filePath)
        self.fileInfo.setMTime()
        self.fileInfo.extras.clear()

    def save(self, outPath=None):
        """Save data to file.
        outPath -- Path of the output file to write to. Defaults to original file path.
        """
        if not self.canSave:
            raise StateError(_("input_Streamufficient data to write file."))
        if outPath is None:
            fileInfo = self.fileInfo
            outPath = os.path.join(fileInfo.dir, fileInfo.name)
        with file(outPath, "wb") as out:
            # --Tes3 Record
            self.tes3.setChanged()
            self.tes3.hedr.setChanged()
            self.tes3.hedr.numRecords = len(
                self.records
            )  # --numRecords AFTER TES3 record
            self.tes3.getSize()
            self.tes3.dump(out)
            # --Other Records
            for record in self.records:
                record.getSize()
                record.dump(out)

    def sortRecords(self):
        # --Get record type order.
        import mush

        order = 0
        typeOrder = {}
        for typeIncrement in listFromLines(mush.recordTypes):
            (type, increment) = typeIncrement.split()
            if increment == "+":
                order += 1
            typeOrder[type] = order
        # --Get ids for records. (For subsorting.)
        ids = {}
        noSubSort = {"CELL", "LAND", "PGRD", "DIAL", "INFO"}
        for record in self.records:
            recData = record.data
            if record.name in noSubSort:
                ids[record] = 0
            else:
                id = record.getId()
                ids[record] = id and id.lower()
        # --Sort
        self.records.sort(
            cmp=lambda a, b: cmp(typeOrder[a.name], typeOrder[b.name])
            or cmp(ids[a], ids[b])
        )


class FileRefs(FileRep):
    """TES3 file representation with primary focus on references, but also
    including other information used in file repair."""

    def __init__(
        self,
        fileInfo,
        skipNonCells=False,
        skipObjRecords=False,
        log=None,
        progress=None,
    ):
        canSave = not skipNonCells  # ~~Need to convert skipNonCells argument to this.
        FileRep.__init__(self, fileInfo, canSave, log, progress)
        self.skipObjRecords = skipObjRecords
        self.tes3 = None
        self.fmap = None
        self.records = []
        self.cells = []
        self.lands = {}  # --Landscapes indexed by Land.id.
        # --Save Debris Info
        self.debrisIds = {}
        # --Content records
        self.conts = []  # --Content records: CREC, CNTC, NPCC
        self.conts_id = {}
        self.cells_id = {}
        self.refs_scpt = {}
        self.scptRefs = set()
        self.isLoaded = False
        self.isDamaged = False

    # --File Handling---------------------------------------
    def setDebrisIds(self):
        """Setup to record ids to be used by WorldRefs.removeSaveDebris.
        Should be called before load or refresh."""
        for type in ["BOOK", "CREA", "GLOB", "NPC_", "LEVI", "LEVC", "FACT"]:
            if type not in self.debrisIds:
                self.debrisIds[type] = []
        # --Built-In Globals (automatically added by game engine)
        for builtInGlobal in ("monthstorespawn", "dayspassed"):
            if builtInGlobal not in self.debrisIds["GLOB"]:
                self.debrisIds["GLOB"].append(builtInGlobal)

    def refreshSize(self):
        """Return file size if needs to be updated. Else return 0."""
        if self.isLoaded:
            return 0
        else:
            return self.fileInfo.size

    def refresh(self):
        """Load data if file has changed since last load."""
        if self.isDamaged:
            raise StateError(
                self.fileInfo.name + _(": Attempted to access damaged file.")
            )
        if not self.isLoaded:
            try:
                self.load()
                self.isLoaded = True
            except (Tes3ReadError, error):
                self.isDamaged = True
                if not error.inName:
                    error.inName = self.fileInfo.name
                raise

    def load(self):
        """Load reference data from file."""
        progress = self.progress
        filePath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        self.fileSize = os.path.getsize(filePath)
        # --Localize
        cells = self.cells
        records = self.records
        canSave = self.canSave
        skipObjRecords = self.skipObjRecords
        contTypes = {"CREC", "CNTC", "NPCC"}
        levTypes = {"LEVC", "LEVI"}
        debrisIds = self.debrisIds
        debrisTypes = set(debrisIds.keys())
        # --Header
        inPath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        input_Stream = Tes3Reader(self.fileInfo.name, file(inPath, "rb"))
        (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
        self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        if not canSave:
            del self.tes3.others[:]
        # --Progress info
        progress = self.progress
        progress(0.0, "Loading " + self.fileInfo.name)
        # --Raw data read
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            # --CELL?
            if name == "CELL":
                record = Cell(
                    name, size, delFlag, recFlag, input_Stream, 0, skipObjRecords
                )
                cells.append(record)
                if canSave:
                    records.append(record)
            # --Contents
            elif canSave and name in contTypes:
                if name == "CREC":
                    record = Crec(name, size, delFlag, recFlag, input_Stream, True)
                elif name == "CNTC":
                    record = Cntc(name, size, delFlag, recFlag, input_Stream, True)
                else:
                    record = Npcc(name, size, delFlag, recFlag, input_Stream, True)
                self.conts.append(record)
                self.conts_id[record.getId()] = record
                records.append(record)
            # --File Map
            elif name == "FMAP":
                record = Fmap(name, size, delFlag, recFlag, input_Stream)
                self.fmap = record
                records.append(record)
            # --Landscapes
            elif name == "LAND":
                record = Land(name, size, delFlag, recFlag, input_Stream)
                self.lands[record.getId()] = record
                records.append(record)
            # --Scripts
            elif canSave and name == "SCPT":
                record = Scpt(name, size, delFlag, recFlag, input_Stream, True)
                records.append(record)
                if record.getRef():
                    self.refs_scpt[record] = record.getRef()
            # --Save debris info?
            elif name in debrisTypes:
                record = Record(name, size, delFlag, recFlag, input_Stream)
                id = record.getId()
                if id:
                    debrisIds[name].append(id.lower())
                if canSave:
                    records.append(record)
            # --Skip Non-cell?
            elif not canSave:
                input_Stream.seek(size, 1, name)
            # --Keep non-cell?
            else:
                records.append(Record(name, size, delFlag, recFlag, input_Stream))
        # --Done Reading
        input_Stream.close()
        # --Analyze Cells
        cntCells = 0
        progress.setMax(len(self.cells))
        for cell in self.cells:
            cell.load(None, 1)
            self.cells_id[cell.getId()] = cell
            if not canSave:
                cell.data = None  # --Free some memory
            # --Progress
            cntCells += 1
            progress(cntCells)
        # --Scripts
        if self.refs_scpt:
            self.updateScptRefs()

    def save(self, outPath=None):
        """Save data to file.
        outPath -- Path of the output file to write to. Defaults to original file path.
        """
        if not self.canSave or self.skipObjRecords:
            raise StateError(_("input_Streamufficient data to write file."))
        if not outPath:
            fileInfo = self.fileInfo
            outPath = os.path.join(fileInfo.dir, fileInfo.name)
        out = file(outPath, "wb")
        # --Tes3 Record
        self.tes3.changed = 1
        self.tes3.hedr.changed = 1
        self.tes3.hedr.numRecords = len(self.records)  # --numRecords AFTER TES3 record
        self.tes3.getSize()
        self.tes3.dump(out)
        # --Size Cell Records
        cntRecords = 0
        progress = self.progress
        progress.setMax(len(self.cells))
        progress(0.0, "Saving " + self.fileInfo.name)
        for record in self.cells:
            record.getSize()
            # --Progress
            cntRecords += 1
            progress(cntRecords)
        # --Other Records
        for record in self.records:
            record.getSize()  # --Should already be done, but just in case.
            record.dump(out)
        out.close()

    # --Renumbering-------------------------------------------------------------
    def getFirstObjectIndex(self):
        """Returns first object index number. Assumes that references are in linear order."""
        if not self.fileInfo.isEsp():
            raise StateError(_("FileRefs.renumberObjects is for esps only."))
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                if object[0] == 0:
                    return object[1]
        return 0

    def renumberObjects(self, first):
        """Offsets all local object index numbers by specified amount. FOR ESPS ONLY!
        Returns number of objects changed."""
        if not self.fileInfo.isEsp():
            raise StateError(_("FileRefs.renumberObjects is for esps only."))
        if first <= 0:
            raise ArgumentError(_("First index should be a positive integer"))
        log = self.log
        next = int(first)
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                if object[0] == 0:
                    newObject = (0, next) + object[2:]
                    objects.replace(object, newObject)
                    next += 1
        return next - first

    # --Remapping---------------------------------------------------------------
    def remap(self, newMasters, modMap, objMaps=[]):
        """Remap masters and modIndexes.
        newMasters -- New master list. Same format as Cell.masters.
        modMap -- mapping dictionary so that newModIndex = modMap[oldModIndex]
        objMaps -- ObjectIndex mapping dictionaries"""
        # --Masters
        self.tes3.masters = newMasters
        # --File mapping
        modMapKeys = modMap.keys()
        # --Remap iObjs
        cells_id = self.cells_id
        reObjNum = re.compile("[0-9A-Z]{8}$")
        for iMod, objMap in objMaps:
            cellIds = objMap.keys()
            for cellId in cellIds:
                cellObjMap = objMap[cellId]
                # --Save
                cell = cells_id.get(cellId)
                if not cell:
                    continue
                # --Objects
                objects = cell.getObjects()
                for object in objects.list():
                    # --Different mod?
                    if object[0] != iMod:
                        pass
                    # --Cell deleted?
                    elif cellObjMap == -1:
                        objects.remove(object)
                    # --Remapped object?
                    elif object[1] in cellObjMap:
                        (newIObj, objId) = cellObjMap[object[1]]
                        objIdBase = reObjNum.sub(
                            "", objId
                        )  # --Strip '00001234' id num from object
                        # --Mismatched object id?
                        if objId != objIdBase:
                            pass
                        # --Deleted object?
                        elif newIObj == -1:
                            objects.remove(object)
                        # --Remapped object?
                        else:
                            newObject = self.remapObject(object, iMod, newIObj)
                            objects.replace(object, newObject)
        self.updateScptRefs()
        # --Remap iMods
        if not modMapKeys:
            return
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                # --Remap IMod
                iMod = object[0]
                # --No change?
                if iMod not in modMapKeys:
                    pass
                # --Object deleted?
                elif modMap[iMod] == -1:
                    objects.remove(object)
                # --Object not deleted?
                else:
                    newObject = self.remapObject(object, modMap[iMod])
                    objects.replace(object, newObject)
        self.updateScptRefs()

    def remapObject(self, object, newIMod, newIObj=-1):
        """Returns an object mapped to a newMod."""
        (iMod, iObj, objId, objRecords) = object[:4]
        if newIObj == -1:
            newIObj = iObj
        newObject = (newIMod, newIObj) + object[2:]
        if objRecords and objRecords[0].name == "MVRF":
            data = cStringIO.StringIO()
            if (
                newIMod > 255 and settings["mash.extend.pluginput_Stream"]
            ):  # MWSE compatibility == enabled
                data.write(struct.pack("2i", newIMod, newIObj))
            else:
                data.write(struct.pack("i", newIObj)[:3])
                data.write(struct.pack("B", newIMod))
            objRecords[0].data = data.getvalue()
            objRecords[0].setChanged(False)
            data.close()
        # --Remap any script references
        oldRef = (iMod, iObj)
        if oldRef in self.scptRefs:
            newRef = (newIMod, newIObj)
            for scpt in self.refs_scpt.keys():
                if self.refs_scpt[scpt] == oldRef:
                    scpt.setRef(newRef)
                    self.refs_scpt[scpt] = newRef
                    # --Be sure to call updateScptRefs when finished remapping *all* objects.
        # --Done
        return newObject

    def updateScptRefs(self):
        """Updates refs_scpt and scptRefs data. Call after all objects have been remapped."""
        for scpt in self.refs_scpt.keys():
            self.refs_scpt[scpt] = scpt.getRef()
        self.scptRefs = set(self.refs_scpt.values())

    def listBadRefScripts(self):
        """Logs any scripts with bad refs."""
        if not self.log:
            return
        ids = []
        for record in self.records:
            if record.name != "SCPT":
                continue
            rnam = record.rnam
            if rnam and rnam.data == chr(255) * 4:
                ids.append(record.getId())
        if ids:
            self.log.setHeader(_("Detached Global Scripts"))
            for id in sorted(ids, key=string.lower):
                self.log(id)

    def getObjectMap(self, oldRefs):
        """Returns an iObj remapping from an old FileRefs to this FileRefs.

        This is used to update saved games from one version of a mod to a newer version.
        """
        objMap = {}  # --objMap[cellId][oldIObj] = newIObj
        # --Old cells
        for oldCell in oldRefs.cells:
            cellId = oldCell.getId()
            newCell = self.cells_id.get(cellId)
            # --Cell deleted?
            if not newCell:
                objMap[cellId] = -1
                continue
            cellObjMap = {}
            newObjects = newCell.getObjects().list()
            nextObjectIndex = {}
            # --Old Objects
            for oldObject in oldCell.getObjects().list():
                (iMod, oldIObj, objId) = oldObject[:3]
                if iMod:
                    continue  # --Skip mods to masters
                # --New Objects
                objIndex = nextObjectIndex.get(objId, 0)
                newIObj = -1  # --Delete by default
                while objIndex < len(newObjects):
                    newObject = newObjects[objIndex]
                    objIndex += 1
                    if newObject[0]:
                        continue  # --Skip mods to masters
                    if newObject[2] == objId:
                        newIObj = newObject[1]
                        break
                nextObjectIndex[objId] = objIndex
                # --Obj map has changed?
                if newIObj != oldIObj:
                    cellObjMap[oldIObj] = (newIObj, objId)
            # --Save mapping for this cell?
            if cellObjMap:
                objMap[cellId] = cellObjMap
        # --Done
        return objMap

    # --Removers ---------------------------------------------------------------
    def removeLvcrs(self):
        """Remove all LVCR refs.
        In save game, effect is to reset the spawn point."""
        count = 0
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                for objRecord in object[3]:
                    if objRecord.name == "LVCR":
                        objects.remove(object)
                        count += 1
                        break
        return count

    def removeOrphanContents(self):
        """Remove orphaned content records."""
        reObjNum = re.compile("[0-9A-Z]{8}$")
        # --Determine which contIds are matched to a reference.
        contIds = set(self.conts_id.keys())
        matched = {id: False for id in contIds}
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                objId = object[2]
                # --LVCR? Get id of spawned creature input_Streamtead.
                for objRecord in object[3]:
                    if objRecord.name == "NAME":
                        objId = cstrip(objRecord.data)
                        break
                if reObjNum.search(objId):
                    if objId in contIds:
                        matched[objId] = True
        # --Special case: PlayerSaveGame
        matched["PlayerSaveGame00000000"] = True
        # --unmatched = container records that have not been matched.
        orphans = set([self.conts_id[id] for id in contIds if not matched[id]])
        for orphan in sorted(orphans, key=lambda a: a.getId().lower()):
            self.log("  " + orphan.getId())
        # --Delete Records
        self.records = [record for record in self.records if record not in orphans]
        self.conts = [record for record in self.conts if record not in orphans]
        self.conts_id = {
            id: record for id, record in self.conts_id.iteritems() if matched[id] > 0
        }
        return len(orphans)

    def removeRefsById(self, objIds, safeCells=[]):
        """Remove refs with specified object ids, except in specified cells.
        objIds -- Set of object ids to re removed.
        skipCells -- Set of cell names to be skipped over."""
        reObjNum = re.compile("[0-9A-F]{8}$")
        delCount = {}
        reSafeCells = re.compile("(" + ("|".join(safeCells)) + ")")
        cellsSkipped = []
        for cell in self.cells:
            if safeCells and reSafeCells.match(cell.getId()):
                cellsSkipped.append(cell.getId())
                continue
            objects = cell.getObjects()
            for object in objects.list():
                objId = object[2]
                # --If ref is a spawn point, then use id of spawned creature.
                for objRecord in object[3]:
                    if objRecord.name == "NAME":
                        objId = cstrip(objRecord.data)
                        break
                objBase = reObjNum.sub(
                    "", objId
                )  # --Strip '00001234' id num from object
                if objBase in objIds:
                    objects.remove(object)
                    delCount[objBase] = delCount.get(objBase, 0) + 1
        # --Done
        log = self.log
        log.setHeader(_("Cells Skipped:"))
        for cell in sorted(cellsSkipped, key=lambda a: a.lower()):
            log("  " + cell)
        log.setHeader(_("References Deleted:"))
        for objId in sorted(delCount.keys(), key=lambda a: a.lower()):
            log("  %03d  %s" % (delCount[objId], objId))

    # --Replacers --------------------------------------------------------------
    def replaceRefsById(self, refReplacer):
        """Replace refs according to refReplacer."""
        log = self.log
        oldIds = set(refReplacer.newIds.keys())
        replCount = {}
        for cell in self.cells:
            objects = cell.getObjects()
            for object in objects.list():
                (iMod, iObj, oldId, objRecords) = object[:4]
                if oldId.lower() in oldIds:
                    newId = refReplacer.getNewId(oldId)
                    newObject = (iMod, iObj, newId, objRecords)
                    objects.replace(object, newObject)
                    replCount[oldId] = replCount.get(oldId, 0) + 1
        # --Add Records?
        newRecords = refReplacer.getSrcRecords()
        if newRecords:
            selfIds = set(
                [record.getId().lower() for record in self.records if record.getId()]
            )
            log.setHeader(_("Records added:"))
            for newId in sorted(newRecords.keys()):
                if newId not in selfIds:
                    self.records.append(newRecords[newId])
                    log(newId)
        # --Log
        log.setHeader(_("References replaced:"))
        for oldId in sorted(replCount.keys(), key=lambda a: a.lower()):
            log("%03d %s" % (replCount[oldId], oldId))
        # --Return number of references replaced.
        return sum(replCount.values())


class WorldRefs:
    """World references as defined by a set of masters (esms and esps)."""

    def __init__(self, masterNames=[], progress=None, log=None):
        self.progress = progress or Progress()
        self.log = log or Log()
        self.levListMasters = (
            {}
        )  # --Count of masters for each leveled list (LEVC or LEVI)
        self.masterNames = []  # --Names of masters, in order added
        self.extCellNames = set()  # --Named exterior cells.
        self.cellRefIds = {}  # --objId = cellRefIds[cellId][(iMod,iObj)]
        self.cellRefAlts = {}  # --(iModNew,iObj) = cellRefAlts[cellId][(iModOld,iObj)]
        self.debrisIds = {}
        self.lands = {}  # --Landscape records indexed by landscape record id.
        if masterNames:
            self.addMasters(masterNames)

    def addMasters(self, masterNames):
        """Add a list of mods."""
        # --Load Masters
        # --Master FileRefs
        proItems = []
        totSize = 0
        for masterName in masterNames:
            # --Don't have fileRef? FileRef out of date?
            masterInfo = modInfos[masterName]
            fileRefs = masterInfo.extras.get("FileRefs")
            if not fileRefs:
                fileRefs = masterInfo.extras["FileRefs"] = FileRefs(
                    masterInfo, True, True
                )
                fileRefs.setDebrisIds()
            refreshSize = fileRefs.refreshSize()
            if refreshSize:
                proItems.append((fileRefs, refreshSize))
                totSize += refreshSize
        # --Refresh masters
        cumSize = 0
        for fileRefs, size in proItems:
            self.progress.setBaseScale(1.0 * cumSize / totSize, 1.0 * size / totSize)
            fileRefs.progress = self.progress
            fileRefs.refresh()
            cumSize += size
        # --Do Mapping
        del proItems[:]
        totSize = 0
        for masterName in masterNames:
            size = len(modInfos[masterName].extras["FileRefs"].cells)
            proItems.append((masterName, size))
            totSize += size
        cumSize = 0
        for masterName, size in proItems:
            if size:
                self.progress.setBaseScale(
                    1.0 * cumSize / totSize, 1.0 * size / totSize
                )
            self.addMaster(masterName)
            cumSize += size

    def addMaster(self, masterName):
        """Add a single mod."""
        masterInfo = modInfos[masterName]
        self.masterNames.append(masterName)
        # --Map info
        iMod = len(self.masterNames)
        # --Map masters
        masterMap = self.getMasterMap(masterInfo)
        masterRefs = masterInfo.extras["FileRefs"]
        # --Get Refs types and alts
        cellRefIds = self.cellRefIds
        cellRefAlts = self.cellRefAlts
        # --Progress
        cntCells = 0
        progress = self.progress
        progress.setMax(len(masterRefs.cells))
        progress(0.0, _("Building ") + masterName)
        for cell, record in masterRefs.lands.items():
            self.lands[cell] = record
        for masterCell in masterRefs.cells:
            cellId = masterCell.getId()
            # --Named exterior cell?
            if not (masterCell.flags & 1) and masterCell.cellName:
                self.extCellNames.add(masterCell.cellName)
            # --New cell id?
            if cellId not in cellRefIds:
                refIds = cellRefIds[cellId] = {}
                refAlts = cellRefAlts[cellId] = {}
            # --Exiting cell id?
            else:
                refIds = cellRefIds[cellId]
                refAlts = cellRefAlts[cellId]
            # --Objects
            for object in masterCell.getObjects().list():
                (iMMod, iObj, objId) = object[:3]
                newIdKey = (iMod, iObj)
                # --Modifies a master reference?
                if iMMod:
                    if iMMod >= len(masterMap):
                        raise Tes3RefError(
                            masterName, cellId, objId, iObj, iMMod, _("NO SUCH MASTER")
                        )
                    altKey = (masterMap[iMMod], iObj)
                    oldIdKey = altKey
                    # --Already modified?
                    if altKey in refAlts:
                        oldIdKey = refAlts[altKey]
                    if oldIdKey not in refIds:
                        raise Tes3RefError(
                            masterName,
                            cellId,
                            objId,
                            iObj,
                            iMMod,
                            masterInfo.masterNames[iMMod - 1],
                        )
                    del refIds[oldIdKey]
                    refAlts[altKey] = newIdKey
                # --Save it
                refIds[newIdKey] = objId
            # --Progress
            cntCells += 1
            progress(cntCells)
        # --Debris Ids
        for type, ids in masterRefs.debrisIds.items():
            if type not in self.debrisIds:
                self.debrisIds[type] = set()
            self.debrisIds[type].update(ids)
        # --List Masters
        levListMasters = self.levListMasters
        for levList in masterRefs.debrisIds["LEVC"] + masterRefs.debrisIds["LEVI"]:
            if levList not in levListMasters:
                levListMasters[levList] = []
            levListMasters[levList].append(masterName)

    def getMasterMap(self, masterInfo):
        """Return a map of a master's masters to the refworld's masters."""
        masterMap = [0]
        # --Map'em
        for mmName in masterInfo.masterNames:
            if mmName not in self.masterNames:
                raise MoshError(
                    _("Miss-ordered esm: %s should load before %s")
                    % (mmName, masterInfo.name)
                )
            masterMap.append(self.masterNames.index(mmName) + 1)
        # --Done
        return masterMap

    # --Repair ---------------------------------------------
    def removeDebrisCells(self, fileRefs):
        """Removes debris cells -- cells that are not supported by any of the master files."""
        # --Make sure fileRefs for a save file!
        if not fileRefs.fileInfo.isEss():
            fileName = fileRefs.fileInfo.fileName
            raise ArgumentError(
                _("Cannot remove debris cells from a non-save game!") + fileName
            )
        log = self.log
        cntDebrisCells = 0
        log.setHeader("Debris Cells")
        for cell in fileRefs.cells:
            # --Cell Id
            cellId = cell.getId()
            if cellId not in self.cellRefIds:
                log(cellId)
                fileRefs.records.remove(cell)
                fileRefs.cells.remove(cell)
                del fileRefs.cells_id[cellId]
                cntDebrisCells += 1
        return cntDebrisCells

    def removeDebrisRecords(self, fileRefs):
        """Removes debris records (BOOK, CREA, GLOB, NPC_) that are not present
        in masters and that aren't constructed in game (custom enchantment scrolls)."""
        # --Make sure fileRefs for a save file!
        if not fileRefs.fileInfo.isEss():
            fileName = fileRefs.fileInfo.fileName
            raise ArgumentError(
                _("Cannot remove save debris from a non-save game!") + fileName
            )
        goodRecords = []
        debrisIds = self.debrisIds
        debrisTypes = set(debrisIds.keys())
        reCustomId = re.compile(r"^\d{10,}$")
        removedIds = {}
        for record in fileRefs.records:
            type = record.name
            if type in debrisTypes:
                id = record.getId()
                if (
                    id
                    and id.lower() not in debrisIds[type]
                    and not reCustomId.match(id)
                ):
                    if type not in removedIds:
                        removedIds[type] = []
                    removedIds[type].append(id)
                    continue  # --Skip appending this record to good records.
            goodRecords.append(record)
        # --Save altered record list?
        cntDebrisIds = 0
        if removedIds:
            # --Save changes
            del fileRefs.records[:]
            fileRefs.records.extend(goodRecords)
            # --Log
            log = self.log
            for type in sorted(removedIds.keys()):
                log.setHeader(_("Debris %s:") % (type,))
                for id in sorted(removedIds[type], key=lambda a: a.lower()):
                    log("  " + id)
                cntDebrisIds += len(removedIds[type])
        return cntDebrisIds

    def removeOverLists(self, fileRefs):
        """Removes leveled lists when more than one loaded mod changes that
        same leveled list."""
        if not fileRefs.fileInfo.isEss():
            fileName = fileRefs.fileInfo.fileName
            raise ArgumentError(
                _("Cannot remove overriding lists from a non-save game!") + fileName
            )
        listTypes = {"LEVC", "LEVI"}
        levListMasters = self.levListMasters
        log = self.log
        cntLists = 0
        log.setHeader(_("Overriding Lists"))
        # --Go through records and trim overriding lists.
        goodRecords = []
        for record in fileRefs.records:
            type = record.name
            if type in listTypes:
                id = record.getId()
                idl = id.lower()
                masters = levListMasters.get(idl, "")
                if len(masters) != 1:
                    log("  " + id)
                    for master in masters:
                        log("    " + master)
                    cntLists += 1
                    # del fileRefs.debrisIds[type][idl]
                    continue  # --Skip appending this record to good records.
            goodRecords.append(record)
        del fileRefs.records[:]
        fileRefs.records.extend(goodRecords)
        return cntLists

    def repair(self, fileRefs):
        """Repair the references for a file."""
        # --Progress/Logging
        log = self.log
        logBDD = _("BAD DELETE>>DELETED %d %d %s")
        logBRR = _("BAD REF>>REMATCHED  %d %d %s %d")
        logBRN = _("BAD REF>>NO MASTER  %d %d %s")
        logBRD = _("BAD REF>>DOUBLED    %d %d %s")
        # ----
        isMod = fileRefs.fileInfo.isMod()
        reObjNum = re.compile("[0-9A-Z]{8}$")
        emptyDict = {}
        cellRefIds = self.cellRefIds
        cntRepaired = 0
        cntDeleted = 0
        cntUnnamed = 0
        for cell in fileRefs.cells:
            # --Data arrays
            usedKeys = []
            badDeletes = []
            badObjects = []
            doubleObjects = []
            refMods = {}
            # --Cell Id
            cellId = cell.getId()
            log.setHeader(cellId)
            # --Debris cell name?
            if not isMod:
                cellName = cell.cellName
                if (
                    not (cell.flags & 1)
                    and cellName
                    and (cellName not in self.extCellNames)
                ):
                    log(_("Debris Cell Name: ") + cellName)
                    cell.flags &= ~32
                    cell.cellName = ""
                    cell.setChanged()
                    cntUnnamed += 1
            refIds = cellRefIds.get(
                cellId, emptyDict
            )  # --Empty if cell is new in fileRefs.
            objects = cell.getObjects()
            for object in objects.list():
                (iMod, iObj, objId, objRecords) = object[:4]
                refKey = (iMod, iObj)
                # --Used Key?
                if refKey in usedKeys:
                    log(logBRD % object[:3])
                    objects.remove(object)
                    doubleObjects.append(object)
                    cell.setChanged()
                # --Local object?
                elif not iMod:
                    # --Object Record
                    for objRecord in objRecords:
                        # --Orphan delete?
                        if objRecord.name == "DELE":
                            log(logBDD % object[:3])
                            objects.remove(object)
                            badDeletes.append(object)
                            cntDeleted += 1
                            cell.setChanged()
                            break
                    # --Not Deleted?
                    else:  # --Executes if break not called in preceding for loop.
                        usedKeys.append(refKey)
                # --Modified object?
                else:
                    refId = refIds.get(refKey, None)
                    objIdBase = reObjNum.sub(
                        "", objId
                    )  # --Strip '00001234' id num from object
                    # --Good reference?
                    if refId and (isMod or (refId == objIdBase)):
                        usedKeys.append(refKey)
                    # --Missing reference?
                    else:
                        badObjects.append(object)
                        cell.setChanged()
            # --Fix bad objects.
            if badObjects:
                # --Build rematching database where iMod = refMods[(iObj,objId)]
                refMods = {}
                repeatedKeys = []
                for refId in refIds.keys():
                    (iMod, iObj) = refId
                    objId = refIds[refId]
                    key = (iObj, objId)
                    # --Repeated Keys?
                    if key in refMods:
                        repeatedKeys.append(key)
                    else:
                        refMods[key] = iMod
                # --Remove remaps for any repeated keys
                for key in repeatedKeys:
                    if key in refMods:
                        del refMods[key]
                # --Try to remap
                for object in badObjects:
                    (iMod, iObj, objId) = object[:3]
                    objIdBase = reObjNum.sub(
                        "", objId
                    )  # --Strip '00001234' id num from object
                    refModsKey = (iObj, objIdBase)
                    newMod = refMods.get(refModsKey, None)
                    # --Valid rematch?
                    if newMod and ((newMod, iObj) not in usedKeys):
                        log(logBRR % (iMod, iObj, objId, newMod))
                        usedKeys.append((newMod, iObj))
                        objects.replace(object, fileRefs.remapObject(object, newMod))
                        cntRepaired += 1
                    elif not newMod:
                        log(logBRN % tuple(object[:3]))
                        objects.remove(object)
                        cntDeleted += 1
                    else:
                        log(logBRD % tuple(object[:3]))
                        objects.remove(object)
                        cntDeleted += 1
        # --Done
        fileRefs.updateScptRefs()
        return (cntRepaired, cntDeleted, cntUnnamed)

    def repairWorldMap(self, fileRefs, gridLines=True):
        """Repair savegame's world map."""
        if not fileRefs.fmap:
            return 0
        progress = self.progress
        progress.setMax((28 * 2) ** 2)
        progress(0.0, _("Drawing Cells"))
        proCount = 0
        for gridx in xrange(-28, 28, 1):
            for gridy in xrange(28, -28, -1):
                id = "[%d,%d]" % (gridx, gridy)
                cell = fileRefs.cells_id.get(id, None)
                isMarked = cell and cell.flags & 32
                fileRefs.fmap.drawCell(self.lands.get(id), gridx, gridy, isMarked)
                proCount += 1
                progress(proCount)
        fileRefs.fmap.drawGrid(gridLines)
        return 1

    def repairWorldMapMCP(
        self, fileRefs, gridLines=True
    ):  # Polemos: Added (I hope) support for MCP extended world map
        """Repair savegame's world map."""
        if not fileRefs.fmap:
            return 0
        progress = self.progress
        progress.setMax((51 + 51) * (64 + 38))
        progress(0.0, _("Drawing Cells"))
        proCount = 0
        for gridx in xrange(-51, 51, 1):
            for gridy in xrange(38, -64, -1):
                id = "[%d,%d]" % (gridx, gridy)
                cell = fileRefs.cells_id.get(id, None)
                isMarked = cell and cell.flags & 32
                fileRefs.fmap.drawCell(self.lands.get(id), gridx, gridy, isMarked)
                proCount += 1
                progress(proCount)
        fileRefs.fmap.drawGrid(gridLines)
        return 1


class FileDials(FileRep):
    """TES3 file representation focusing on dialog.

    Only TES3 DIAL and INFO records are analyzed. All others are left in raw data
    form."""

    def __init__(self, fileInfo, canSave=True):
        FileRep.__init__(self, fileInfo, canSave)
        self.dials = []
        self.infos = {}  # --info = self.infos[(dial.type,dial.id,info.id)]

    def load(self, factory={}):
        """Load dialogs from file."""
        canSave = self.canSave
        InfoClass = factory.get("INFO", InfoS)  # --Info class from factory.
        # --Header
        inPath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        input_Stream = Tes3Reader(self.fileInfo.name, file(inPath, "rb"))
        (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
        self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        # --Raw data read
        dial = None
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            # --DIAL?
            if name == "DIAL":
                dial = Dial(name, size, delFlag, recFlag, input_Stream, True)
                self.dials.append(dial)
                if canSave:
                    self.records.append(dial)
            # --INFO?
            elif name == "INFO":
                info = InfoClass(name, size, delFlag, recFlag, input_Stream, True)
                self.records.append(info)
                dial.infos.append(info)
                self.infos[(dial.type, dial.id, info.id)] = info
            # --Non-dials?
            elif canSave:
                record = Record(name, size, delFlag, recFlag, input_Stream)
                self.records.append(record)
            else:
                input_Stream.seek(size, 1, "Record")
        # --Done Reading
        input_Stream.close()

    def save(self, outPath=None):
        """Save data to file.
        outPath -- Path of the output file to write to. Defaults to original file path.
        """
        if not self.canSave:
            raise StateError(_("input_Streamufficient data to write file."))
        FileRep.save(self, outPath)

    def loadText(self, textFileName):
        """Replaces dialog text with text read from file."""
        # --Text File
        infoKey = None
        text = None
        texts = {}
        reHeader = re.compile("^#")
        reInfo = re.compile(r'@ +(\d) +"(.+?)" +(\d+)')
        reSingleQuote = re.compile("[\x91\x92]")
        reDoubleQuote = re.compile("[\x93\x94]")
        reEllipsis = re.compile("\x85")
        reEolSpaces = re.compile(r" +\r\n")
        reExtraSpaces = re.compile(r"  +")
        reIllegalChars = re.compile(r"[@#]")
        # --Read file
        textFile = file(textFileName, "rb")
        for line in textFile:
            if reHeader.match(line):
                continue
            maInfo = reInfo.match(line)
            if maInfo:
                infoKey = (int(maInfo.group(1)), maInfo.group(2), maInfo.group(3))
                texts[infoKey] = text = []
            else:
                text.append(line)
        textFile.close()
        # --Strip and clean texts
        updated = []
        unmatched = []
        trimmed = {}
        for infoKey in texts.keys():
            if infoKey not in self.infos:
                unmatched.append(infoKey)
                continue
            text = "".join(texts[infoKey])
            # --Required Subs
            text = text.strip(" \r\n")
            text = reSingleQuote.sub("'", text)
            text = reDoubleQuote.sub('"', text)
            text = reEllipsis.sub("...", text)
            text = reIllegalChars.sub("", text)
            # --Optional subs
            text = reEolSpaces.sub("\r\n", text)
            text = reExtraSpaces.sub(" ", text)
            # --Trim?
            if len(text) > 511:
                trimmed[infoKey] = (text[:511], text[511:])
                text = text[:511]
            info = self.infos[infoKey]
            if text != info.text:
                info.text = text
                info.setChanged()
                updated.append(infoKey)
        # --Report
        buff = cStringIO.StringIO()
        for header, infoKeys in ((_("Updated"), updated), (_("Unmatched"), unmatched)):
            if infoKeys:
                buff.write("=== %s\n" % (header,))
            for infoKey in infoKeys:
                buff.write("* %s\n" % (infoKey,))
        if trimmed:
            buff.write("=== %s\n" % (_("Trimmed"),))
            for infoKey, (preTrim, postTrim) in trimmed.items():
                buff.write(f"{infoKey}\n{preTrim}<<<{postTrim}\n\n")
        return buff.getvalue()

    def dumpText(self, textFileName, groupBy="spId", spId=None):
        """Dumps dialogs to file."""
        newDials = self.dials[:]
        newDials.sort(key=lambda a: a.id.lower())
        newDials.sort(key=lambda a: a.type, reverse=True)
        infoKeys = []
        for dial in newDials:
            dial.sortInfos()
            for info in dial.infos:
                infoKeys.append((dial.type, dial.id, info.id))
        if groupBy == "spId":
            infoKeys.sort(
                key=lambda a: self.infos[a].spId and self.infos[a].spId.lower()
            )
        # --Text File
        with file(textFileName, "wb") as textFile:
            prevSpId = prevTopic = -1
            for infoKey in infoKeys:
                info = self.infos[infoKey]
                # --Filter by spId?
                if spId and info.spId != spId:
                    continue
                # --Empty text?
                if not info.text:
                    continue
                # --NPC Header?
                if groupBy == "spId" and info.spId != prevSpId:
                    prevSpId = info.spId
                    header = prevSpId or ""
                    textFile.write('# "%s" %s\r\n' % (header, "-" * (75 - len(header))))
                # --Topic header?
                elif groupBy == "topic" and infoKey[1] != prevTopic:
                    prevTopic = infoKey[1]
                    header = prevTopic or ""
                    textFile.write('# "%s" %s\r\n' % (header, "-" * (75 - len(header))))
                textFile.write('@ %d "%s" %s' % infoKey)
                if info.spId:
                    textFile.write(' "' + info.spId + '"')
                textFile.write("\r\n")
                textFile.write(info.text)
                textFile.write("\r\n")
                textFile.write("\r\n")


class FileLists(FileRep):
    """TES3 file representation focussing on levelled lists.

    Only TES3 LEVI and LEVC records are analyzed. All others are left in raw data
    form."""

    def __init__(self, fileInfo, canSave=True):
        FileRep.__init__(self, fileInfo, canSave)
        self.levcs = {}
        self.levis = {}
        self.srcMods = {}  # --Used by merge functionality

    def load(self):
        """Load leveled lists from file."""
        canSave = self.canSave
        # --Header
        inPath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        input_Stream = Tes3Reader(self.fileInfo.name, file(inPath, "rb"))
        (name, size, delFlag, recFlag) = input_Stream.unpack("4s3i", 16, "REC_HEAD")
        self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        # --Raw data read
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            # --LEVC?
            if name == "LEVC":
                levc = Levc(name, size, delFlag, recFlag, input_Stream, True)
                self.levcs[levc.id] = levc
                if canSave:
                    self.records.append(levc)
            elif name == "LEVI":
                levi = Levi(name, size, delFlag, recFlag, input_Stream, True)
                self.levis[levi.id] = levi
                if canSave:
                    self.records.append(levi)
            # --Other
            elif canSave:
                record = Record(name, size, delFlag, recFlag, input_Stream)
                self.records.append(record)
            else:
                input_Stream.seek(size, 1, "Record")
        # --Done Reading
        input_Stream.close()

    def beginMerge(self):
        """Beginput_Stream merge process."""
        # --Delete existing lists.
        listTypes = {"LEVC", "LEVI"}
        self.records = [
            record for record in self.records if record.name not in listTypes
        ]
        self.levcs.clear()
        self.levis.clear()

    def mergeWith(self, newFL):
        """Add lists from another FileLists object."""
        srcMods = self.srcMods
        for levls, newLevls in ((self.levcs, newFL.levcs), (self.levis, newFL.levis)):
            for listId, newLevl in newLevls.items():
                if listId not in srcMods:
                    srcMods[listId] = [newFL.fileInfo.name]
                    levl = levls[listId] = copy.deepcopy(newLevl)
                    self.records.append(levl)
                else:
                    srcMods[listId].append(newFL.fileInfo.name)
                    levls[listId].mergeWith(newLevl)

    def completeMerge(self):
        """Completes merge process. Use this when finished using mergeWith."""
        # --Remove lists that aren't the sum of at least two esps.
        srcMods = self.srcMods
        for levls in (self.levcs, self.levis):
            for listId in levls.keys():
                if len(srcMods[listId]) < 2 or levls[listId].isDeleted:
                    self.records.remove(levls[listId])
                    del levls[listId]
                    del srcMods[listId]
        # --Log
        log = self.log
        for label, levls in (("Creature", self.levcs), ("Item", self.levis)):
            if not len(levls):
                continue
            log.setHeader(_("Merged %s Lists:") % (label,))
            for listId in sorted(levls.keys(), key=lambda a: a.lower()):
                log(listId)
                for mod in srcMods[listId]:
                    log("  " + mod)


class FileScripts(FileRep):
    """TES3 file representation focussing on scripts. Only scripts are analyzed. All other recods are left in raw data form."""

    def __init__(self, fileInfo, canSave=True):
        FileRep.__init__(self, fileInfo, canSave)
        self.scripts = []

    def load(self, factory={}):
        """Load dialogs from file."""
        canSave = self.canSave
        # --Header
        inPath = os.path.join(self.fileInfo.dir, self.fileInfo.name)
        input_Stream = Tes3Reader(self.fileInfo.name, file(inPath, "rb"))
        (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
        self.tes3 = Tes3(name, size, delFlag, recFlag, input_Stream, True)
        # --Raw data read
        dial = None
        while not input_Stream.atEnd():
            # --Get record info and handle it
            (name, size, delFlag, recFlag) = input_Stream.unpackRecHeader()
            # --SCPT?
            if name == "SCPT":
                record = Scpt(name, size, delFlag, recFlag, input_Stream, True)
                self.scripts.append(record)
                if canSave:
                    self.records.append(record)
            # --Non-dials?
            elif canSave:
                record = Record(name, size, delFlag, recFlag, input_Stream)
                self.records.append(record)
            else:
                input_Stream.seek(size, 1, "Record")
        # --Done Reading
        input_Stream.close()

    def save(self, outPath=None):
        """Save data to file.
        outPath -- Path of the output file to write to. Defaults to original file path.
        """
        if not self.canSave:
            raise StateError(_("input_Streamufficient data to write file."))
        FileRep.save(self, outPath)

    def loadText(self, textFileName):
        """Replaces dialog text with text read from file."""
        with file(textFileName, "rb") as textFile:
            reHeader = re.compile("^# ([a-zA-Z_0-9]+)")
            id, lines, changed = None, [], []
            id_records = {record.id.lower(): record for record in self.scripts}

            def unBuffer():
                record = id and id_records.get(id.lower())
                if record:
                    code = ("".join(lines)).strip()
                    if code.lower() != record.sctx.data.strip().lower():  # ?
                        record.setCode(code)  # ?x2
                        changed.append(id)

            for line in textFile:
                maHeader = reHeader.match(line)
                if maHeader:
                    unBuffer()
                    id, lines = maHeader.group(1), []
                elif id:
                    lines.append(line)
        unBuffer()
        return sorted(changed, key=string.lower)

    def dumpText(self, textFileName):
        """Dumps dialogs to file."""
        with file(textFileName, "wb") as textFile:
            for script in sorted(self.scripts, key=lambda a: a.id.lower()):
                textFile.write("# %s %s\r\n" % (script.id, "=" * (76 - len(script.id))))
                textFile.write(script.sctx.data.strip())
                textFile.write("\r\n\r\n")
