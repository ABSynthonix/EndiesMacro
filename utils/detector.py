import re
import json
import time

import psutil
import utils.globals


class Detector:
    def __init__(self):
        self.cfg = utils.globals.config

        self.current_aura = None
        self.current_biome = None

        self.json_pattern = re.compile(r"\{.*\}")

        self.auto_rejoin_allowed = True
        self.disconnect_patterns = [
            r"Lost connection to the game server",  # Standard 277
            r"disconnectErrorCode",  # Generic error
            r"Connection lost",  # Simple drop
            r"ID_DISCONNECTION_NOTIFICATION",  # The engine-level event
            r"Cleanup shared replicator",  # Logged when the connection is being torn down
            r"Connection closed by remote host",  # Server-side kick/shutdown
            r"RakNet: stop client",  # Low-level network stop
        ]

    def roblox_running(self):
        """Allows you to detect if Roblox is currently running."""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == "RobloxPlayerBeta.exe":
                return True
        return False

    def process_line(self, line):
        """
        Processes a single line.
        Returns a dict only if a change is detected.
        """

        is_disconnect_line = any(re.search(p, line, re.IGNORECASE) for p in self.disconnect_patterns)

        is_manual_hint = "Disconnect from" in line and "ID_DISCONNECTION_NOTIFICATION" in line

        if is_disconnect_line or is_manual_hint:
            time.sleep(self.cfg.settings["Disconnect_Detection_Time"])

            print("Disconnection detected.")

            if not self.roblox_running():
                print("Disconnection marked as manual.")
                self.auto_rejoin_allowed = False
                return {"status": "manual_leave"}

            print("Disconnection marked as accidental.")
            self.auto_rejoin_allowed = True
            return {"status": "lost_connection"}

        match = self.json_pattern.search(line)
        if not match:
            return None

        try:
            raw_json = match.group()
            data = json.loads(raw_json)

            inner_data = data.get("data", {})

            new_state: str = inner_data.get("state")
            new_hover: str = inner_data.get("largeImage", {}).get("hoverText")
            asset_id: int = inner_data.get("largeImage", {}).get("assetId")

            if new_state and new_state.startswith('Equipped "'):
                aura_name: str = new_state.split('"')[1].replace("_", ": ")

                if aura_name != self.current_aura:
                    self.current_aura = aura_name
                    return {"aura": aura_name}

            if new_hover:
                biome_name: str = new_hover.strip()

                if biome_name != self.current_biome and biome_name not in ["Sol's RNG"]:
                    self.current_biome = biome_name
                    return {"biome": biome_name, "asset_id": asset_id}

        except (json.JSONDecodeError, KeyError, IndexError):
            return None