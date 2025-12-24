
import sys
import os
import json
import threading
import hashlib
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QPushButton, QDialog, 
                               QFormLayout, QLineEdit, QComboBox, QMessageBox, 
                               QFrame, QSizePolicy, QGraphicsDropShadowEffect,
                               QMenuBar, QMenu, QTabWidget, QTableWidget, QTableWidgetItem,
                               QHeaderView, QCheckBox, QScrollArea, QDialogButtonBox,
                               QAbstractItemView, QFileDialog, QListWidget, QInputDialog, QTextEdit)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread
from PySide6.QtGui import QFont, QColor, QPainter, QBrush, QAction, QIcon, QTextCursor

# --- Internationalization ---

class Translator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance.translations = {}
            cls._instance.current_lang = "en"
        return cls._instance
    
    def load_language(self, lang_code):
        self.current_lang = lang_code
        # Look in package 'locales' directory
        path = os.path.join(os.path.dirname(__file__), 'locales', f'{lang_code}.json')
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                return True
            except Exception as e:
                print(f"Error loading locale {lang_code}: {e}")
        return False

    def get(self, key, default=None):
        return self.translations.get(key, default or key)

# Global instance
_translator = Translator()

def T(key, default=None):
    return _translator.get(key, default)

# --- Utils ---
# Import the server module
import opscalesrv
from opscalesrv import load_opscalesrv_config, anpr

# --- Styling ---

STYLESHEET = """
* {
    color: #E0E0E0;
    selection-background-color: #BB86FC;
    selection-color: #000000;
}
QMainWindow, QDialog, QWidget {
    background-color: #121212;
}
QMenuBar {
    background-color: #121212;
    border-bottom: 1px solid #333333;
}
QMenuBar::item:selected {
    background-color: #333333;
}
QMenu {
    background-color: #1E1E1E;
    border: 1px solid #333333;
}
QMenu::item:selected {
    background-color: #BB86FC;
    color: #000000;
}
QLabel {
    background-color: transparent;
    border: none;
}
QPushButton {
    background-color: #2D2D2D;
    border: 1px solid #3E3E3E;
    border-radius: 4px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #3D3D3D;
    border: 1px solid #505050;
}
QPushButton:pressed {
    background-color: #505050;
}
QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit {
    background-color: #2D2D2D;
    border: 1px solid #3E3E3E;
    border-radius: 4px;
    padding: 6px;
    color: #FFFFFF;
}
QComboBox::drop-down {
    border: none;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #E0E0E0;
    margin-right: 5px;
}
QComboBox QAbstractItemView {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    selection-background-color: #BB86FC;
    selection-color: #000000;
}
QTableWidget, QTableView {
    background-color: #1E1E1E;
    gridline-color: #333333;
    border: 1px solid #333333;
}
QTableWidget::item, QTableView::item {
    background-color: #1E1E1E;
}
QTableWidget::item:selected, QTableView::item:selected {
    background-color: #BB86FC;
    color: #000000;
}
QHeaderView, QHeaderView::section {
    background-color: #2D2D2D;
    color: #FFFFFF;
    padding: 4px;
    border: none;
    border-right: 1px solid #333333;
    border-bottom: 1px solid #333333;
}
QCheckBox {
    spacing: 5px;
    background-color: transparent;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #3E3E3E;
    background-color: #2D2D2D;
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background-color: #BB86FC;
    border-color: #BB86FC;
}
QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
    background-color: #121212;
    border: none;
}
QScrollBar:vertical {
    border: none;
    background: #121212;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #3E3E3E;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QTabWidget::pane {
    border: 1px solid #333333;
    background-color: #121212;
}
QTabBar::tab {
    background-color: #1E1E1E;
    border: 1px solid #333333;
    padding: 8px 12px;
    color: #B0B0B0;
}
QTabBar::tab:selected {
    background-color: #BB86FC;
    color: #000000;
}
ModernFrame {
    background-color: #1E1E1E;
}
"""

class SignalManager(QObject):
    request_received = Signal(dict)

# Global signal manager
signal_manager = SignalManager()

def server_callback(data):
    signal_manager.request_received.emit(data)

# --- Configuration Manager ---

