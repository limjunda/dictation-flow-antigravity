"""Smart text processor with voice commands and number conversion."""
import re
from typing import Dict, List, Tuple
from .basic import BasicProcessor


class SmartProcessor(BasicProcessor):
    """Smart processing: voice commands, numbers, dates."""
    
    # Voice commands for punctuation and formatting
    VOICE_COMMANDS: Dict[str, str] = {
        "new line": "\n",
        "newline": "\n",
        "new paragraph": "\n\n",
        "comma": ",",
        "period": ".",
        "full stop": ".",
        "question mark": "?",
        "exclamation mark": "!",
        "exclamation point": "!",
        "colon": ":",
        "semicolon": ";",
        "open quote": '"',
        "close quote": '"',
        "open bracket": "(",
        "close bracket": ")",
        "open brace": "{",
        "close brace": "}",
    }
    
    # Number words to digits
    NUMBER_WORDS: Dict[str, int] = {
        "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
        "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
        "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
        "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90, "hundred": 100, "thousand": 1000,
    }
    
    @property
    def name(self) -> str:
        return "smart"
    
    def process(self, text: str) -> str:
        """Apply smart formatting to text."""
        if not text or not text.strip():
            return ""
        
        text = text.strip()
        
        # Apply voice commands first
        text = self._apply_voice_commands(text)
        
        # Convert number words to digits
        text = self._convert_numbers(text)
        
        # Apply basic processing (capitalization, punctuation)
        # But skip adding period if we have newlines
        text = self._smart_capitalize(text)
        
        # Add final punctuation only if needed
        if text and text[-1] not in self.SENTENCE_ENDINGS and text[-1] != "\n":
            text += "."
        
        return text
    
    def _apply_voice_commands(self, text: str) -> str:
        """Replace voice commands with their symbols."""
        # Sort by length (longest first) to avoid partial matches
        commands = sorted(self.VOICE_COMMANDS.keys(), key=len, reverse=True)
        
        for command in commands:
            pattern = re.compile(re.escape(command), re.IGNORECASE)
            text = pattern.sub(self.VOICE_COMMANDS[command], text)
        
        return text
    
    def _convert_numbers(self, text: str) -> str:
        """Convert number words to digits."""
        # Process line by line to preserve newlines
        lines = text.split("\n")
        converted_lines = []
        
        for line in lines:
            words = line.split()
            result = []
            i = 0
            
            while i < len(words):
                word_lower = words[i].lower()
                
                # Check for compound numbers like "twenty three"
                if word_lower in self.NUMBER_WORDS:
                    num = self.NUMBER_WORDS[word_lower]
                    
                    # Look ahead for compound
                    if i + 1 < len(words):
                        next_lower = words[i + 1].lower()
                        if next_lower in self.NUMBER_WORDS:
                            next_num = self.NUMBER_WORDS[next_lower]
                            if num >= 20 and next_num < 10:
                                num += next_num
                                i += 1
                    
                    result.append(str(num))
                else:
                    result.append(words[i])
                
                i += 1
            
            converted_lines.append(" ".join(result))
        
        return "\n".join(converted_lines)
    
    def _smart_capitalize(self, text: str) -> str:
        """Capitalize considering newlines as sentence breaks."""
        if not text:
            return text
        
        # Split by newlines, capitalize each part
        lines = text.split("\n")
        capitalized_lines = []
        
        for line in lines:
            if line:
                line = line.strip()
                if line and line[0].islower():
                    line = line[0].upper() + line[1:]
                line = self._capitalize_sentences(line)
            capitalized_lines.append(line)
        
        return "\n".join(capitalized_lines)
