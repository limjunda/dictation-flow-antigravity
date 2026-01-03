"""Hybrid text injection - keystroke or clipboard based on text length."""
from enum import Enum
from typing import Optional
import time
import pyperclip
from pynput.keyboard import Controller, Key


class InjectionMethod(Enum):
    """Text injection method."""
    AUTO = "auto"
    KEYSTROKE = "keystroke"
    CLIPBOARD = "clipboard"


class TextInjector:
    """Injects text at current cursor position."""
    
    def __init__(
        self,
        method: InjectionMethod = InjectionMethod.AUTO,
        short_text_threshold: int = 20,
        keystroke_delay: float = 0.01
    ):
        self.method = method
        self.short_text_threshold = short_text_threshold
        self.keystroke_delay = keystroke_delay
        self._keyboard = Controller()
    
    def _choose_method(self, text: str) -> InjectionMethod:
        """Choose injection method based on text length."""
        if self.method != InjectionMethod.AUTO:
            return self.method
        
        if len(text) <= self.short_text_threshold:
            return InjectionMethod.KEYSTROKE
        return InjectionMethod.CLIPBOARD
    
    def _inject_keystroke(self, text: str) -> None:
        """Inject text via simulated keystrokes."""
        for char in text:
            self._keyboard.type(char)
            if self.keystroke_delay > 0:
                time.sleep(self.keystroke_delay)
    
    def _inject_clipboard(self, text: str) -> None:
        """Inject text via clipboard paste."""
        # Save current clipboard
        try:
            original_clipboard = pyperclip.paste()
        except Exception:
            original_clipboard = None
        
        try:
            # Copy text to clipboard
            pyperclip.copy(text)
            time.sleep(0.05)  # Small delay for clipboard
            
            # Simulate Ctrl+V
            self._keyboard.press(Key.ctrl)
            self._keyboard.tap('v')
            self._keyboard.release(Key.ctrl)
            
            time.sleep(0.1)  # Wait for paste to complete
        finally:
            # Restore original clipboard
            if original_clipboard is not None:
                try:
                    pyperclip.copy(original_clipboard)
                except Exception:
                    pass
    
    def inject(self, text: str) -> bool:
        """Inject text at current cursor position.
        
        Returns True if successful, False otherwise.
        """
        if not text:
            return False
        
        method = self._choose_method(text)
        
        try:
            if method == InjectionMethod.KEYSTROKE:
                self._inject_keystroke(text)
            else:
                self._inject_clipboard(text)
            return True
        except Exception as e:
            print(f"Injection failed: {e}")
            return False