class ConfigManager:
    @staticmethod
    def get_default_config():
        """Return default configuration without password"""
        return {
            "allowed_hosts": [
                {
                    "ip": "127.0.0.1",
                    "ports": [7373, 7374, 7375, 7376, 7377, 7378, 7379, 7380, 7381, 8080],
                    "description": "Localhost access"
                },
                {
                    "ip": "192.168.1.53",
                    "ports": [7373, 7374, 7375, 7376, 7377, 7378, 7379, 7380, 7381, 8080],
                    "description": "Local network access"
                },
                {
                    "ip": "localhost",
                    "ports": [7373, 7374, 7375, 7376, 7377, 7378, 7379, 7380, 7381, 8080],
                    "description": "Localhost hostname access"
                }
            ],
            "serial": {
                "port": "/dev/ttyUSB0",
                "baudrate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1,
                "timeout": 1,
                "xonxoff": False,
                "rtscts": False,
                "dsrdtr": False,
                "write_timeout": None,
                "inter_byte_timeout": None,
                "exclusive": None,
                "description": "Serial port configuration for data reading - all pyserial parameters supported"
            },
            "settings": {
                "log_file": "requests.log",
                "deny_unknown_hosts": True,
                "log_all_requests": True,
                "encode": "utf-8",
                "language": "en",
                "name": "OpScale Server",
                "port": 7373
            },
            "anpr": {
                "enabled": False,
                "timeout": 10,
                "entrance": {
                    "server": "10.10.145.36",
                    "port": 80,
                    "URL": "/ISAPI/Event/notification/alertStream",
                    "username": "admin",
                    "password": "",
                    "plate": "licensePlate"
                },
                "exit": {
                    "server": "10.10.145.36",
                    "port": 80,
                    "URL": "/ISAPI/Event/notification/alertStream",
                    "username": "admin",
                    "password": "",
                    "plate": "licensePlate"
                }
            }
        }
    
    @staticmethod
    def load_config():
        config_path = 'opscalesrv.json'
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        # If config doesn't exist, create it with defaults
        default_config = ConfigManager.get_default_config()
        ConfigManager.save_config(default_config)
        return default_config

    @staticmethod
    def save_config(config):
        config_path = 'opscalesrv.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    @staticmethod
    def reset_to_default():
        """Reset configuration to default values"""
        default_config = ConfigManager.get_default_config()
        ConfigManager.save_config(default_config)
        return default_config

# --- Custom Widgets ---

