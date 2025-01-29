# Wrye Nash, Copyright (C) 2018-, Polemos
# Polemos: I created this as a basis for Nexus site compatibility. It gives Internet abilities
# to Wrye Mash. I hope the next guy who works on Wrye Mash will find it useful and build on it.


from lxml import html
from lxml import _elementpath as _dummy  #  Polemos: Needed for py2exe to work.
import requests
import gui.dialog
import os, wx


os.environ["REQUESTS_CA_BUNDLE"] = "cacert.pem"


def wrye_download_site(url, mode):
    """Mirrors and download site of Wrye Mash."""
    if url == "home":
        if not mode:  # Regular Morrowind
            return "https://www.nexusmods.com/morrowind/mods/45439"
        else:  # OpenMW/TES3mp
            return "https://www.nexusmods.com/morrowind/mods/46935"
    if url == "download":
        if not mode:  # Regular Morrowind
            return "https://www.nexusmods.com/morrowind/mods/45439?tab=files"
        else:  # OpenMW/TES3mp
            return "https://www.nexusmods.com/morrowind/mods/46935?tab=files"


class WryeWeb:
    """Wrye Mash version checker for Nexus."""

    def __init__(self, mode):
        """Init."""
        self.openmw = mode
        self.mash_net = wrye_download_site("home", self.openmw)

    def get_mash_ver(self):
        """Parse Nexus page."""
        progress = gui.dialog.netProgressDialog()
        try:
            progress.update(4)
            page = requests.get(self.mash_net)
            tree = html.fromstring(page.content)
            get_ver = tree.xpath('//*[@id="pagetitle"]/ul[2]/li[5]/div/div[2]')
            self.mash_net_ver = int(("%s" % (get_ver[0].text.strip().replace("v", ""))))
            progress.update()
            result = self.mash_net_ver
        except:
            result = "error"
        finally:
            progress.Destroy()
            return result


class VisitWeb:
    """Visit a mod's webpage."""

    def __init__(self, webData):
        """Init."""
        repo, ID = webData
        if repo == "Nexus":
            self.Nexus(ID)
        # elif repo ==...
        else:
            return

    def Nexus(self, ID):
        """Nexus site implementation."""
        nexusWeb = "https://www.nexusmods.com/morrowind/mods/%s" % ID
        self.visit(nexusWeb)

    def visit(self, website):
        """Open mod website on user's default system browser."""
        wx.LaunchDefaultBrowser(website)
