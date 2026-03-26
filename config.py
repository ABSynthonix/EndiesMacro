import os
import glob

def get_latest_log_file():
    logs_dir = os.path.join(os.environ["LOCALAPPDATA"], "Roblox", "Logs")

    search_path = os.path.join(logs_dir, "*.log")
    files = glob.glob(search_path)

    if not files:
        return None

    files.sort(key=os.path.getmtime, reverse=True)

    return files[0]

Webhook = "https://discord.com/api/webhooks/1486812124956201082/VogdtdHUlFAmjjGegzt9ln7-f6cb9Hs0Nfmqg69sGp59EFtZIKHNcVf4Tegkjo5JkEw8"
PS_Link = "https://www.roblox.com/share?code=542ff8e83e7d6c48824e141a09929285&type=Server"