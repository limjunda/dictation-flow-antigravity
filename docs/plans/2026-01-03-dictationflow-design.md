# DictationFlow - Personal Speech-to-Text Application

A Windows desktop application that converts speech to text and types it wherever your cursor is pointing.

## Overview

DictationFlow is a personal dictation tool that captures your voice, transcribes it using configurable speech recognition engines, processes the text for proper formatting, and injects it at your current cursor position.

**Key Features:**
- **Hybrid Speech Recognition**: Google Cloud (primary) with local fallbacks (Whisper, Faster-Whisper, Vosk)
- **3 Text Processing Modes**: Basic, Smart, Context-Aware (toggleable)
- **Customizable Global Hotkey**: Toggle recording from anywhere
- **Minimal UI**: System tray icon + optional floating widget

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DictationFlow App                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Hotkey    │  │   Audio     │  │    System Tray      │  │
│  │   Manager   │  │   Capture   │  │    + Float Widget   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  Core Controller                      │   │
│  │         (Orchestrates all components)                 │   │
│  └──────────────────────────────────────────────────────┘   │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Speech    │  │    Text     │  │      Text           │  │
│  │   Engine    │  │  Processor  │  │      Injector       │  │
│  │  (Pluggable)│  │ (3 modes)   │  │  (Cursor Position)  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Proposed Changes

### Core Module

#### [NEW] [main.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/main.py)
- Application entry point
- Initialize PyQt6 application and event loop
- Load configuration and instantiate controller

#### [NEW] [controller.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/controller.py)
- Core orchestrator connecting all components
- Manages recording state (idle → recording → processing)
- Coordinates audio → speech → processing → injection pipeline

---

### Audio Capture

#### [NEW] [audio/capture.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/audio/capture.py)
- Records microphone input using `sounddevice`
- Configurable sample rate (16kHz for most models)
- Provides audio data as numpy arrays or WAV bytes

---

### Speech Engines (Pluggable)

#### [NEW] [speech/base.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/speech/base.py)
- Abstract `SpeechEngine` base class
- Methods: `transcribe(audio)`, `is_available()`, `get_name()`

#### [NEW] [speech/google_cloud.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/speech/google_cloud.py)
- Google Cloud Speech-to-Text implementation
- Uses `google-cloud-speech` SDK
- Tracks quota usage for auto-fallback

#### [NEW] [speech/whisper_engine.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/speech/whisper_engine.py)
- OpenAI Whisper implementation
- Configurable model size (tiny, base, small)

#### [NEW] [speech/faster_whisper.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/speech/faster_whisper.py)
- Faster-Whisper (CTranslate2) implementation
- 4x faster than standard Whisper, recommended local fallback

#### [NEW] [speech/vosk_engine.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/speech/vosk_engine.py)
- Vosk implementation
- Lightweight, real-time capable

**Model Comparison:**

| Model | Speed | Accuracy | Size | Offline |
|-------|-------|----------|------|---------|
| Google Cloud | ⚡ Fast | ⭐⭐⭐⭐⭐ | N/A | ❌ |
| Faster-Whisper | ⚡ Fast | ⭐⭐⭐⭐ | ~150MB | ✅ |
| Whisper (base) | Medium | ⭐⭐⭐⭐ | 142MB | ✅ |
| Vosk | ⚡⚡ Fastest | ⭐⭐⭐ | 50MB | ✅ |

---

### Text Processing (3 Modes)

#### [NEW] [processing/base.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/processing/base.py)
- Abstract `TextProcessor` base class

#### [NEW] [processing/basic.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/processing/basic.py)
- Rule-based processing: capitalization, periods, commas
- ~10ms latency

#### [NEW] [processing/smart.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/processing/smart.py)
- Regex patterns for numbers, dates, times
- Voice commands: "new line", "new paragraph"
- ~50ms latency

#### [NEW] [processing/context_aware.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/processing/context_aware.py)
- LLM-enhanced processing (Gemini Flash or Ollama)
- Grammar correction, sentence smoothing
- ~200-500ms latency