class TrafficLight(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 80)
        self.state = "IDLE" 
        self.color = QColor("#FFC107")  # Initial state (Yellow)
        
        # Glow effect
        self.glow = QGraphicsDropShadowEffect(self)
        self.glow.setBlurRadius(30)
        self.glow.setColor(self.color)
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)

    def set_state(self, status):
        """
        Status can be:
        - True (bool): Treated as 'OK'
        - False (bool): Treated as 'FAIL'
        - 'OK' (str): Green
        - 'FAIL' (str): Red
        - 'IDLE' (str): Yellow
        """
        if isinstance(status, bool):
            self.state = 'OK' if status else 'FAIL'
        else:
            self.state = str(status).upper()

        if self.state == 'OK':
            self.color = QColor("#00E676")  # Green
        elif self.state == 'FAIL':
            self.color = QColor("#FF5252")  # Red
        else:
            self.color = QColor("#FFC107")  # Yellow (IDLE)
        
        self.glow.setColor(self.color)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background
        painter.setBrush(QBrush(self.color.darker(180)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(10, 10, 60, 60)
        
        # Draw active circle - Always draw roughly same size but color changes
        # For 'dimmed' look we could use darker color, but user wants 'Yellow', 'Red', 'Green'
        # Let's make it always 'active' looking so the color is visible.
        painter.setBrush(QBrush(self.color))
        painter.drawEllipse(15, 15, 50, 50)

class ModernFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            ModernFrame {
                background-color: #1E1E1E;
                border-radius: 12px;
                border: 1px solid #333333;
            }
        """)

# --- Settings Dialogs ---

class SerialSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_serial_settings"))
        self.resize(400, 500)
        layout = QVBoxLayout(self)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.form_layout = QFormLayout(content)
        
        self.inputs = {}
        self.config = ConfigManager.load_config().get('serial', {})
        
        # Define fields based on JSON structure
        self.add_field("port", T("lbl_port"), str)
        self.add_field("baudrate", T("lbl_baudrate"), int, options=["9600", "19200", "38400", "57600", "115200"])
        self.add_field("bytesize", T("lbl_bytesize"), int, options=["5", "6", "7", "8"])
        self.add_field("parity", T("lbl_parity"), str, options=["N", "E", "O", "M", "S"])
        self.add_field("stopbits", T("lbl_stopbits"), float, options=["1", "1.5", "2"])
        self.add_field("timeout", T("lbl_timeout_s"), float)
        self.add_field("xonxoff", T("lbl_xonxoff"), bool)
        self.add_field("rtscts", T("lbl_rtscts"), bool)
        self.add_field("dsrdtr", T("lbl_dsrdtr"), bool)
        self.add_field("write_timeout", T("lbl_write_timeout"), float, nullable=True)
        self.add_field("inter_byte_timeout", T("lbl_inter_byte_timeout"), float, nullable=True)
        self.add_field("exclusive", T("lbl_exclusive_access"), bool, nullable=True)

        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save_data)
        btns.rejected.connect(self.reject)

        btns.button(QDialogButtonBox.Save).setText(T("btn_save"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)

    def add_field(self, key, label, type_, options=None, nullable=False):
        val = self.config.get(key)
        
        if type_ == bool:
            widget = QCheckBox()
            widget.setChecked(bool(val))
            self.inputs[key] = (widget, type_)
        elif options:
            widget = QComboBox()
            widget.addItems(options)
            widget.setCurrentText(str(val) if val is not None else options[0])
            self.inputs[key] = (widget, type_)
        else:
            widget = QLineEdit()
            if val is not None:
                widget.setText(str(val))
            if nullable:
                widget.setPlaceholderText("None")
            self.inputs[key] = (widget, type_)
            
        self.form_layout.addRow(label, widget)

    def save_data(self):
        full_config = ConfigManager.load_config()
        new_serial_config = full_config.get('serial', {})
        
        for key, (widget, type_) in self.inputs.items():
            if type_ == bool:
                new_serial_config[key] = widget.isChecked()
            else:
                text = widget.currentText() if isinstance(widget, QComboBox) else widget.text()
                if not text and (isinstance(widget, QLineEdit) or widget.placeholderText() == "None"):
                    new_serial_config[key] = None
                else:
                    try:
                        if type_ == int:
                            new_serial_config[key] = int(text)
                        elif type_ == float:
                            new_serial_config[key] = float(text)
                        else:
                            new_serial_config[key] = text
                    except ValueError:
                        QMessageBox.warning(self, T("msg_invalid_input"), f"{T('msg_invalid_value_for')} {key}")
                        return

        full_config['serial'] = new_serial_config
        ConfigManager.save_config(full_config)
        self.accept()

class AllowedHostsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_allowed_hosts"))
        self.resize(600, 400)
        layout = QVBoxLayout(self)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([T("hdr_ip_address"), T("hdr_ports"), T("hdr_description")])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton(T("btn_add_host"))
        add_btn.clicked.connect(self.add_row)
        remove_btn = QPushButton(T("btn_remove_selected"))
        remove_btn.clicked.connect(self.remove_row)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(remove_btn)
        layout.addLayout(btn_layout)
        
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save_data)
        btns.rejected.connect(self.reject)

        btns.button(QDialogButtonBox.Save).setText(T("btn_save"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)
        
        self.load_data()

    def load_data(self):
        hosts = ConfigManager.load_config().get('allowed_hosts', [])
        self.table.setRowCount(len(hosts))
        for i, host in enumerate(hosts):
            self.table.setItem(i, 0, QTableWidgetItem(host.get('ip', '')))
            ports = ",".join(map(str, host.get('ports', [])))
            self.table.setItem(i, 1, QTableWidgetItem(ports))
            self.table.setItem(i, 2, QTableWidgetItem(host.get('description', '')))

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

    def remove_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)

    def save_data(self):
        hosts = []
        for i in range(self.table.rowCount()):
            ip = self.table.item(i, 0).text() if self.table.item(i, 0) else ""
            ports_str = self.table.item(i, 1).text() if self.table.item(i, 1) else ""
            desc = self.table.item(i, 2).text() if self.table.item(i, 2) else ""
            
            if not ip: continue
            
            try:
                ports = [int(p.strip()) for p in ports_str.split(',') if p.strip()]
            except ValueError:
                QMessageBox.warning(self, T("msg_invalid_input"), f"{T('msg_invalid_ports_format')} {ip}")
                return
                
            hosts.append({
                "ip": ip,
                "ports": ports,
                "description": desc
            })
            
        full_config = ConfigManager.load_config()
        full_config['allowed_hosts'] = hosts
        ConfigManager.save_config(full_config)
        self.accept()

class GeneralSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_general"))
        self.resize(400, 350)
        layout = QVBoxLayout(self)
        
        self.form_layout = QFormLayout()
        
        self.inputs = {}
        self.config = ConfigManager.load_config().get('settings', {})
        
        # Server Name
        self.add_field("name", T("lbl_server_name", "Server Name"), str)
        
        # Language Selection
        lang_val = self.config.get("language", "en")
        self.add_field("language", T("lbl_language"), list, options=["en", "tr", "de", "fr", "ru", "ja", "ko"], current=lang_val)
        
        self.add_field("port", T("lbl_port"), int)
        self.add_field("log_file", T("lbl_log_file"), str)
        self.add_field("encode", T("lbl_encoding"), str)
        self.add_field("deny_unknown_hosts", T("lbl_deny_hosts"), bool)
        self.add_field("log_all_requests", T("lbl_log_all"), bool)
        
        layout.addLayout(self.form_layout)
        
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save_data)
        btns.rejected.connect(self.reject)
        
        # Translate buttons
        btns.button(QDialogButtonBox.Save).setText(T("btn_save"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)

    def add_field(self, key, label, type_, options=None, current=None):
        val = self.config.get(key)
        if type_ == bool:
            widget = QCheckBox()
            widget.setChecked(bool(val))
        elif type_ == list:
            widget = QComboBox()
            if options:
                widget.addItems(options)
                if current and current in options:
                    widget.setCurrentText(current)
                elif val and str(val) in options: # Fallback for existing config
                    widget.setCurrentText(str(val))
        else:
            widget = QLineEdit()
            if val is not None: # Ensure 0 or False are not treated as empty
                widget.setText(str(val))
            
        self.inputs[key] = (widget, type_)
        self.form_layout.addRow(label, widget)

    def save_data(self):
        full_config = ConfigManager.load_config()
        new_settings = full_config.get('settings', {})
        
        for key, (widget, type_) in self.inputs.items():
            if type_ == bool:
                new_settings[key] = widget.isChecked()
            elif type_ == list:
                new_settings[key] = widget.currentText()
            else:
                text = widget.text()
                try:
                    if type_ == int:
                        new_settings[key] = int(text)
                    elif type_ == float:
                        new_settings[key] = float(text)
                    else:
                        new_settings[key] = text
                except ValueError:
                    QMessageBox.warning(self, T("msg_invalid_input"), f"{T('msg_invalid_value_for')} {key}")
                    return
                
        full_config['settings'] = new_settings
        ConfigManager.save_config(full_config)
        self.accept()

class CheckPasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_auth_required"))
        self.resize(300, 150)
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(T("lbl_enter_password")))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)

        btns.button(QDialogButtonBox.Ok).setText(T("btn_ok"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)
        
    def get_password(self):
        return self.password_edit.text()

class SetPasswordDialog(QDialog):
    def __init__(self, has_current_password=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_set_password"))
        self.resize(300, 200)
        self.has_current = has_current_password
        
        layout = QFormLayout(self)
        
        self.current_pwd = QLineEdit()
        self.current_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.EchoMode.Password)
        
        if has_current_password:
            layout.addRow(T("lbl_current_password"), self.current_pwd)
            
        layout.addRow(T("lbl_new_password"), self.new_pwd)
        layout.addRow(T("lbl_confirm_password"), self.confirm_pwd)
        
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.validate_and_save)
        btns.rejected.connect(self.reject)

        btns.button(QDialogButtonBox.Save).setText(T("btn_save"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)
        
    def validate_and_save(self):
        if self.new_pwd.text() != self.confirm_pwd.text():
            QMessageBox.warning(self, T("msg_error"), T("msg_passwords_no_match"))
            return
            
        self.accept()
        
    def get_data(self):
        return self.current_pwd.text(), self.new_pwd.text()

class ANPRSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_anpr"))
        self.resize(500, 450)
        
        self.config = ConfigManager.load_config().get('anpr', {})
        self.working_config = dict(self.config)
        
        # Ensure defaults exist
        default_cam = {
            "server": "10.10.145.36",
            "port": 80,
            "URL": "/ISAPI/Event/notification/alertStream",
            "username": "admin",
            "password": "",
            "plate": "licensePlate"
        }
        
        if 'entrance' not in self.working_config:
            self.working_config['entrance'] = default_cam.copy()
        if 'exit' not in self.working_config:
            self.working_config['exit'] = default_cam.copy()
        
        layout = QVBoxLayout(self)
        
        # Enabled Checkbox
        self.enabled_cb = QCheckBox(T("lbl_enable_anpr"))
        self.enabled_cb.setChecked(self.working_config.get('enabled', False))
        layout.addWidget(self.enabled_cb)
        
        layout.addSpacing(15)
        
        # Camera Selector
        sel_layout = QHBoxLayout()
        sel_layout.addWidget(QLabel(T("lbl_select_camera")))
        self.cam_selector = QComboBox()
        self.cam_selector.addItems([T("cam_entrance"), T("cam_exit")])
        self.cam_selector.currentTextChanged.connect(self.on_camera_changed)
        sel_layout.addWidget(self.cam_selector)
        sel_layout.addStretch()
        layout.addLayout(sel_layout)
        
        layout.addSpacing(10)
        
        # Form
        form_frame = QFrame()
        form_frame.setFrameShape(QFrame.StyledPanel)
        form_layout = QFormLayout(form_frame)
        
        self.server_edit = QLineEdit()
        self.port_edit = QLineEdit()
        self.url_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.timeout_edit = QLineEdit()
        self.plate_edit = QLineEdit()
        
        # Connect signals
        self.server_edit.textChanged.connect(lambda: self.update_val('server', self.server_edit.text()))
        self.port_edit.textChanged.connect(lambda: self.update_val('port', self.port_edit.text()))
        self.url_edit.textChanged.connect(lambda: self.update_val('URL', self.url_edit.text()))
        self.username_edit.textChanged.connect(lambda: self.update_val('username', self.username_edit.text()))
        self.password_edit.textChanged.connect(lambda: self.update_val('password', self.password_edit.text()))
        self.timeout_edit.textChanged.connect(self.update_anpr_timeout)
        self.plate_edit.textChanged.connect(lambda: self.update_val('plate', self.plate_edit.text()))
        
        form_layout.addRow(T("lbl_server_ip"), self.server_edit)
        form_layout.addRow(T("lbl_cam_port"), self.port_edit)
        form_layout.addRow(T("lbl_url"), self.url_edit)
        form_layout.addRow(T("lbl_username"), self.username_edit)
        form_layout.addRow(T("lbl_password"), self.password_edit)
        form_layout.addRow(T("lbl_timeout_s", "Timeout (s)"), self.timeout_edit)
        form_layout.addRow(T("lbl_plate"), self.plate_edit)
        
        layout.addWidget(form_frame)
        
        layout.addSpacing(10)
        
        # Test Button
        self.test_btn = QPushButton(T("btn_test"))
        self.test_btn.setStyleSheet("background-color: #3700B3; height: 35px;")
        self.test_btn.clicked.connect(self.test_camera_action)
        layout.addWidget(self.test_btn)
        
        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.save_data)
        btns.rejected.connect(self.reject)
        
        btns.button(QDialogButtonBox.Save).setText(T("btn_save"))
        btns.button(QDialogButtonBox.Cancel).setText(T("btn_cancel"))
        
        layout.addWidget(btns)
        
        # Initialize form
        self.on_camera_changed(T("cam_entrance"))

    def block_signals_form(self, block):
        self.server_edit.blockSignals(block)
        self.port_edit.blockSignals(block)
        self.url_edit.blockSignals(block)
        self.username_edit.blockSignals(block)
        self.password_edit.blockSignals(block)
        self.timeout_edit.blockSignals(block)
        self.plate_edit.blockSignals(block)

    def on_camera_changed(self, text):
        if not text: return
        # Map translated text back to internal keys 'entrance' or 'exit'
        if text == T("cam_entrance"):
            key = 'entrance'
        elif text == T("cam_exit"):
            key = 'exit'
        else:
            return # Should not happen
            
        data = self.working_config.get(key, {})
        
        self.block_signals_form(True)
        self.server_edit.setText(str(data.get('server', '')))
        self.port_edit.setText(str(data.get('port', '')))
        self.url_edit.setText(str(data.get('URL', '')))
        self.username_edit.setText(str(data.get('username', '')))
        self.password_edit.setText(str(data.get('password', '')))
        self.timeout_edit.setText(str(self.working_config.get('timeout', 10)))
        self.plate_edit.setText(str(data.get('plate', '')))
        self.block_signals_form(False)

    def update_anpr_timeout(self, value):
        try:
            self.working_config['timeout'] = int(value)
        except:
            pass

    def update_val(self, field, value):
        # Map translated text back to internal keys 'entrance' or 'exit'
        current_cam_text = self.cam_selector.currentText()
        if current_cam_text == T("cam_entrance"):
            key = 'entrance'
        elif current_cam_text == T("cam_exit"):
            key = 'exit'
        else:
            return # Should not happen

        if key not in self.working_config:
            self.working_config[key] = {}
            
        if field == 'port':
            try:
                self.working_config[key][field] = int(value)
            except:
                self.working_config[key][field] = value
        else:
            self.working_config[key][field] = value

    def save_data(self):
        self.working_config['enabled'] = self.enabled_cb.isChecked()
        
        full_config = ConfigManager.load_config()
        full_config['anpr'] = self.working_config
        ConfigManager.save_config(full_config)
        self.accept()

    def test_camera_action(self):
        # Map translated text back to internal keys 'entrance' or 'exit'
        current_cam_text = self.cam_selector.currentText()
        if current_cam_text == T("cam_entrance"):
            key = 'entrance'
        elif current_cam_text == T("cam_exit"):
            key = 'exit'
        else:
            return
            
        # Get current settings from form
        cam_settings = dict(self.working_config.get(key, {}))
        cam_settings['timeout'] = self.working_config.get('timeout', 10)
        
        # Disable button and show status
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing... (Window Responsive)")
        QApplication.setOverrideCursor(Qt.WaitCursor)
        
        # Start background thread
        self.test_thread = CameraTestThread(cam_settings)
        self.test_thread.finished.connect(self.on_test_finished)
        self.test_thread.error.connect(self.on_test_error)
        self.test_thread.start()

    def on_test_error(self, err_msg):
        QApplication.restoreOverrideCursor()
        self.test_btn.setEnabled(True)
        self.test_btn.setText(T("btn_test"))
        QMessageBox.critical(self, T("msg_error"), f"Test failed: {err_msg}")

    def on_test_finished(self, result):
        QApplication.restoreOverrideCursor()
        self.test_btn.setEnabled(True)
        self.test_btn.setText(T("btn_test"))
        
        xml_data, http_status, parsed_plate = result
        
        # Show in a dialog
        dlg = QDialog(self)
        dlg.setWindowTitle(T("title_anpr_test"))
        dlg.resize(800, 600)
        d_lay = QVBoxLayout(dlg)
        
        # INFO Header
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.StyledPanel)
        info_frame.setStyleSheet("background-color: #2C2C2C; border-radius: 5px;")
        info_lay = QFormLayout(info_frame)
        
        status_lbl = QLabel(str(http_status))
        status_lbl.setStyleSheet(f"font-weight: bold; color: {'#4CAF50' if http_status == 200 else '#F44336'};")
        
        plate_lbl = QLabel(parsed_plate)
        plate_lbl.setStyleSheet("font-weight: bold; color: #BB86FC; font-size: 14px;")
        
        info_lay.addRow("HTTP Status Code:", status_lbl)
        info_lay.addRow("Parsed Plate (SAP):", plate_lbl)
        
        d_lay.addWidget(info_lay.parentWidget())
        d_lay.addWidget(QLabel("Raw Camera Response (XML):"))
        
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(xml_data)
        txt.setFont(QFont("Courier New", 10))
        d_lay.addWidget(txt)
        
        close_btn = QPushButton(T("btn_ok"))
        close_btn.setStyleSheet("height: 40px; font-weight: bold;")
        close_btn.clicked.connect(dlg.accept)
        d_lay.addWidget(close_btn)
        
        dlg.exec()

# --- Background Camera Test Thread ---

class CameraTestThread(QThread):
    finished = Signal(tuple)
    error = Signal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def run(self):
        try:
            result = anpr.test_camera(self.settings)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# --- Background Server Thread ---

class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        
    def run(self):
        load_opscalesrv_config()
        config = ConfigManager.load_config()
        port = int(config.get('settings', {}).get('port', 7373))
        
        opscalesrv.ON_REQUEST_CALLBACK = server_callback
        try:
            opscalesrv.start_server(port=port, host='0.0.0.0')
        except Exception as e:
            print(f"Server error: {e}")

class LogViewerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(T("title_logs"))
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setFont(QFont("Monospace", 10))
        layout.addWidget(self.text_edit)
        
        self.load_logs()
        
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton(T("btn_refresh", "Refresh")) # Fallback if key missing
        refresh_btn.clicked.connect(self.load_logs)
        close_btn = QPushButton(T("btn_close", "Close")) # Fallback
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        
    def load_logs(self):
        config = ConfigManager.load_config()
        log_file = config.get('settings', {}).get('log_file', 'requests.log')
        
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Show last 1000 lines if too large? 
                    # For now show all, text edit handles reasonably sized files.
                    self.text_edit.setText(content)
                    self.text_edit.moveCursor(QTextCursor.End)
            except Exception as e:
                self.text_edit.setText(f"Error reading log file: {e}")
        else:
            self.text_edit.setText("Log file not found.")

# --- Main Window ---

class MainWindow(QMainWindow):
    request_signal = Signal(dict)

    def __init__(self):
        super().__init__()
        
        # Connect signal
        self.request_signal.connect(self.update_ui_from_request)
        
        # Load Language
        config = ConfigManager.load_config()
        lang = config.get('settings', {}).get('language', 'en')
        _translator.load_language(lang)
        
        self.setWindowTitle(T("app_title"))
        self.resize(480, 320)
        
        # Menu Bar
        self.create_menu_bar()
        
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header Area
        header_layout = QHBoxLayout()
        
        # Use configured name or default "Monitoring Panel"
        srv_name = config.get('settings', {}).get('name', '')
        if not srv_name:
            srv_name = T("lbl_monitoring", "Monitoring Panel")
            
        title_lbl = QLabel(srv_name)
        title_lbl.setStyleSheet("font-size: 16px; color: #888888; font-weight: bold;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        
        # Content Area - Card Like
        content_frame = ModernFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Left: Traffic Light
        self.traffic_light = TrafficLight()
        content_layout.addWidget(self.traffic_light, 0, Qt.AlignVCenter)
        
        content_layout.addSpacing(20)
        
        # Right: Values
        value_layout = QVBoxLayout()
        
        # ANPR Plate Label (Hidden by default, shown if enabled in config)
        self.plate_label = QLabel(T("lbl_no_plate"))
        self.plate_label.setAlignment(Qt.AlignCenter)
        self.plate_label.setStyleSheet("""
            background-color: white;
            color: black;
            border: 2px solid #333333;
            border-radius: 4px;
            padding: 4px 10px;
            font-size: 24px;
            font-weight: bold;
            font-family: monospace;
        """)
        self.plate_label.hide() # Hide by default
        
        # Check config for ANPR
        config = ConfigManager.load_config()
        if config.get('anpr', {}).get('enabled', False):
            self.plate_label.show()
        
        self.value_label = QLabel("--.--")
        self.value_label.setFont(QFont("Segoe UI", 42, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("color: #BB86FC;")
        
        self.value_label.setStyleSheet("color: #BB86FC;")
        
        self.msg_label = QLabel(T("lbl_no_data"))
        self.msg_label.setAlignment(Qt.AlignRight)
        self.msg_label.setStyleSheet("color: #888888; font-size: 12px;")
        
        self.time_label = QLabel("")
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet("color: #666666; font-size: 10px;")
        
        value_layout.addStretch()
        value_layout.addWidget(self.plate_label, 0, Qt.AlignRight) # Align right to match values
        value_layout.addSpacing(10)
        value_layout.addWidget(self.value_label)
        value_layout.addWidget(self.msg_label)
        value_layout.addWidget(self.time_label)
        value_layout.addStretch()
        
        content_layout.addLayout(value_layout)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(content_frame)
        
        # Status Bar
        self.status_bar = QLabel(T("status_initial"))
        self.status_bar.setStyleSheet("color: #666666; font-size: 11px;")
        self.status_bar.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_bar)

        # Timers & Signals
        self.reset_timer = QTimer()
        self.reset_timer.timeout.connect(self.reset_state)
        
        signal_manager.request_received.connect(self.handle_request)
        
        # Start Server Daemon Thread
        self.server_thread = ServerThread()
        self.server_thread.start()

    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Server Menu
        server_menu = menubar.addMenu(T("menu_server"))
        
        # Restart Action
        restart_act = QAction(T("act_restart"), self)
        restart_act.triggered.connect(self.restart_server)
        server_menu.addAction(restart_act)
        
        # Test Mode Action (Moved to Server)
        self.test_mode_act = QAction(T("act_test_mode"), self, checkable=True)
        self.test_mode_act.setChecked(opscalesrv.TEST_MODE)
        self.test_mode_act.triggered.connect(self.toggle_test_mode)
        server_menu.addAction(self.test_mode_act)
        
        server_menu.addSeparator()
        
        # Set Password Action
        pwd_act = QAction(T("act_set_password"), self)
        pwd_act.triggered.connect(self.open_set_password)
        server_menu.addAction(pwd_act)
        
        # ABAP Generation Action
        abap_act = QAction(T("act_gen_abap"), self)
        abap_act.triggered.connect(self.generate_abap_code)
        server_menu.addAction(abap_act)
        
        server_menu.addSeparator()
        
        # Exit Action
        exit_act = QAction(T("act_exit"), self)
        exit_act.triggered.connect(self.close)
        server_menu.addAction(exit_act)
        
        # Settings Menu
        settings_menu = menubar.addMenu(T("menu_settings"))
        
        serial_act = QAction(T("act_serial"), self)
        serial_act.triggered.connect(self.open_serial_settings)
        settings_menu.addAction(serial_act)
        
        hosts_act = QAction(T("act_hosts"), self)
        hosts_act.triggered.connect(self.open_hosts_settings)
        settings_menu.addAction(hosts_act)
        
        general_act = QAction(T("act_general"), self)
        general_act.triggered.connect(self.open_general_settings)
        settings_menu.addAction(general_act)
        
        anpr_act = QAction(T("act_anpr"), self)
        anpr_act.triggered.connect(self.open_anpr_settings)
        settings_menu.addAction(anpr_act)
        
        settings_menu.addSeparator()
        
        reset_act = QAction(T("act_reset_settings", "Reset Settings"), self)
        reset_act.triggered.connect(self.reset_settings)
        settings_menu.addAction(reset_act)
        
        # Logs Menu
        logs_menu = menubar.addMenu(T("menu_logs", "Logs"))
        
        show_log_act = QAction(T("act_show_log", "Show Logs"), self)
        show_log_act.triggered.connect(self.show_logs)
        logs_menu.addAction(show_log_act)
        
        clear_log_act = QAction(T("act_clear_log", "Clear Logs"), self)
        clear_log_act.triggered.connect(self.clear_logs)
        logs_menu.addAction(clear_log_act)
        
        # Help Menu
        help_menu = menubar.addMenu(T("menu_help"))
        
        about_act = QAction(T("act_about"), self)
        about_act.triggered.connect(self.show_about)
        help_menu.addAction(about_act)

    def generate_abap_code(self):
        if not self.check_password():
            return
            
        dir_path = QFileDialog.getExistingDirectory(self, T("title_select_abap_dir"))
        if dir_path:
            try:
                # We need to manually invoke the copy logic or reimplement it since copy_abap_files 
                # in __init__.py targets os.getcwd() and is a bit rigid.
                # Let's read from package source and write to selected dir.
                
                package_dir = os.path.dirname(opscalesrv.__file__)
                abap_source_dir = os.path.join(package_dir, 'abap')
                
                if not os.path.exists(abap_source_dir):
                    QMessageBox.warning(self, T("msg_error"), f"{T('msg_abap_dir_not_found')}: {abap_source_dir}")
                    return

                files = [f for f in os.listdir(abap_source_dir) if f.endswith('.abap')]
                if not files:
                    QMessageBox.warning(self, T("msg_error"), T("msg_no_abap_files"))
                    return
                
                import shutil
                copied_count = 0
                for f in files:
                    src = os.path.join(abap_source_dir, f)
                    dst = os.path.join(dir_path, f)
                    shutil.copy2(src, dst)
                    copied_count += 1
                
                QMessageBox.information(self, T("msg_success"), f"{T('msg_abap_saved_to')}:\n{dir_path}")
                
            except Exception as e:
                QMessageBox.critical(self, T("msg_error"), f"{T('msg_failed_gen_abap')}: {e}")

    def restart_server(self):
        # Password check removed as per user request
        # if not self.check_password():
        #     return

        self.status_bar.setText(T("status_restarting"))
        self.traffic_light.set_state("IDLE")  # Set to Yellow
        QApplication.processEvents()
        
        # Stop existing server
        opscalesrv.stop_server()
        
        # Wait a bit for shutdown
        import time
        time.sleep(0.5)
        
        # Start new thread
        self.server_thread = ServerThread()
        self.server_thread.start()
        
        # Update status
        config = ConfigManager.load_config()
        port = config.get('settings', {}).get('port', 7373)
        self.status_bar.setText(f"{T('status_server_restarted')} | {T('lbl_port')}: {port} | {T('status_waiting_requests')}")
        QMessageBox.information(self, T("title_server_restarted"), f"{T('msg_server_restarted_on_port')} {port}")

    def handle_request(self, data):
        """
        Callback from background server thread.
        Emit signal to update UI on main thread.
        """
        self.request_signal.emit(data)

    def update_ui_from_request(self, data):
        """
        Slot to update UI on main thread
        """
        # Ignore favicon requests to prevent overwriting relevant data
        path = data.get('path', '')
        if path and 'favicon.ico' in path:
            return

        # Handle case where response_data might be None (e.g. from check_access logging)
        resp = data.get('response_data')
        if not resp:
            # Maybe just update status bar for access checks?
            client = f"{data.get('client_ip')}"
            status = data.get('status')
            if status: 
                self.status_bar.setText(f"{T('status_req_from')}: {client} | {T('status_path')}: {path} | {T('status_status')}: {status}")
            return

        # Determine status based on result being exactly "OK"
        is_ok = False
        try:
            msg_data = resp.get('message', {})
            result = msg_data.get('result', 'FAIL')
            is_ok = (result == 'OK')
        except Exception as e:
            # print(f"DEBUG: Error in check: {e}")
            is_ok = False

        # Set traffic light based on OK status
        self.traffic_light.set_state(is_ok)
        
        client = f"{data.get('client_ip')}"
        self.status_bar.setText(f"{T('status_req_from')}: {client} | {T('status_path')}: {path} | {T('status_status')}: {data.get('status')}")
        
        try:
            timestamp = resp.get('timestamp', '')
            if timestamp:
                # Format ISO timestamp to readable format if possible
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            else:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
            self.time_label.setText(timestamp)
        
            msg = resp.get('message', {})
            val = msg.get('value')
            txt = msg.get('msg', T('msg_data_received'))
            plate = msg.get('plate', T('lbl_no_plate'))
            
            # Check ANPR enabled status dynamically
            config = ConfigManager.load_config()
            anpr_enabled = config.get('anpr', {}).get('enabled', False)
            self.plate_label.setVisible(anpr_enabled)
            
            if val is not None:
                self.value_label.setText(f"{float(val):.2f}")
            else:
                self.value_label.setText(T("lbl_error_short"))
            
            self.plate_label.setText(str(plate))    
            self.msg_label.setText(str(txt)[:30])
        except Exception as e:
            print(f"Error updating UI: {e}")

    def reset_state(self):
        self.traffic_light.set_state(False)
        self.status_bar.setText(T("status_idle_waiting"))
        self.reset_timer.stop()

    def toggle_test_mode(self, checked):
        opscalesrv.TEST_MODE = checked
        if checked:
            self.status_bar.setText(T("status_test_mode"))
            # Set Very Dark Purple background for test mode
            purple_style = "background-color: #560159;"
            self.setStyleSheet(f"QMainWindow {{ {purple_style} }}")
            if self.centralWidget():
                self.centralWidget().setStyleSheet(f".QWidget {{ {purple_style} }}")
        else:
            self.status_bar.setText(T("status_serial_mode"))
            self.setStyleSheet("")
            if self.centralWidget():
                self.centralWidget().setStyleSheet("")

    def open_serial_settings(self):
        if self.check_password():
            if SerialSettingsDialog(self).exec():
                QMessageBox.information(self, T("title_restart_required"), T("msg_restart_required"))

    def open_hosts_settings(self):
        if self.check_password():
            if AllowedHostsDialog(self).exec():
                # Allowed hosts might update live if I reload config in server loop, but server loads only once.
                QMessageBox.information(self, T("title_restart_required"), T("msg_restart_required"))

    def open_general_settings(self):
        if self.check_password():
            if GeneralSettingsDialog(self).exec():
                QMessageBox.information(self, T("title_restart_required"), T("msg_restart_required"))

    def open_anpr_settings(self):
        if self.check_password():
            if ANPRSettingsDialog(self).exec():
                QMessageBox.information(self, T("title_restart_required"), T("msg_restart_required"))

    def show_logs(self):
        LogViewerDialog(self).exec()

    def clear_logs(self):
        if self.check_password():
            config = ConfigManager.load_config()
            log_file = config.get('settings', {}).get('log_file', 'requests.log')
            
            try:
                # Open with 'w' to truncate
                with open(log_file, 'w', encoding='utf-8') as f:
                    pass
                QMessageBox.information(self, "Success", T("msg_logs_cleared", "Logs cleared."))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to clear logs: {e}")

    def check_password(self):
        config = ConfigManager.load_config()
        stored_hash = config.get('settings', {}).get('password')
        
        if not stored_hash:
            return True
            
        dlg = CheckPasswordDialog(self)
        if dlg.exec():
            pwd = dlg.get_password()
            pwd_hash = hashlib.sha256(pwd.encode('utf-8')).hexdigest()
            if pwd_hash == stored_hash:
                return True
            else:
                QMessageBox.warning(self, T("msg_access_denied"), T("msg_incorrect_pwd"))
                return False
        return False

    def show_about(self):
        text = """
        <h2 style='color: #BB86FC'>Opriori Scale Server</h2>
        <p><b>ANPR supported</b></p>
        <p>Version 1.0.36</p>
        <br>
        <p>Altay Kireççi (c)(p) 12192025</p>
        <p><a href='http://www.opriori.com.tr' style='color: #03DAC6'>www.opriori.com.tr</a></p>
        """
        QMessageBox.about(self, T("act_about"), text)

    def reset_settings(self):
        """Reset all settings to default values"""
        if not self.check_password():
            return
        
        # Confirm reset
        reply = QMessageBox.question(
            self, 
            T("title_reset_settings", "Reset Settings"),
            T("msg_confirm_reset", "Are you sure you want to reset all settings to default values?\n\nThis will:\n- Reset all configuration to defaults\n- Remove password protection\n- Require server restart\n\nThis action cannot be undone."),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                ConfigManager.reset_to_default()
                QMessageBox.information(
                    self, 
                    T("msg_success", "Success"),
                    T("msg_settings_reset", "Settings have been reset to default values.\n\nPlease restart the server for changes to take effect.")
                )
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    T("msg_error", "Error"),
                    f"{T('msg_reset_failed', 'Failed to reset settings')}: {e}"
                )

    def open_set_password(self):
        config = ConfigManager.load_config()
        stored_hash = config.get('settings', {}).get('password')
        
        dlg = SetPasswordDialog(has_current_password=bool(stored_hash), parent=self)
        if dlg.exec():
            current, new = dlg.get_data()
            
            if stored_hash:
                current_hash = hashlib.sha256(current.encode('utf-8')).hexdigest()
                if current_hash != stored_hash:
                    QMessageBox.warning(self, T("msg_error"), T("msg_incorrect_pwd"))
                    return
            
            # Save new password
            settings = config.get('settings', {})
            if new:
                settings['password'] = hashlib.sha256(new.encode('utf-8')).hexdigest()
                QMessageBox.information(self, T("msg_success"), T("msg_pwd_set"))
            else:
                # If existing password and new is empty, remove password protection?? 
                # Or just treat empty as no password? Let's assume empty means remove.
                if 'password' in settings:
                    del settings['password']
                QMessageBox.information(self, T("msg_success"), T("msg_pwd_removed"))
            
            config['settings'] = settings
            ConfigManager.save_config(config)

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
