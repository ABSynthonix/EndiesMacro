import time

import config
from config import get_latest_log_file
from utils.detector import Detector
from utils.streamer import LogStreamer
from webhook_manager import Notifier

def main():
    log_path = get_latest_log_file()

    streamer = LogStreamer(log_path)
    detector = Detector()

    webhook = Notifier(config.Webhook, config.PS_Link)

    if streamer.open_log():
        try:
            webhook.send_log_event(
                "Macro Started!",
                0x00FF00
            )
            print("Macro Started!")
            first_run = True

            current_biome = None

            while True:
                for line in streamer.get_new_lines():
                    if line == "FORCE_RESTART":
                        break # Roblox Restart

                    change = detector.process_line(line)

                    if change:
                        if first_run:
                            first_run = False
                            continue

                        print(change)

                        if "aura" in change:
                            webhook.send_log_event(
                                f"Aura Equipped/Found: {change['aura']}",
                                0x00FFE1
                            )
                            print(f'Aura Equipped: {change['aura']}')

                        if "biome" in change:
                            previous_biome = current_biome
                            current_biome = change['biome']
                            asset = change['asset_id']

                            if previous_biome:
                                webhook.send_log_event(
                                    f"Biome Ended: {previous_biome}",
                                    0x00FFE1,
                                    asset_id=asset
                                )

                            if current_biome != "NORMAL":
                                webhook.send_log_event(
                                    f"Biome Started: {current_biome}",
                                    0x00FFE1,
                                    ps_included=True,
                                    asset_id=asset
                                )
                            print(f'Biome Started: {current_biome}')

                time.sleep(.1)
        except KeyboardInterrupt:
            streamer.close()
            webhook.send_log_event(
                "Macro Stopped!",
                0xFF0000
            )
            print("Macro Stopped!")

if __name__ == "__main__":
    main()