---

### Text Injection

#### [NEW] [injection/injector.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/injection/injector.py)
- Hybrid approach:
  - Short text (<20 chars): Keystroke simulation
  - Longer text: Clipboard paste with save/restore
- Uses `pynput` for keyboard simulation
- Uses `pyperclip` for clipboard operations

---

### Hotkey Manager

#### [NEW] [hotkey/manager.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/hotkey/manager.py)
- Global hotkey capture using `pynput`
- Customizable key combination
- Toggle behavior (start/stop recording)

---

### User Interface

#### [NEW] [ui/tray.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/ui/tray.py)
- System tray icon with context menu
- Visual states: idle (gray), recording (red pulse), processing (yellow)
- Quick access to engine/mode switching

#### [NEW] [ui/widget.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/ui/widget.py)
- Floating recording widget
- Live transcription preview
- Audio waveform visualization
- Draggable, position memory

#### [NEW] [ui/settings.py](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/src/ui/settings.py)
- Settings dialog window
- Hotkey configuration
- Engine selection with fallback
- Processing mode selection
- API key management

---

### Configuration

#### [NEW] [config/default.yaml](file:///c:/Users/admin/github_repo/dictation-flow-antigravity/config/default.yaml)
```yaml
hotkey:
  modifiers: ["ctrl", "shift"]
  key: "d"

speech:
  primary_engine: "google_cloud"
  fallback_engine: "faster_whisper"
  auto_fallback: true

processing:
  mode: "smart"  # basic, smart, context_aware

ui:
  show_widget: true
  play_sounds: true

injection:
  method: "auto"  # auto, keystroke, clipboard
```

---

## Project Structure

```
dictation-flow-antigravity/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── controller.py
│   ├── audio/
│   │   ├── __init__.py
│   │   └── capture.py
│   ├── speech/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── google_cloud.py
│   │   ├── whisper_engine.py
│   │   ├── faster_whisper.py
│   │   └── vosk_engine.py
│   ├── processing/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── basic.py
│   │   ├── smart.py
│   │   └── context_aware.py
│   ├── injection/
│   │   ├── __init__.py
│   │   └── injector.py
│   ├── hotkey/
│   │   ├── __init__.py
│   │   └── manager.py
│   └── ui/
│       ├── __init__.py
│       ├── tray.py
│       ├── widget.py
│       └── settings.py
├── config/
│   ├── default.yaml
│   └── user.yaml
├── assets/
│   ├── icons/
│   └── sounds/
├── tests/
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Dependencies

```
# Core
PyQt6>=6.5.0
pynput>=1.7.6
sounddevice>=0.4.6
numpy>=1.24.0

# Speech Engines
google-cloud-speech>=2.21.0
openai-whisper>=20231117
faster-whisper>=0.10.0
vosk>=0.3.45

# Text Processing
google-generativeai>=0.3.0

# Utilities
pyperclip>=1.8.2
pyyaml>=6.0
```

---

## Verification Plan

### Automated Tests
- Unit tests for each speech engine (mock audio input)
- Unit tests for each text processor mode
- Integration test for controller pipeline

### Manual Verification
1. **Run application**: `python -m src.main`
2. **Test hotkey**: Press configured hotkey, verify recording starts
3. **Test dictation**: Speak, verify text appears at cursor
4. **Test mode switching**: Toggle between processing modes
5. **Test engine switching**: Try each speech engine
6. **Test fallback**: Disable internet, verify local engine activates

---

## Implementation Phases

### Phase 1: Core Foundation
- Project setup, dependencies
- Audio capture
- Basic text injector
- Hotkey manager

### Phase 2: Speech Engines
- Google Cloud integration
- Faster-Whisper integration
- Engine switching logic

### Phase 3: Text Processing
- Basic mode
- Smart mode with voice commands
- Context-aware mode (optional)

### Phase 4: UI Polish
- System tray with all features
- Floating widget
- Settings dialog

### Phase 5: Additional Engines (Optional)
- Whisper (standard)
- Vosk
