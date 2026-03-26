import os
import time


class LogWatcher:
    def __init__(self, log_dir, callback):
        self.log_dir = log_dir
        self.callback = callback
        self.running = False
        self.current_file_path = None

    def get_latest_log(self):
        files = [
            os.path.join(self.log_dir, f)
            for f in os.listdir(self.log_dir)
            if f.endswith(".log")
        ]

        if not files:
            return None

        return max(files, key=os.path.getmtime)

    def follow_log(self, file):
        file.seek(0, 2)

        while self.running:
            latest = self.get_latest_log()
            if latest and latest != self.current_file_path:
                print("[LogWatcher]: Switched to new log file")
                return

            line = file.readline()

            if not line:
                time.sleep(0.05)
                continue

            self.callback(line)

    def start(self):
        self.running = True

        while self.running:
            log_file = self.get_latest_log()

            if not log_file:
                time.sleep(1)
                continue

            if log_file != self.current_file_path:
                self.current_file_path = log_file
                print(f"[LogWatcher]: Using log {log_file}")

                try:
                    with open(log_file, 'r', encoding="utf-8", errors="ignore") as f:
                        self.follow_log(f)
                except Exception as e:
                    print("[LogWatcher] Error:", e)

            time.sleep(0.2)

    def stop(self):
        self.running = False