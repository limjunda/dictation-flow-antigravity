"""System tray icon and menu."""
from typing import Callable, Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class SystemTray(QObject):
    """System tray icon with context menu."""
    
    # Signals
    toggle_requested = pyqtSignal()
    quit_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._tray = QSystemTrayIcon(self)
        self._menu = QMenu()
        self._setup_menu()
        self._tray.setContextMenu(self._menu)
        
        # Set default icon (will be replaced with actual icons)
        self._set_idle_icon()
        
        self._tray.setToolTip("DictationFlow - Ready")
    
    def _setup_menu(self) -> None:
        """Set up the context menu."""
        # Toggle action
        self._toggle_action = QAction("Start Recording", self._menu)
        self._toggle_action.triggered.connect(self.toggle_requested.emit)
        self._menu.addAction(self._toggle_action)
        
        self._menu.addSeparator()
        
        # Settings action
        settings_action = QAction("Settings...", self._menu)
        settings_action.triggered.connect(self.settings_requested.emit)
        self._menu.addAction(settings_action)
        
        self._menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self._menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        self._menu.addAction(quit_action)
    
    def _set_idle_icon(self) -> None:
        """Set icon for idle state."""
        # Using default application icon for now
        # TODO: Replace with custom icons
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_MediaPlay
            ))
    
    def _set_recording_icon(self) -> None:
        """Set icon for recording state."""
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_MediaStop
            ))
    
    def _set_processing_icon(self) -> None:
        """Set icon for processing state."""
        app = QApplication.instance()
        if app:
            self._tray.setIcon(app.style().standardIcon(
                app.style().StandardPixmap.SP_BrowserReload
            ))
    
    def set_state_idle(self) -> None:
        """Update UI for idle state."""
        self._set_idle_icon()
        self._toggle_action.setText("Start Recording")
        self._tray.setToolTip("DictationFlow - Ready")
    
    def set_state_recording(self) -> None:
        """Update UI for recording state."""
        self._set_recording_icon()
        self._toggle_action.setText("Stop Recording")
        self._tray.setToolTip("DictationFlow - Recording...")
    
    def set_state_processing(self) -> None:
        """Update UI for processing state."""
        self._set_processing_icon()
        self._toggle_action.setText("Processing...")
        self._tray.setToolTip("DictationFlow - Processing...")
    
    def show(self) -> None:
        """Show the tray icon."""
        self._tray.show()
    
    def hide(self) -> None:
        """Hide the tray icon."""
        self._tray.hide()
    
    def show_message(self, title: str, message: str) -> None:
        """Show a notification message."""
        self._tray.showMessage(title, message)
