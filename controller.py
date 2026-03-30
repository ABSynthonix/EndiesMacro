import time
import random
import pydirectinput
import win32gui
import win32con
import win32com.client
import utils.globals

class Controller:
    def __init__(self):
        self.last_movement = time.time()
        self.cfg = utils.globals.config

        self.use_item_sequence = utils.globals.item_in_inventory_sequence

        self.anti_afk_interval_min = self.cfg.settings["Anti_AFK_Range_Min"]
        self.anti_afk_interval_max = self.cfg.settings["Anti_AFK_Range_Max"]
        self.send_webhook = self.cfg.settings["Send_Webhook"]

        self.anti_afk_interval = random.randint(self.anti_afk_interval_min, self.anti_afk_interval_max)

        self.br_interval = 60 * 36
        self.last_br_use = time.time() - self.br_interval
        self.can_use_br = True

        self.sc_interval = 60 * 21
        self.last_sc_use = time.time() - self.sc_interval
        self.can_use_sc = True

        self.shell = win32com.client.Dispatch("WScript.Shell")

    def force_focus(self):
        """Force focus on Roblox's Window"""
        hwnd = win32gui.FindWindow(None, "Roblox")
        if not hwnd:
            return False

        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

            self.shell.SendKeys('%')

            win32gui.SetForegroundWindow(hwnd)
            win32gui.SetActiveWindow(hwnd)
            return True
        except Exception as e:
            print(f'Focus Error: {e}')
            return False

    def press_low_delay(self, input):
        pydirectinput.keyDown(input)
        time.sleep(.02)
        pydirectinput.keyUp(input)

    def anti_afk(self):
        current_time = time.time()
        if (current_time - self.last_movement) > self.anti_afk_interval:
            print("Attempting Anti-AFK.")

            prev_hwnd = win32gui.GetForegroundWindow()

            if self.force_focus():
                time.sleep(.5)

                pydirectinput.press('right')
                time.sleep(.1)
                pydirectinput.press('left')

                if prev_hwnd and prev_hwnd != win32gui.FindWindow(None, "Roblox"):
                    try:
                        win32gui.SetForegroundWindow(prev_hwnd)
                    except:
                        pass

                self.last_movement = current_time
                self.anti_afk_interval = random.randint(self.anti_afk_interval_min, self.anti_afk_interval_max)
                return True
        return False

    def press_join(self):
        prev_hwnd = win32gui.GetForegroundWindow()

        if self.force_focus():
            time.sleep(.5)

            pydirectinput.press('\\')
            time.sleep(.5)
            pydirectinput.press('down')
            time.sleep(.5)
            pydirectinput.press('enter')
            time.sleep(.5)
            pydirectinput.press('\\')

            if prev_hwnd and prev_hwnd != win32gui.FindWindow(None, "Roblox"):
                try:
                    print("setting focus back")
                    win32gui.SetForegroundWindow(prev_hwnd)
                except:
                    pass
            return True

        print("no prev to focus")
        return False

    def use_item(self, name):
        prev_hwnd = win32gui.GetForegroundWindow()

        if self.force_focus():
            time.sleep(.5)

            for input in self.use_item_sequence:
                if input == "ITEM_HERE":
                    for char in name:
                        if char == " ":
                            self.press_low_delay('space')
                        else:
                            self.press_low_delay(char)
                        print(char)
                else:
                    self.press_low_delay(input)
                    print(input)

        if prev_hwnd and prev_hwnd != win32gui.FindWindow(None, "Roblox"):
            try:
                print("setting focus back")
                win32gui.SetForegroundWindow(prev_hwnd)
            except:
                pass

    def use_biome_randomizer(self, webhook):
        current_time = time.time()

        if self.can_use_br and (current_time - self.last_br_use) > self.br_interval:
            self.can_use_br = False
            self.can_use_sc = False

            self.use_item("biome randomizer")
            if self.send_webhook: webhook.send_log_event("Biome Randomizer Used")

            self.last_br_use = current_time
            self.can_use_br = True
            self.can_use_sc = True

    def use_strange_controller(self, webhook):
        current_time = time.time()

        if self.can_use_sc and (current_time - self.last_sc_use) > self.sc_interval:
            self.can_use_sc = False
            self.can_use_br = False

            self.use_item("strange controller")
            if self.send_webhook: webhook.send_log_event("Strange Controller Used")

            self.last_sc_use = current_time
            self.can_use_sc = True
            self.can_use_br = True