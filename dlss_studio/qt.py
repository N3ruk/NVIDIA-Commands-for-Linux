"""Prefer PySide6; use the system PyQt6 without downloading dependencies."""
try:
    from PySide6.QtCore import Qt, QTimer, QSize
    from PySide6.QtGui import QFont, QIcon, QDesktopServices, QPalette, QColor
    from PySide6.QtCore import QUrl
    from PySide6.QtWidgets import *
    BINDING = "PySide6"
except ImportError:
    from PyQt6.QtCore import Qt, QTimer, QSize, QUrl
    from PyQt6.QtGui import QFont, QIcon, QDesktopServices, QPalette, QColor
    from PyQt6.QtWidgets import *
    BINDING = "PyQt6"
