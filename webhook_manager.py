import requests
from datetime import datetime
from utils.globals import MACRO_NAME

class Notifier:
    def __init__(self, webhook_url, ps_url):
        self.webhook_url = webhook_url
        self.ps_url = ps_url
        self.last_sent = 0

    def get_asset_url(self, asset_id):
        """Converts a roblox asset id to an image URL."""
        if not asset_id:
            return None
        res = requests.get(
            "https://thumbnails.roblox.com/v1/assets",
            params={
                "assetIds": asset_id,
                "size": "420x420",
                "format": "Png",
                "isCircular": "false"
            }
        )
        data = res.json()
        image_url = data["data"][0]["imageUrl"]

        return image_url if image_url else None

    def send_log_event(self, title: str, color: int=0x00ff00, ps_included: bool=False, asset_id: int=None, send: bool=False):
        """Sends a Discord Embed."""
        if not self.webhook_url or not send:
            return

        image_url = self.get_asset_url(asset_id)

        embed = {
                "description": f"""
                            ## {title}
                            {f"\n[[**Private Server Link**]]({self.ps_url})" if ps_included else ""}
                        """,
                "color": color,
                "timestamp": datetime.utcnow().isoformat(),
                "footer": {"text": MACRO_NAME}
        }
        if image_url:
            embed["thumbnail"] = {"url": image_url}

        payload = {
            "embeds": [embed]
        }

        try:
            response = requests.post(self.webhook_url, json=payload)
            if response.status_code not in [200, 204]:
                print(f"Webhook Failed ({response.status_code}): {response.text}")
        except Exception as e:
            print(f'Webhook Error: {e}')
            return False