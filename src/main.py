"""DictationFlow application entry point."""
import sys
from typing import Optional
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread

from .controller import DictationController, State
from .hotkey.manager import HotkeyManager
from .processing.smart import SmartProcessor
from .processing.basic import BasicProcessor
from .config import Config
from .ui.tray import SystemTray
from .ui.widget import FloatingWidget
from .ui.settings import SettingsDialog


class DictationApp:
    """Main application class."""
    
    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)
        self._app.setApplicationName("DictationFlow")
        
        # Load configuration
        self._config = Config()
        
        # Initialize components
        self._init_controller()
        self._init_hotkey()
        self._init_ui()
    
    def _init_controller(self) -> None:
        """Initialize the dictation controller."""
        engine = self._create_speech_engine()
        processor = self._create_text_processor()
        
        self._controller = DictationController(
            speech_engine=engine,
            text_processor=processor,
            on_state_change=self._on_state_change,
            on_transcription=self._on_transcription
        )
    
    def _create_speech_engine(self):
        """Create speech engine based on config."""
        engine_name = self._config.get("engine", "vosk")
        
        # Try configured engine first
        if engine_name == "vosk":
            try:
                from .speech import VoskEngine
                engine = VoskEngine()
                if engine.is_available():
                    print("Using Vosk speech engine")
                    return engine
            except Exception as e:
                print(f"Vosk not available: {e}")
        
        if engine_name == "faster_whisper":
            try:
                from .speech import FasterWhisperEngine
                model = self._config.get("model", "base")
                # Clean model name
                if "(" in model:
                    model = model.split()[0]
                engine = FasterWhisperEngine(model_size=model)
                if engine.is_available():
                    print("Using Faster-Whisper speech engine")
                    return engine
            except Exception as e:
                print(f"Faster-Whisper not available: {e}")
        
        if engine_name == "google_cloud":
            try:
                from .speech import GoogleCloudEngine
                credentials = self._config.get("google_cloud_credentials", "")
                engine = GoogleCloudEngine(credentials_path=credentials if credentials else None)
                if engine.is_available():
                    print("Using Google Cloud Speech engine")
                    return engine
            except Exception as e:
                print(f"Google Cloud Speech not available: {e}")
        
        # Fallback: try any available engine
        try:
            from .speech import VoskEngine
            engine = VoskEngine()
            if engine.is_available():
                print("Falling back to Vosk speech engine")
                return engine
        except Exception:
            pass
        
        print("WARNING: No speech engine available. Install vosk or faster-whisper.")
        return None
    
    def _create_text_processor(self):
        """Create text processor based on config."""
        processor_name = self._config.get("processor", "smart")
        
        if processor_name == "basic":
            return BasicProcessor()
        else:
            return SmartProcessor()
    
    def _init_hotkey(self) -> None:
        """Initialize global hotkey from config."""
        modifiers = self._config.get("hotkey_modifiers", ["ctrl", "shift"])
        key = self._config.get("hotkey_key", "d")
        
        self._hotkey = HotkeyManager(
            modifiers=modifiers,
            key=key,
            on_trigger=self._controller.toggle
        )
        self._hotkey.start()
    
    def _init_ui(self) -> None:
        """Initialize UI components."""
        # System tray
        self._tray = SystemTray()
        self._tray.toggle_requested.connect(self._controller.toggle)
        self._tray.settings_requested.connect(self._show_settings)
        self._tray.quit_requested.connect(self._quit)
        self._tray.show()
        
        # Floating widget
        self._widget = FloatingWidget()
        self._widget.close_requested.connect(self._hide_widget)
        
        # Position widget in bottom-right corner
        screen = self._app.primaryScreen().geometry()
        self._widget.move(screen.width() - 340, screen.height() - 160)
        
        # Show widget based on config
        if self._config.get("show_widget", True):
            self._widget.show()
    
    def _on_state_change(self, state: State) -> None:
        """Handle controller state changes."""
        if state == State.IDLE:
            self._tray.set_state_idle()
            self._widget.set_state_idle()
        elif state == State.RECORDING:
            self._tray.set_state_recording()
            self._widget.set_state_recording()
            # Show widget when recording starts (if auto-show enabled)
            if self._config.get("auto_show_widget", True) and not self._widget.isVisible():
                self._widget.show()
        elif state == State.PROCESSING:
            self._tray.set_state_processing()
            self._widget.set_state_processing()
    
    def _on_transcription(self, text: str) -> None:
        """Handle completed transcription."""
        if self._config.get("show_notifications", True):
            self._tray.show_message("Dictation", text[:100])
        self._widget.set_preview_text(text)
    
    def _show_settings(self) -> None:
        """Show the settings dialog."""
        dialog = SettingsDialog(self._config.to_dict())
        dialog.settings_changed.connect(self._apply_settings)
        dialog.exec()
    
    def _apply_settings(self, settings: dict) -> None:
        """Apply new settings."""
        # Save settings
        self._config.update(settings)
        
        # Update hotkey
        self._hotkey.update_hotkey(
            settings.get("hotkey_modifiers", ["ctrl", "shift"]),
            settings.get("hotkey_key", "d")
        )
        
        # Update speech engine if changed
        if settings.get("engine") != self._config.get("engine"):
            new_engine = self._create_speech_engine()
            self._controller.set_speech_engine(new_engine)
        
        # Update text processor if changed
        new_processor = self._create_text_processor()
        self._controller.set_text_processor(new_processor)
        
        # Update widget visibility
        if settings.get("show_widget"):
            self._widget.show()
        else:
            self._widget.hide()
    
    def _hide_widget(self) -> None:
        """Hide the floating widget."""
        self._widget.hide()
    
    def _toggle_widget(self) -> None:
        """Toggle floating widget visibility."""
        if self._widget.isVisible():
            self._widget.hide()
        else:
            self._widget.show()
    
    def _quit(self) -> None:
        """Quit the application."""
        self._hotkey.stop()
        self._widget.hide()
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
