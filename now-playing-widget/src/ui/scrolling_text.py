"""
Scrolling Text Widget for Now Playing Display
Displays song title and artist with scrolling and animation effects
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QSize, QRect, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QLinearGradient, QPen, QBrush
from PyQt6.QtWidgets import QApplication
import sys


class ScrollingTextWidget(QWidget):
    """Widget displaying scrolling now-playing text with effects"""
    
    text_changed = pyqtSignal(str, str)  # title, artist
    
    def __init__(self, width: int = 800, height: int = 100):
        """
        Initialize scrolling text widget
        
        Args:
            width: Widget width
            height: Widget height
        """
        super().__init__()
        self.width = width
        self.height = height
        self.title = "Now Playing"
        self.artist = "Artist Name"
        self.album = ""
        
        # Animation
        self.scroll_offset = 0
        self.scroll_speed = 2
        self.direction = 1  # 1 for forward, -1 for backward
        self.bounce = False
        
        # Styling
        self.bg_color = QColor("#3B4554")
        self.title_color = QColor("#6FB3D5")
        self.artist_color = QColor("#D5F4E6")
        self.accent_color = QColor("#EEB76B")
        
        # Animation state
        self.animation_enabled = True
        self.text_width = 0
        self.visible_width = self.width - 20
        
        self.setFixedSize(width, height)
        self.init_ui()
        self.start_animation()
    
    def init_ui(self):
        """Initialize UI"""
        # Create animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_scroll)
        
        # Set style
        self.setStyleSheet(f"""
            background-color: {self.bg_color.name()};
            border: 2px solid {self.title_color.name()};
            border-radius: 8px;
        """)
    
    def set_now_playing(self, title: str, artist: str, album: str = ""):
        """
        Update now-playing information
        
        Args:
            title: Song title
            artist: Artist name
            album: Album name (optional)
        """
        self.title = title if title else "Now Playing"
        self.artist = artist if artist else "Artist"
        self.album = album if album else ""
        
        # Reset scroll position
        self.scroll_offset = 0
        self.update()
        self.text_changed.emit(self.title, self.artist)
    
    def start_animation(self):
        """Start text scrolling animation"""
        if self.animation_enabled:
            self.animation_timer.start(50)  # Update every 50ms
    
    def stop_animation(self):
        """Stop text scrolling animation"""
        self.animation_timer.stop()
    
    def _animate_scroll(self):
        """Update scroll position"""
        if self.bounce:
            # Bouncing effect
            self.scroll_offset += self.scroll_speed * self.direction
            
            if self.scroll_offset >= self.text_width - self.visible_width:
                self.direction = -1
            elif self.scroll_offset <= 0:
                self.direction = 1
        else:
            # Continuous scrolling (wrapping)
            self.scroll_offset += self.scroll_speed
            if self.scroll_offset > self.text_width:
                self.scroll_offset = -self.visible_width
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the scrolling text"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with gradient
        gradient = QLinearGradient(0, 0, 0, self.height)
        gradient.setColorAt(0, QColor("#3B4554"))
        gradient.setColorAt(1, QColor("#2C303A"))
        painter.fillRect(self.rect(), gradient)
        
        # Draw border
        pen = QPen(self.title_color, 2)
        painter.setPen(pen)
        painter.drawRoundedRect(0, 0, self.width - 1, self.height - 1, 8, 8)
        
        # Set clipping region for scrolling text
        clip_rect = QRect(10, 10, self.width - 20, self.height - 20)
        painter.setClipRect(clip_rect)
        
        # Draw title
        painter.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        painter.setPen(self.title_color)
        
        title_text = self.title
        title_rect = painter.fontMetrics().boundingRect(title_text)
        self.text_width = title_rect.width()
        
        title_x = 10 - self.scroll_offset
        title_y = 20
        painter.drawText(title_x, title_y + title_rect.height(), title_text)
        
        # Draw artist name
        painter.setFont(QFont("Arial", 11))
        painter.setPen(self.artist_color)
        
        artist_text = f"{self.artist}"
        if self.album:
            artist_text += f" • {self.album}"
        
        artist_y = title_y + title_rect.height() + 15
        painter.drawText(10, artist_y + painter.fontMetrics().height(), artist_text)
        
        # Draw accent line
        painter.setPen(QPen(self.accent_color, 2))
        painter.drawLine(10, 8, self.width - 10, 8)
        
        painter.end()


class AdvancedScrollingTextWidget(QWidget):
    """Advanced scrolling text with multiple animation effects"""
    
    def __init__(self, width: int = 1000, height: int = 120):
        """
        Initialize advanced scrolling text widget
        
        Args:
            width: Widget width
            height: Widget height
        """
        super().__init__()
        self.width = width
        self.height = height
        
        # Text content
        self.title = "Now Playing"
        self.artist = "Artist Name"
        self.album = ""
        self.is_playing = False
        
        # Animation parameters
        self.animation_frame = 0
        self.max_frames = 120
        self.effect_type = "glow"  # "glow", "pulse", "rainbow", "shadow"
        self.scroll_offset = 0
        self.scroll_speed = 1.5
        
        # Colors
        self.base_colors = {
            "bg": QColor("#3B4554"),
            "title": QColor("#6FB3D5"),
            "artist": QColor("#D5F4E6"),
            "accent": QColor("#EEB76B"),
            "secondary": QColor("#DF7676"),
        }
        
        self.setFixedSize(width, height)
        self.setup_timers()
        self.start()
    
    def setup_timers(self):
        """Setup animation timers"""
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
    
    def start(self):
        """Start animation"""
        self.animation_timer.start(30)  # 30fps animation
    
    def stop(self):
        """Stop animation"""
        self.animation_timer.stop()
    
    def set_now_playing(self, title: str, artist: str, album: str = "", is_playing: bool = True):
        """Update now-playing information"""
        self.title = title
        self.artist = artist
        self.album = album
        self.is_playing = is_playing
        self.animation_frame = 0
        self.update()
    
    def set_effect(self, effect_type: str):
        """Set animation effect type"""
        if effect_type in ["glow", "pulse", "rainbow", "shadow", "wave"]:
            self.effect_type = effect_type
    
    def _update_animation(self):
        """Update animation frame"""
        self.animation_frame = (self.animation_frame + 1) % self.max_frames
        self.scroll_offset += self.scroll_speed
        self.update()
    
    def paintEvent(self, event):
        """Paint advanced animated text"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background
        painter.fillRect(self.rect(), self.base_colors["bg"])
        
        # Draw border with gradient
        pen = QPen(self.base_colors["title"], 2)
        painter.setPen(pen)
        painter.drawRoundedRect(0, 0, self.width - 1, self.height - 1, 10, 10)
        
        # Draw decorative lines
        self._draw_decorative_elements(painter)
        
        # Draw title with effect
        self._draw_title_with_effect(painter)
        
        # Draw artist and album
        self._draw_artist_info(painter)
        
        # Draw playing indicator
        if self.is_playing:
            self._draw_playing_indicator(painter)
        
        painter.end()
    
    def _draw_decorative_elements(self, painter: QPainter):
        """Draw decorative elements"""
        # Top line
        painter.setPen(QPen(self.base_colors["accent"], 1))
        painter.drawLine(10, 8, self.width - 10, 8)
        
        # Bottom line
        painter.setPen(QPen(self.base_colors["secondary"], 1))
        painter.drawLine(10, self.height - 8, self.width - 10, self.height - 8)
        
        # Side accents
        accent_height = int(30 * abs(self.animation_frame - 60) / 60)
        painter.setPen(QPen(self.base_colors["title"], 2))
        painter.drawLine(5, (self.height - accent_height) // 2, 5, (self.height + accent_height) // 2)
        painter.drawLine(self.width - 5, (self.height - accent_height) // 2, 
                        self.width - 5, (self.height + accent_height) // 2)
    
    def _draw_title_with_effect(self, painter: QPainter):
        """Draw title with selected effect"""
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        if self.effect_type == "glow":
            self._draw_glow_text(painter, self.title, 20, self.base_colors["title"])
        elif self.effect_type == "pulse":
            self._draw_pulse_text(painter, self.title, 20, self.base_colors["title"])
        elif self.effect_type == "shadow":
            self._draw_shadow_text(painter, self.title, 20, self.base_colors["title"])
        elif self.effect_type == "rainbow":
            self._draw_rainbow_text(painter, self.title, 20)
        else:
            painter.setPen(self.base_colors["title"])
            painter.drawText(20, 35, self.title)
    
    def _draw_glow_text(self, painter: QPainter, text: str, x: int, color: QColor):
        """Draw text with glow effect"""
        glow_radius = int(10 * abs(self.animation_frame - 60) / 60)
        
        # Draw glow layers
        for i in range(glow_radius, 0, -2):
            glow_color = QColor(color)
            glow_color.setAlpha(int(100 * (1 - i / glow_radius)))
            painter.setPen(glow_color)
            painter.setFont(QFont("Arial", 16 + i // 2, QFont.Weight.Bold))
            painter.drawText(x - i // 2, 35, text)
        
        # Draw main text
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.setPen(color)
        painter.drawText(x, 35, text)
    
    def _draw_pulse_text(self, painter: QPainter, text: str, x: int, color: QColor):
        """Draw text with pulse effect"""
        scale = 0.8 + 0.2 * abs(self.animation_frame - 60) / 60
        
        # Save painter state
        painter.save()
        painter.translate(x + 50, 25)
        painter.scale(scale, scale)
        painter.translate(-(x + 50), -25)
        
        painter.setPen(color)
        painter.drawText(x, 35, text)
        
        painter.restore()
    
    def _draw_shadow_text(self, painter: QPainter, text: str, x: int, color: QColor):
        """Draw text with shadow effect"""
        shadow_offset = int(5 * abs(self.animation_frame - 60) / 60)
        
        # Draw shadow
        shadow_color = QColor("#000000")
        shadow_color.setAlpha(100)
        painter.setPen(shadow_color)
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.drawText(x + shadow_offset, 35 + shadow_offset, text)
        
        # Draw main text
        painter.setPen(color)
        painter.drawText(x, 35, text)
    
    def _draw_rainbow_text(self, painter: QPainter, text: str, x: int):
        """Draw text with rainbow color effect"""
        colors = [
            QColor("#6FB3D5"),  # Blue
            QColor("#D5F4E6"),  # Mint
            QColor("#EEB76B"),  # Orange
            QColor("#DF7676"),  # Red
            QColor("#8FBD81"),  # Green
        ]
        
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        
        char_x = x
        for i, char in enumerate(text):
            color = colors[(i + self.animation_frame // 10) % len(colors)]
            painter.setPen(color)
            painter.drawText(char_x, 35, char)
            char_x += painter.fontMetrics().width(char) + 2
    
    def _draw_artist_info(self, painter: QPainter):
        """Draw artist and album information"""
        painter.setFont(QFont("Arial", 12))
        painter.setPen(self.base_colors["artist"])
        
        artist_text = self.artist
        if self.album:
            artist_text += f" • {self.album}"
        
        painter.drawText(20, 65, artist_text)
    
    def _draw_playing_indicator(self, painter: QPainter):
        """Draw animated playing indicator"""
        # Draw 3 animated bars
        bar_width = 4
        bar_spacing = 8
        bar_heights = []
        
        for i in range(3):
            phase = (self.animation_frame + i * 40) % 120
            height = int(20 * abs(phase - 60) / 60)
            bar_heights.append(height)
        
        painter.setPen(QPen(self.base_colors["accent"], 2))
        
        x = self.width - 50
        for i, height in enumerate(bar_heights):
            y = self.height // 2 - height // 2
            painter.drawLine(x + i * (bar_width + bar_spacing), y + height, 
                           x + i * (bar_width + bar_spacing), y)
            painter.drawLine(x + i * (bar_width + bar_spacing) + bar_width, y + height,
                           x + i * (bar_width + bar_spacing) + bar_width, y)


# Example usage
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create window
    window = QWidget()
    window.setGeometry(100, 100, 1000, 300)
    window.setStyleSheet("background-color: #2C303A;")
    
    layout = QVBoxLayout()
    window.setLayout(layout)
    
    # Add basic scrolling text widget
    scroll_widget = ScrollingTextWidget(980, 80)
    scroll_widget.set_now_playing("Nova Rising", "Synthwave Dream", "Digital Horizons")
    layout.addWidget(scroll_widget)
    
    # Add advanced scrolling text widget with glow effect
    advanced_widget = AdvancedScrollingTextWidget(980, 120)
    advanced_widget.set_now_playing("Eternal Echo", "Neon Skies", "Cyberpunk 2077", True)
    advanced_widget.set_effect("glow")
    layout.addWidget(advanced_widget)
    
    window.show()
    sys.exit(app.exec())
