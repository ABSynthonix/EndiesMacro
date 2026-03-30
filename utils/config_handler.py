import json
import os

class ConfigManager:
    def __init__(self, filename="settings.json"):
        self.config_dir = os.path.join(os.getenv('APPDATA'), "EndiesMacro")
        self.filepath = os.path.join(self.config_dir, filename)

        self.ensure_config_dir()
        self.settings = self.load_config()

    def ensure_config_dir(self):
        """Creates the 'config' folder if it's missing."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def load_config(self):
        """Reads the JSON file. If it doesn't exist, it creates a new one."""
        if not os.path.exists(self.filepath):
            default_config = {
                "Private_Server_Link": "",
                "Webhook": "",
                "Auto_Rejoin": False,
                "Anti_AFK": False,
                "Send_Webhook": False,
                "Place_Id": 15532962292
            }
            self.save_config(default_config)
            return default_config

        with open(self.filepath, 'r') as f:
            return json.load(f)

    def save_config(self, data=None):
        """Saves new data to the JSON file."""
        save_data = data if data else self.settings
        with open(self.filepath, 'w') as f:
            json.dump(save_data, f, indent=4)
        self.settings = save_data