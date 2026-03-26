import re
import json

class Detector:
    def __init__(self):
        self.current_aura = None
        self.current_biome = None

        self.json_pattern = re.compile(r"\{.*\}")

    def process_line(self, line):
        """
        Processes a single line.
        Returns a dict only if a change is detected.
        """
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