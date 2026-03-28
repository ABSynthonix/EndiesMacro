import time

import sys
import utils.globals
from rejoiner import Rejoiner
from config import get_latest_log_file
from utils.detector import Detector
from utils.streamer import LogStreamer
from webhook_manager import Notifier
from controller import Controller

def main():
    cfg = utils.globals.config
    cfg.load_config()

    log_path = get_latest_log_file()

    streamer = LogStreamer(log_path)
    detector = Detector()
    controller = Controller()

    rejoiner = Rejoiner()

    webhook = Notifier(cfg.settings["Webhook"], cfg.settings["Private_Server_Link"])

    do_send_webhooks = cfg.settings["Send_Webhook"]
    do_anti_afk = cfg.settings["Anti_AFK"]
    do_biome_randomizer = cfg.settings["Use_Biome_Randomizer"]
    do_strange_controller = cfg.settings["Use_Strange_Controller"]

    if streamer.open_log():
        try:
            if do_send_webhooks:
                webhook.send_log_event(
                    "Macro Started!",
                    0x00FF00
                )
            print("Macro Started!")
            first_run = True

            current_biome = None
            asset = None

            while True:

                for line in streamer.get_new_lines():

                    change = detector.process_line(line)

                    if change:
                        if "status" in change:
                            if change["status"] == "lost_connection":
                                if detector.roblox_running():
                                    print("Automatic disconnection confirmed.")
                                    rejoiner.launch_roblox()
                                    time.sleep(cfg.settings["Rejoin_Wait_Time"])
                                    pressed_join = False
                                    while not pressed_join:
                                        pressed_join = controller.press_join()
                                        if not pressed_join:
                                            time.sleep(2)

                                    return True
                                else:
                                    print("Disconnection marked as manual.")
                                    return False

                        if first_run:
                            first_run = False
                            continue

                        print(change)

                        if "aura" in change:
                            if do_send_webhooks:
                                webhook.send_log_event(
                                    f"Aura Equipped/Found: {change['aura']}",
                                    0x00FFE1
                                )
                            print(f'Aura Equipped: {change['aura']}')

                        if "biome" in change:
                            previous_biome = current_biome
                            previous_asset = asset
                            current_biome = change['biome']
                            asset = change['asset_id']

                            if previous_biome and previous_biome != "NORMAL":
                                if do_send_webhooks:
                                    webhook.send_log_event(
                                        f"Biome Ended: {previous_biome}",
                                        0x00FFE1,
                                        asset_id=previous_asset
                                    )

                            if current_biome != "NORMAL":
                                if do_send_webhooks:
                                    webhook.send_log_event(
                                        f"Biome Started: {current_biome}",
                                        0x00FFE1,
                                        ps_included=True,
                                        asset_id=asset
                                    )
                            print(f'Biome Started: {current_biome}')

                if do_anti_afk:
                    controller.anti_afk()

                if do_strange_controller:
                    controller.use_strange_controller(webhook)

                if do_biome_randomizer:
                    controller.use_biome_randomizer(webhook)

                time.sleep(.1)
        except KeyboardInterrupt:
            streamer.close()
            if do_send_webhooks:
                webhook.send_log_event(
                    "Macro Stopped!",
                    0xFF0000
                )
            print("Macro Stopped!")

if __name__ == "__main__":
    while True:
        try:
            rejoined = main()

            if not rejoined:
                print("Stopping macro.")
                sys.exit()

            print("Macro restarting.")
            time.sleep(2)
        except KeyboardInterrupt:
            print("Macro manually stopped.")
            sys.exit()
        except Exception as e:
            print(f"Error: {e}")
            sys.exit()