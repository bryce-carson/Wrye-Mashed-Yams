class ResourceReplacer:
    """Resource Replacer. Used to apply and remove a set of resource (texture, etc.) replacement files."""

    # --Class data
    textureExts = {".dds", ".tga", ".bmp"}
    dirExts = {
        "bookart": textureExts,
        "fonts": {".fnt", ".tex"},
        "icons": textureExts,
        "meshes": {".nif", ".kf"},
        "music": {".mp3"},
        "sound": {".wav"},
        "splash": textureExts,
        "textures": textureExts,
    }

    def __init__(self, replacerDir, file):
        """Initialize"""
        self.replacerDir = replacerDir
        self.file = file
        self.progress = None
        self.cumSize = 0

    def isApplied(self):
        """Returns True if has been applied."""
        return self.file in settings["mosh.resourceReplacer.applied"]

    def apply(self, progress=None):
        """Copy files to appropriate resource directories (Textures, etc.)."""
        if progress:
            self.progress = progress
            self.cumSize = 0
            self.totSize = 0
            self.doRoot(self.sizeDir)
            self.progress.setMax(self.totSize)
        self.doRoot(self.applyDir)
        settings.getChanged("mosh.resourceReplacer.applied").append(self.file)
        self.progress = None

    def remove(self):
        """Uncopy files from appropriate resource directories (Textures, etc.)."""
        self.doRoot(self.removeDir)
        settings.getChanged("mosh.resourceReplacer.applied").remove(self.file)

    def doRoot(self, action):
        """Copy/uncopy files to/from appropriate resource directories."""
        # --Root directory is Textures directory?
        dirExts = ResourceReplacer.dirExts
        textureExts = ResourceReplacer.textureExts
        srcDir = os.path.join(self.replacerDir, self.file)
        destDir = modInfos.dir
        isTexturesDir = True  # --Assume true for now.
        for srcFile in scandir.listdir(srcDir):
            srcPath = os.path.join(srcDir, srcFile)
            if os.path.isdir(srcPath) and srcFile.lower() in dirExts:
                isTexturesDir = False
                destPath = os.path.join(destDir, srcFile)
                action(srcPath, destPath, dirExts[srcFile.lower()])
        if isTexturesDir:
            destPath = os.path.join(destDir, "Textures")
            action(srcDir, destPath, textureExts)

    def sizeDir(self, srcDir, destDir, exts):
        """Determine cumulative size of files to copy."""
        for srcFile in scandir.listdir(srcDir):
            srcExt = os.path.splitext(srcFile)[-1].lower()
            srcPath = os.path.join(srcDir, srcFile)
            destPath = os.path.join(destDir, srcFile)
            if srcExt in exts:
                self.totSize += os.path.getsize(srcPath)
            elif os.path.isdir(srcPath):
                self.sizeDir(srcPath, destPath, exts)

    def applyDir(self, srcDir, destDir, exts):
        """Copy files to appropriate resource directories (Textures, etc.)."""
        for srcFile in scandir.listdir(srcDir):
            srcExt = os.path.splitext(srcFile)[-1].lower()
            srcPath = os.path.join(srcDir, srcFile)
            destPath = os.path.join(destDir, srcFile)
            if srcExt in exts:
                if not os.path.exists(destDir):
                    os.makedirs(destDir)
                shutil.copyfile(srcPath, destPath)
                if self.progress:
                    self.cumSize += os.path.getsize(srcPath)
                    self.progress(self.cumSize, _("Copying Files..."))
            elif os.path.isdir(srcPath):
                self.applyDir(srcPath, destPath, exts)

    def removeDir(self, srcDir, destDir, exts):
        """Uncopy files from appropriate resource directories (Textures, etc.)."""
        for srcFile in scandir.listdir(srcDir):
            srcExt = os.path.splitext(srcFile)[-1].lower()
            srcPath = os.path.join(srcDir, srcFile)
            destPath = os.path.join(destDir, srcFile)
            if os.path.exists(destPath):
                if srcExt in exts:
                    os.remove(destPath)
                elif os.path.isdir(srcPath):
                    self.removeDir(srcPath, destPath, exts)
