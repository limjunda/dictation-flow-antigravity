"""Settings dialog for DictationFlow configuration."""
from typing import Optional, Callable
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QPushButton, QCheckBox,
    QGroupBox, QLineEdit, QKeySequenceEdit, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeySequence


class SettingsDialog(QDialog):
    """Settings dialog for configuring DictationFlow."""
    
    # Signals
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, current_settings: dict, parent=None):
        super().__init__(parent)
        self._settings = current_settings.copy()
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self) -> None:
        """Set up the dialog UI."""
        self.setWindowTitle("DictationFlow Settings")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Hotkey settings
        hotkey_group = QGroupBox("Hotkey")
        hotkey_layout = QFormLayout(hotkey_group)
        
        self._hotkey_edit = QKeySequenceEdit()
        self._hotkey_edit.setToolTip("Press your desired key combination")
        hotkey_layout.addRow("Toggle Recording:", self._hotkey_edit)
        
        layout.addWidget(hotkey_group)
        
        # Speech engine settings
        engine_group = QGroupBox("Speech Recognition")
        engine_layout = QFormLayout(engine_group)
        
        self._engine_combo = QComboBox()
        self._engine_combo.addItems(["vosk", "faster_whisper", "google_cloud"])
        self._engine_combo.currentTextChanged.connect(self._on_engine_changed)
        engine_layout.addRow("Engine:", self._engine_combo)
        
        self._model_combo = QComboBox()
        engine_layout.addRow("Model:", self._model_combo)
        
        # API Key input (for cloud engines)
        self._api_key_label = QLabel("API Key:")
        self._api_key_edit = QLineEdit()
        self._api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._api_key_edit.setPlaceholderText("Paste your Google Cloud API key or credentials path")
        engine_layout.addRow(self._api_key_label, self._api_key_edit)
        
        # Initially hide API key field
        self._api_key_label.hide()
        self._api_key_edit.hide()
        
        layout.addWidget(engine_group)
        
        # Text processing settings
        processing_group = QGroupBox("Text Processing")
        processing_layout = QFormLayout(processing_group)
        
        self._processor_combo = QComboBox()
        self._processor_combo.addItems(["basic", "smart", "context_aware"])
        processing_layout.addRow("Mode:", self._processor_combo)
        
        layout.addWidget(processing_group)
        
        # UI settings
        ui_group = QGroupBox("Interface")
        ui_layout = QFormLayout(ui_group)
        
        self._show_widget_check = QCheckBox("Show floating widget")
        ui_layout.addRow(self._show_widget_check)
        
        self._auto_show_check = QCheckBox("Auto-show widget when recording")
        ui_layout.addRow(self._auto_show_check)
        
        self._notifications_check = QCheckBox("Show notifications")
        ui_layout.addRow(self._notifications_check)
        
        layout.addWidget(ui_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        # Apply styling
        self._apply_style()
    
    def _apply_style(self) -> None:
        """Apply dark theme styling."""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 4px;
                color: #4CAF50;
            }
            QLabel {
                color: #cccccc;
            }
            QComboBox, QLineEdit, QKeySequenceEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: #ffffff;
                min-height: 24px;
            }
            QComboBox:hover, QLineEdit:hover, QKeySequenceEdit:hover {
                border-color: #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QCheckBox {
                color: #cccccc;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #555;
                background-color: #3d3d3d;
            }
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                color: #ffffff;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #666;
            }
            QPushButton:default {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            QPushButton:default:hover {
                background-color: #45a049;
            }
        """)
    
    def _on_engine_changed(self, engine: str) -> None:
        """Update model options when engine changes."""
        self._model_combo.clear()
        
        if engine == "vosk":
            self._model_combo.addItems(["en-us (default)", "en-us-small"])
            self._api_key_label.hide()
            self._api_key_edit.hide()
        elif engine == "faster_whisper":
            self._model_combo.addItems(["tiny", "base", "small", "medium"])
            self._api_key_label.hide()
            self._api_key_edit.hide()
        elif engine == "google_cloud":
            self._model_combo.addItems(["default"])
            self._api_key_label.show()
            self._api_key_edit.show()
    
    def _load_settings(self) -> None:
        """Load current settings into UI."""
        # Hotkey
        modifiers = self._settings.get("hotkey_modifiers", ["ctrl", "shift"])
        key = self._settings.get("hotkey_key", "d")
        hotkey_str = "+".join(modifiers + [key])
        self._hotkey_edit.setKeySequence(QKeySequence(hotkey_str.replace("ctrl", "Ctrl").replace("shift", "Shift")))
        
        # Engine
        engine = self._settings.get("engine", "vosk")
        idx = self._engine_combo.findText(engine)
        if idx >= 0:
            self._engine_combo.setCurrentIndex(idx)
        self._on_engine_changed(engine)
        
        # Processor
        processor = self._settings.get("processor", "smart")
        idx = self._processor_combo.findText(processor)
        if idx >= 0:
            self._processor_combo.setCurrentIndex(idx)
        
        # UI options
        self._show_widget_check.setChecked(self._settings.get("show_widget", True))
        self._auto_show_check.setChecked(self._settings.get("auto_show_widget", True))
        self._notifications_check.setChecked(self._settings.get("show_notifications", True))
        
        # API key
        self._api_key_edit.setText(self._settings.get("google_cloud_credentials", ""))
    
    def _save_settings(self) -> None:
        """Save settings and close dialog."""
        # Parse hotkey
        key_seq = self._hotkey_edit.keySequence()
        key_str = key_seq.toString().lower()
        parts = key_str.split("+")
        
        modifiers = [p for p in parts[:-1] if p]
        key = parts[-1] if parts else "d"
        
        new_settings = {
            "hotkey_modifiers": modifiers,
            "hotkey_key": key,
            "engine": self._engine_combo.currentText(),
            "model": self._model_combo.currentText(),
            "processor": self._processor_combo.currentText(),
            "show_widget": self._show_widget_check.isChecked(),
            "auto_show_widget": self._auto_show_check.isChecked(),
            "show_notifications": self._notifications_check.isChecked(),
            "google_cloud_credentials": self._api_key_edit.text(),
        }
        
        self._settings.update(new_settings)
        self.settings_changed.emit(self._settings)
        self.accept()
    
    def get_settings(self) -> dict:
        """Get current settings."""
        return self._settings.copy()
