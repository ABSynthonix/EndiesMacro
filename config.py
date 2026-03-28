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