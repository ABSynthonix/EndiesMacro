import os
import re
import utils.globals

class Rejoiner:
    def __init__(self):
        self.cfg = utils.globals.config

        self.link_code = self._extract_code(self.cfg.settings["Private_Server_Link"])

    def _extract_code(self, url):
        match = re.search(r"(?:code=|privateServerLinkCode=)([\w-]+)", url)
        return match.group(1) if match else None

    def launch_roblox(self):
        if not self.link_code:
            print("❌ Error: No link code found in your PS_Link!")
            return False

        share_protocol = f"roblox://navigation/share_links?code={self.link_code}&type=Server"

        desktop_protocol = f"roblox-player:1+launchmode:play+gameinstanceid:+placeid:{self.cfg.settings['Place_Id']}+linkCode:{self.link_code}"

        print(f"🚀 Launching Private Server (Code: {self.link_code[:6]}...)")

        try:
            os.startfile(share_protocol)
            return True
        except Exception as e:
            print(f"Primary Launch failed, trying Method B... {e}")
            try:
                os.startfile(desktop_protocol)
                return True
            except Exception as e2:
                print(f"All launch methods failed: {e2}")
                return False