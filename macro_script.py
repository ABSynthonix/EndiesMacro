import time
import utils.globals

from PyQt6.QtCore import QThread, pyqtSignal
from config import get_latest_log_file
from controller import Controller
from rejoiner import Rejoiner
from utils.detector import Detector
from utils.streamer import LogStreamer
from webhook_manager import Notifier

class MacroScript(QThread):
    log_signal = pyqtSignal(str)
    stat_signal = pyqtSignal(dict)
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True
        self._first_aura_detect = True
        self._previous_biome = None
        self._previous_asset_id = None
        self._current_biome = None
        self._current_asset_id = None

    def stop(self):
        self._is_running = False

    def run(self, restart: bool=False):
        """Starts the macro."""
        cfg = utils.globals.config

        while self._is_running:
            log_path = get_latest_log_file()
            streamer = LogStreamer(log_path)
            detector = Detector()
            controller = Controller()
            rejoiner = Rejoiner()
            webhook = Notifier(cfg.settings["Webhook"], cfg.settings["Private_Server_Link"])

            if not streamer.open_log():
                self.log_signal.emit("Failed to open log file.")
                break

            web_col = 0xFFFF00 if restart else 0x00FF00
            web_txt = "Macro Restarted" if restart else "Macro Started"

            self.log_signal.emit(web_txt)
            webhook.send_log_event(
                title=web_txt,
                color=web_col,
                send=cfg.settings["Send_Webhook"]
            )

            session_active = True
            while session_active and self._is_running:
                lines = streamer.get_new_lines()
                if lines:
                    for line in lines:
                        change = detector.process_line(line)
                        if change:
                            if "status" in change and change["status"] == "lost_connection":
                                if detector.roblox_running():
                                    self.log_signal.emit("Rejoining...")
                                    webhook.send_log_event(
                                        title="Rejoining | Connection Lost",
                                        color=0x00FFFF,
                                        send=cfg.settings["Send_Webhook"]
                                    )
                                    rejoiner.launch_roblox()
                                    time.sleep(cfg.settings["Rejoin_Wait_Time"])
                                    while not controller.press_join():
                                        time.sleep(2)
                                    session_active = False
                                else:
                                    self.log_signal.emit("Manually Closed Roblox.")
                                    self._is_running = False
                                    session_active = False

                            if "aura" in change:
                                if self._first_aura_detect:
                                    self._first_aura_detect = False

                                    webhook.send_log_event(
                                        title=f"Aura Equipped/Found: {change['aura']}",
                                        color=0xFFFFFF,
                                        send=cfg.settings["Send_Webhook"]
                                    )
                                    self.stat_signal.emit({
                                        "type": "aura",
                                        "val": change["aura"]
                                    })
                                    self.log_signal.emit(f"Found: {change['aura']}")

                            if "biome" in change:
                                self._previous_biome =  self._current_biome
                                self._previous_asset_id = self._current_asset_id
                                self._current_biome = change["biome"]
                                self._current_asset_id = change["asset_id"]

                                if self._previous_biome and self._previous_asset_id:
                                    webhook.send_log_event(
                                        title=f"Biome Ended: {self._previous_biome}",
                                        color=0x0000AA,
                                        ps_included=True,
                                        asset_id=self._previous_asset_id,
                                        send=cfg.settings["Send_Webhook"]
                                    )

                                webhook.send_log_event(
                                    title=f"Biome Started: {self._current_biome}",
                                    color=0x0000FF,
                                    ps_included=True,
                                    asset_id=self._current_asset_id,
                                    send=cfg.settings["Send_Webhook"]
                                )
                                self.stat_signal.emit({
                                    "type": "biome",
                                    "val": change["biome"]
                                })
                                self.log_signal.emit(f"Biome Started: {change['biome']}")

                        if cfg.settings["Anti_AFK"]:
                            controller.anti_afk()

                        time.sleep(.1)
                else:
                    time.sleep(.5)

                if not self._is_running:
                    break

                time.sleep(.1)

            self.log_signal.emit("Macro Stopped.")
            webhook.send_log_event(
                title="Macro Stopped",
                color=0xFF0000,
                send=cfg.settings["Send_Webhook"]
            )