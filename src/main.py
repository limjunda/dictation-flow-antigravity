"""DictationFlow application entry point."""
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from .controller import DictationController, State
from .hotkey.manager import HotkeyManager
from .processing.smart import SmartProcessor
from .ui.tray import SystemTray


class DictationApp:
    """Main application class."""
    
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)
        self._app.setApplicationName("DictationFlow")
        
        # Initialize components
        self._init_controller()
        self._init_hotkey()
        self._init_ui()
    
    def _init_controller(self) -> None:
        """Initialize the dictation controller."""
        # Start without speech engine - will add when user configures
        self._controller = DictationController(
            speech_engine=None,
            text_processor=SmartProcessor(),
            on_state_change=self._on_state_change,
            on_transcription=self._on_transcription
        )
    
    def _init_hotkey(self) -> None:
        """Initialize global hotkey."""
        self._hotkey = HotkeyManager(
            modifiers=["ctrl", "shift"],
            key="d",
            on_trigger=self._controller.toggle
        )
        self._hotkey.start()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        self._tray = SystemTray()
        self._tray.toggle_requested.connect(self._controller.toggle)
        self._tray.quit_requested.connect(self._quit)
        self._tray.show()
    
    def _on_state_change(self, state: State) -> None:
        """Handle controller state changes."""
        if state == State.IDLE:
            self._tray.set_state_idle()
        elif state == State.RECORDING:
            self._tray.set_state_recording()
        elif state == State.PROCESSING:
            self._tray.set_state_processing()
    
    def _on_transcription(self, text: str) -> None:
        """Handle completed transcription."""
        self._tray.show_message("Dictation", text[:100])
    
    def _quit(self) -> None:
        """Quit the application."""
        self._hotkey.stop()
        self._tray.hide()
        self._app.quit()
    
    def run(self) -> int:
        """Run the application."""
        return self._app.exec()


def main() -> int:
    """Application entry point."""
    app = DictationApp()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
