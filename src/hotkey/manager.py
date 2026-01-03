"""Global hotkey manager using pynput."""
from typing import Callable, Optional, Set
from pynput import keyboard
import threading


class HotkeyManager:
    """Manages global hotkey detection."""
    
    # Map string names to pynput keys
    MODIFIER_MAP = {
        "ctrl": keyboard.Key.ctrl_l,
        "shift": keyboard.Key.shift_l,
        "alt": keyboard.Key.alt_l,
        "cmd": keyboard.Key.cmd,
        "win": keyboard.Key.cmd,
    }
    
    def __init__(
        self,
        modifiers: list[str],
        key: str,
        on_trigger: Optional[Callable[[], None]] = None
    ):
        self.modifiers: Set[str] = set(m.lower() for m in modifiers)
        self.key = key.lower()
        self.on_trigger = on_trigger
        
        self._pressed_modifiers: Set[str] = set()
        self._listener: Optional[keyboard.Listener] = None
        self._is_listening = False
        self._lock = threading.Lock()
    
    @property
    def is_listening(self) -> bool:
        """Check if hotkey listener is active."""
        return self._is_listening
    
    def _on_press(self, key) -> None:
        """Handle key press events."""
        # Check if it's a modifier
        for name, mod_key in self.MODIFIER_MAP.items():
            if key == mod_key and name in self.modifiers:
                self._pressed_modifiers.add(name)
                return
        
        # Check if it's the trigger key with all modifiers pressed
        try:
            key_char = key.char.lower() if hasattr(key, 'char') and key.char else None
        except AttributeError:
            key_char = None
        
        if key_char == self.key:
            if self._pressed_modifiers >= self.modifiers:
                if self.on_trigger:
                    # Call in separate thread to avoid blocking listener
                    threading.Thread(target=self.on_trigger, daemon=True).start()
    
    def _on_release(self, key) -> None:
        """Handle key release events."""
        for name, mod_key in self.MODIFIER_MAP.items():
            if key == mod_key:
                self._pressed_modifiers.discard(name)
    
    def start(self) -> None:
        """Start listening for hotkey."""
        if self._is_listening:
            return
        
        with self._lock:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            self._is_listening = True
    
    def stop(self) -> None:
        """Stop listening for hotkey."""
        if not self._is_listening:
            return
        
        with self._lock:
            if self._listener:
                self._listener.stop()
                self._listener = None
            self._is_listening = False
    
    def update_hotkey(self, modifiers: list[str], key: str) -> None:
        """Update the hotkey combination."""
        was_listening = self._is_listening
        if was_listening:
            self.stop()
        
        self.modifiers = set(m.lower() for m in modifiers)
        self.key = key.lower()
        
        if was_listening:
            self.start()
