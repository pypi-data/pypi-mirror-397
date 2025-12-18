import sys
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QApplication, QWidget

class EdgeLightOverlay(QWidget):
    def __init__(self):
        super().__init__()

        # Make window frameless, always on top, translucent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Full screen overlay (adjust if multi-monitor)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Example glow parameters
        self.glow_color = QColor(0, 170, 255, 150)   # semi-transparent teal
        self.glow_width = 20

        # Show
        self.show()

    def paintEvent(self, event):
        # Draw the glowing border
        painter = QPainter(self)
        pen = QPen(self.glow_color, self.glow_width)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(
            self.glow_width//2,
            self.glow_width//2,
            -self.glow_width//2,
            -self.glow_width//2
        ))

def main():
    """Main entry point for the edgelight application."""
    app = QApplication(sys.argv)
    overlay = EdgeLightOverlay()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
