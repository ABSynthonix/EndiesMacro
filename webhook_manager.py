from http.client import responses

import requests
import json
from datetime import datetime

class Notifier:
    def __init__(self, webhook_url, ps_url):
        self.webhook_url = webhook_url
        self.ps_url = ps_url
        self.last_sent = 0

    def get_asset_url(self, asset_id):
        """Converts a roblox asset id to an image URL."""
        if not asset_id:
            return None
        return f"https://www.roblox.com/asset-thumbnail/image?assetId={asset_id}&width=420&height=420&format=png"

    def send_log_event(self, title: str, color: int=0x00ff00, ps_included: bool=False, asset_id: int=None):
        """Sends a Discord Embed."""
        if not self.webhook_url:
            return

        image_url = self.get_asset_url(asset_id)

        embed = {
                "description": f"""
                            ## {title}
                            {f"\n[[**Private Server Link**]]({self.ps_url})" if ps_included else ""}
                        """,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": "Endie's Macro"}
        }
        if image_url:
            embed["thumbnail"] = {"url": image_url} if image_url else None

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code not in [200, 204]:
                print(f"Webhook Failed ({response.status_code}): {response.text}")
                if "components" in response.text.lower():
                    print("Retrying without buttons...")
                    del payload["components"]
                    requests.post(self.webhook_url, json=payload)
        except Exception as e:
            print(f'Webhook Error: {e}')
            return False