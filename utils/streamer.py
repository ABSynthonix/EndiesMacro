import os

class LogStreamer:
    def __init__(self, log_path):
        self.log_path = log_path
        self.file_handle = None

    def open_log(self):
        """Opens the log file and processes only new data"""
        try:
            self.file_handle = open(self.log_path, 'rb')
            self.file_handle.seek(0, os.SEEK_END)
            return True
        except Exception as e:
            print(f'Error opening log: {e}')
            return False

    def get_new_lines(self):
        """A generator that scans new lines as they appear"""
        if not self.file_handle:
            return

        if not os.path.exists(self.log_path):
            yield "FORCE_RESTART"
            return

        line = self.file_handle.readline()
        if not line:
            return

        yield line.decode('utf-8', errors='ignore')

    def close(self):
        if self.file_handle:
            self.file_handle.close()