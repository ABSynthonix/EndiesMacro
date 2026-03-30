STYLE_SHEET = """
QMainWindow { background-color: #0B0B0E; }

QFrame#Sidebar {
    background-color: #121217;
    border-right: 1px solid #1E1E24;
}

QLabel { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
QLabel#Title { font-size: 18px; font-weight: bold; margin-bottom: 20px; }
QLabel#SectionTitle { font-size: 12px; color: #8E8E93; font-weight: bold; margin-top: 10px; }

QPushButton#NavBtn {
    background-color: transparent;
    color: #8E8E93;
    text-align: left;
    padding: 12px;
    border-radius: 8px;
    font-size: 14px;
    border: none;
}
QPushButton#NavBtn:hover { background-color: #1E1E24; color: #FFFFFF; }
QPushButton#NavBtn:checked { background-color: #7708ff; color: #FFFFFF; }
QPushButton#StartBtn {
    padding: 8px;
}
QPushButton#StopBtn {
    padding: 8px;
}

QPushButton#SaveBtn {
    background-color: #7708ff;
    color: white;
    border-radius: 8px;
    padding: 15px;
    font-weight: bold;
    margin-top: 20px;
}

QLineEdit, QSpinBox {
    background-color: #1A1A20;
    color: white;
    border: 1px solid #333;
    border-radius: 5px;
    padding: 8px;
}

QCheckBox { color: white; spacing: 10px; }
QCheckBox::indicator { width: 18px; height: 18px; }

QScrollArea { border: none; background-color: transparent; }
"""