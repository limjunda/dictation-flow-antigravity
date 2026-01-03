"""Floating widget for live transcription preview."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QSizeGrip
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen, QLinearGradient


class AudioLevelBar(QWidget):
    """Simple audio level visualization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._level = 0.0
        self.setMinimumHeight(8)
        self.setMaximumHeight(8)
    
    def set_level(self, level: float) -> None:
        """Set audio level (0.0 to 1.0)."""
        self._level = max(0.0, min(1.0, level))
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(40, 40, 40))
        
        # Level bar with gradient
        if self._level > 0:
            width = int(self.width() * self._level)
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(76, 175, 80))  # Green
            gradient.setColorAt(0.7, QColor(255, 193, 7))  # Yellow
            gradient.setColorAt(1.0, QColor(244, 67, 54))  # Red
            
            painter.fillRect(0, 0, width, self.height(), gradient)


class FloatingWidget(QWidget):
    """Floating widget showing recording status and live transcription."""
    
    # Signals
    close_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_position = QPoint()
        self._is_recording = False
        
        self._setup_ui()
        self._setup_style()
        
        # Animation timer for recording pulse
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse_animation)
        self._pulse_opacity = 1.0
        self._pulse_direction = -1
    
    def _setup_ui(self) -> None:
        """Set up the widget UI."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Main container
        self._container = QFrame(self)
        container_layout = QVBoxLayout(self._container)
        container_layout.setContentsMargins(12, 8, 12, 8)
        container_layout.setSpacing(8)
        
        # Header with status and close button
        header = QHBoxLayout()
        header.setSpacing(8)
        
        self._status_indicator = QLabel("●")
        self._status_indicator.setObjectName("statusIndicator")
        header.addWidget(self._status_indicator)
        
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("statusLabel")
        header.addWidget(self._status_label)
        
        header.addStretch()
        
        # Minimize button
        self._minimize_btn = QPushButton("—")
        self._minimize_btn.setObjectName("controlBtn")
        self._minimize_btn.setFixedSize(20, 20)
        self._minimize_btn.clicked.connect(self._toggle_minimize)
        header.addWidget(self._minimize_btn)
        
        # Close button
        close_btn = QPushButton("×")
        close_btn.setObjectName("controlBtn")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.close_requested.emit)
        header.addWidget(close_btn)
        
        container_layout.addLayout(header)
        
        # Audio level bar
        self._audio_bar = AudioLevelBar()
        container_layout.addWidget(self._audio_bar)
        
        # Transcription preview
        self._preview_label = QLabel("")
        self._preview_label.setObjectName("previewLabel")
        self._preview_label.setWordWrap(True)
        self._preview_label.setMinimumHeight(40)
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        container_layout.addWidget(self._preview_label)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)
        
        self.setMinimumSize(280, 100)
        self.resize(320, 120)
        
        self._is_minimized = False
    
    def _setup_style(self) -> None:
        """Apply styling."""
        self._container.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 0.95);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
            
            #statusIndicator {
                color: #4CAF50;
                font-size: 14px;
            }
            
            #statusLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
            }
            
            #previewLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 12px;
                padding: 4px;
            }
            
            #controlBtn {
                background-color: transparent;
                border: none;
                color: rgba(255, 255, 255, 0.6);
                font-size: 16px;
                font-weight: bold;
            }
            
            #controlBtn:hover {
                color: #ffffff;
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 4px;
            }
        """)
    
    def _toggle_minimize(self) -> None:
        """Toggle minimized state."""
        self._is_minimized = not self._is_minimized
        self._preview_label.setVisible(not self._is_minimized)
        self._audio_bar.setVisible(not self._is_minimized)
        
        if self._is_minimized:
            self.resize(200, 40)
            self._minimize_btn.setText("+")
        else:
            self.resize(320, 120)
            self._minimize_btn.setText("—")
    
    def set_state_idle(self) -> None:
        """Set idle state."""
        self._is_recording = False
        self._pulse_timer.stop()
        self._status_indicator.setStyleSheet("color: #4CAF50;")
        self._status_indicator.setText("●")
        self._status_label.setText("Ready")
        self._preview_label.setText("")
        self._audio_bar.set_level(0)
    
    def set_state_recording(self) -> None:
        """Set recording state."""
        self._is_recording = True
        self._pulse_timer.start(50)
        self._status_indicator.setStyleSheet("color: #f44336;")
        self._status_indicator.setText("●")
        self._status_label.setText("Recording...")
    
    def set_state_processing(self) -> None:
        """Set processing state."""
        self._is_recording = False
        self._pulse_timer.stop()
        self._status_indicator.setStyleSheet("color: #FFC107;")
        self._status_indicator.setText("◐")
        self._status_label.setText("Processing...")
    
    def set_preview_text(self, text: str) -> None:
        """Set the transcription preview text."""
        # Truncate if too long
        if len(text) > 200:
            text = "..." + text[-197:]
        self._preview_label.setText(text)
    
    def set_audio_level(self, level: float) -> None:
        """Set audio level for visualization."""
        self._audio_bar.set_level(level)
    
    def _pulse_animation(self) -> None:
        """Animate the recording indicator."""
        self._pulse_opacity += self._pulse_direction * 0.05
        if self._pulse_opacity <= 0.3:
            self._pulse_direction = 1
        elif self._pulse_opacity >= 1.0:
            self._pulse_direction = -1
        
        opacity = int(self._pulse_opacity * 255)
        self._status_indicator.setStyleSheet(
            f"color: rgba(244, 67, 54, {opacity});"
        )
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
