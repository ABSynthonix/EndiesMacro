import os.path
import sys
import ctypes
import time

import utils.globals
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                             QVBoxLayout, QPushButton, QLabel, QTextEdit,
                             QFrame, QListWidget, QStackedWidget, QLineEdit, QFormLayout, QSpinBox, QCheckBox,
                             QScrollArea)
from PyQt6.QtGui import QIcon
from interface_style import STYLE_SHEET
from macro_script import MacroScript
from utils.globals import MACRO_NAME

class EndieMacroUI(QMainWindow):
    def __init__(self):
        super().__init__()

        icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.set_taskbar_id()
        self.setWindowTitle(MACRO_NAME)
        self.resize(1100, 700)
        self.worker = None
        self.running = False
        self.setup_ui()
        self.setStyleSheet(STYLE_SHEET)

    def set_taskbar_id(self):
        shell32 = ctypes.WinDLL('shell32')
        shell32.SetCurrentProcessExplicitAppUserModelID("endye.macro.1")

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(240)
        s_layout = QVBoxLayout(sidebar)
        s_layout.setContentsMargins(20, 30, 20, 30)

        title = QLabel(MACRO_NAME)
        title.setObjectName("Title")
        s_layout.addWidget(title)

        self.btn_home = QPushButton("  Home")
        self.btn_home.setObjectName("NavBtn")
        self.btn_home.setIcon(QIcon("home.png"))
        self.btn_home.setCheckable(True)
        self.btn_home.setChecked(True)

        self.btn_settings = QPushButton("  Settings")
        self.btn_settings.setObjectName("NavBtn")
        self.btn_settings.setIcon(QIcon("settings.png"))
        self.btn_settings.setCheckable(True)

        self.btn_home.clicked.connect(lambda: self.switch_page(0))
        self.btn_settings.clicked.connect(lambda: self.switch_page(1))

        s_layout.addWidget(self.btn_home)
        s_layout.addWidget(self.btn_settings)
        s_layout.addSpacing(20)

        self.start_btn = QPushButton("START MACRO")
        self.start_btn.setObjectName("StartBtn")
        self.start_btn.clicked.connect(self.start_macro)

        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("StopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_macro)

        s_layout.addWidget(self.start_btn)
        s_layout.addWidget(self.stop_btn)
        s_layout.addStretch()

        self.pages = QStackedWidget()
        self.setup_home_page()
        self.setup_settings_page()

        layout.addWidget(sidebar)
        layout.addWidget(self.pages)

    def setup_home_page(self):
        page = QWidget()
        layout = QHBoxLayout(page)

        left_widget = QWidget()
        left_col = QVBoxLayout(left_widget)
        self.status_label = QLabel("Status: Idle")
        self.console = QTextEdit()
        self.console.setObjectName("Console")
        self.console.setReadOnly(True)
        left_col.addWidget(self.status_label)
        left_col.addWidget(self.console)

        right_widget = QWidget()
        right_widget.setFixedWidth(200)
        right_col = QVBoxLayout(right_widget)

        biome_title = QLabel("BIOMES FOUND")
        biome_title.setStyleSheet("font-size: 11px; color: #8E8E93;")
        right_col.addWidget(biome_title)

        self.biome_list = QListWidget()
        self.biome_list.setObjectName("BiomeList")
        right_col.addWidget(self.biome_list)

        layout.addWidget(left_widget)
        layout.addWidget(right_widget)

        self.pages.addWidget(page)

    def setup_settings_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(40, 40, 40, 40)

        form = QFormLayout()
        cfg = utils.globals.config.settings

        net_label = QLabel("NETWORK & WEBHOOKS")
        net_label.setObjectName("SectionTitle")
        layout.addWidget(net_label)

        self.edit_ps = QLineEdit(cfg.get("Private_Server_Link", ""))
        self.edit_webhook = QLineEdit(cfg.get("Webhook", ""))
        self.chk_send_webhook = QCheckBox("Send Webhooks")
        self.chk_send_webhook.setChecked(cfg.get("Send_Webhook", True))

        form.addRow("PS Link:", self.edit_ps)
        form.addRow("Webhook URL:", self.edit_webhook)
        form.addRow(self.chk_send_webhook)

        auto_label = QLabel("AUTOMATION TOGGLES")
        auto_label.setObjectName("SectionTitle")
        form.addRow(auto_label)

        self.chk_rejoin = QCheckBox("Auto Rejoin")
        self.chk_rejoin.setChecked(cfg.get("Auto_Rejoin", True))
        self.chk_afk = QCheckBox("Anti AFK")
        self.chk_afk.setChecked(cfg.get("Anti_AFK", True))
        self.chk_biome_rand = QCheckBox("Use Biome Randomizer")
        self.chk_biome_rand.setChecked(cfg.get("Use_Biome_Randomizer", False))
        self.chk_strange = QCheckBox("Use Strange Controller")
        self.chk_strange.setChecked(cfg.get("Use_Strange_Controller", False))

        form.addRow(self.chk_rejoin)
        form.addRow(self.chk_afk)
        form.addRow(self.chk_biome_rand)
        form.addRow(self.chk_strange)

        time_label = QLabel("TIMINGS & RANGES")
        time_label.setObjectName("SectionTitle")
        form.addRow(time_label)

        self.spin_disconnect = QSpinBox()
        self.spin_disconnect.setRange(1, 60)
        self.spin_disconnect.setValue(cfg.get("Disconnect_Detection_Time", 5))
        self.spin_wait = QSpinBox()
        self.spin_wait.setRange(1, 300)
        self.spin_wait.setValue(cfg.get("Rejoin_Wait_Time", 30))
        self.spin_afk_min = QSpinBox()
        self.spin_afk_min.setRange(1, 2000)
        self.spin_afk_min.setValue(cfg.get("Anti_AFK_Range_Min", 135))
        self.spin_afk_max = QSpinBox()
        self.spin_afk_max.setRange(1, 2000)
        self.spin_afk_max.setValue(cfg.get("Anti_AFK_Range_Max", 713))

        form.addRow("Disconnect Detect (s):", self.spin_disconnect)
        form.addRow("Rejoin Delay (s):", self.spin_wait)
        form.addRow("AFK Min Range:", self.spin_afk_min)
        form.addRow("AFK Max Range:", self.spin_afk_max)

        layout.addLayout(form)

        save_btn = QPushButton("SAVE ALL SETTINGS [ reload ]")
        save_btn.setObjectName("SaveBtn")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)

        layout.addStretch()
        self.pages.addWidget(scroll)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)
        self.btn_home.setChecked(index == 0)
        self.btn_settings.setChecked(index == 1)

    def save_config(self):
        new_settings = utils.globals.config.settings

        new_settings["Private_Server_Link"] = self.edit_ps.text()
        new_settings["Webhook"] = self.edit_webhook.text()

        new_settings["Auto_Rejoin"] = self.chk_rejoin.isChecked()
        new_settings["Anti_AFK"] = self.chk_afk.isChecked()
        new_settings["Send_Webhook"] = self.chk_send_webhook.isChecked()
        new_settings["Use_Biome_Randomizer"] = self.chk_biome_rand.isChecked()
        new_settings["Use_Strange_Controller"] = self.chk_strange.isChecked()

        new_settings["Disconnect_Detection_Time"] = self.spin_disconnect.value()
        new_settings["Rejoin_Wait_Time"] = self.spin_wait.value()
        new_settings["Anti_AFK_Range_Min"] = self.spin_afk_min.value()
        new_settings["Anti_AFK_Range_Max"] = self.spin_afk_max.value()

        utils.globals.config.save_config(new_settings)

        if self.running:
            self.stop_macro()
            time.sleep(0.5)
            self.start_macro()

        self.update_console("Settings Saved Successfully.")

    def start_macro(self):
        self.running = True
        self.worker = MacroScript()
        self.worker.log_signal.connect(self.update_console)
        self.worker.status_signal.connect(self.update_status)
        self.worker.stat_signal.connect(self.handle_stats)
        self.worker.start()
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_macro(self):
        if self.worker:
            self.running = False
            self.worker.stop()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def update_console(self, text):
        self.console.append(f"> {text}")
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def update_status(self, status):
        self.status_label.setText(f"Status: {status}")

    def handle_stats(self, data):
        if data.get("type") == "biome":
            self.biome_list.insertItem(0, data.get("val"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EndieMacroUI()
    window.show()
    sys.exit(app.exec())