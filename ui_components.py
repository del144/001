"""Пользовательские Qt-виджеты с переопределенными обработчиками событий."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QTextEdit,
)


class HoverButton(QPushButton):
    """Кнопка с переопределенными событиями наведения и нажатия."""

    def enterEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        self.setProperty("pressed", True)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.setProperty("pressed", False)
        super().mouseReleaseEvent(event)


class FocusLineEdit(QLineEdit):
    """Поле ввода с реакцией на фокус и очисткой по Escape."""

    def focusInEvent(self, event) -> None:
        self.setProperty("focused", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self.setProperty("focused", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().focusOutEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
            event.accept()
            return
        super().keyPressEvent(event)


class ClickableLabel(QLabel):
    clicked = Signal()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class HintListWidget(QListWidget):
    """Список с обработкой клавиатурных событий."""

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.clearSelection()
            event.accept()
            return
        super().keyPressEvent(event)


class SafeComboBox(QComboBox):
    """Не меняет выбранный элемент колесиком мыши без фокуса."""

    def wheelEvent(self, event) -> None:
        if not self.hasFocus():
            event.ignore()
            return
        super().wheelEvent(event)


class AnimatedCheckBox(QCheckBox):
    """Чекбокс, обновляющий свой стиль при смене состояния."""

    def nextCheckState(self) -> None:
        super().nextCheckState()
        self.setProperty("checkedState", self.isChecked())
        self.style().unpolish(self)
        self.style().polish(self)


class ValidatedSpinBox(QSpinBox):
    """Целочисленный счетчик с безопасным изменением значения."""

    def stepBy(self, steps: int) -> None:
        super().stepBy(steps)
        self.setValue(max(self.minimum(), min(self.maximum(), self.value())))


class CurrencySpinBox(QDoubleSpinBox):
    """Счетчик денежной суммы."""

    def stepBy(self, steps: int) -> None:
        super().stepBy(steps)
        self.setValue(max(self.minimum(), min(self.maximum(), self.value())))


class CalendarDateEdit(QDateEdit):
    """Поле даты: Escape возвращает сегодняшнюю дату."""

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key.Key_Escape:
            self.setDate(QDate.currentDate())
            event.accept()
            return
        super().keyPressEvent(event)


class NoteTextEdit(QTextEdit):
    submitRequested = Signal()

    def keyPressEvent(self, event) -> None:
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.submitRequested.emit()
            event.accept()
            return
        super().keyPressEvent(event)


class StatusProgressBar(QProgressBar):
    """Полоса прогресса с собственным обработчиком отрисовки."""

    def paintEvent(self, event) -> None:
        super().paintEvent(event)


class GroupPanel(QGroupBox):
    """Группа формы, визуально реагирующая на наведение мыши."""

    def enterEvent(self, event) -> None:
        self.setProperty("hovered", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.setProperty("hovered", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)


class MainAppWindow(QMainWindow):
    """Основное окно, вызывающее переданную процедуру при закрытии."""

    def __init__(self) -> None:
        super().__init__()
        self._close_callback = None
        self._close_callback_called = False

    def set_close_callback(self, callback) -> None:
        self._close_callback = callback

    def closeEvent(self, event) -> None:
        if not self._close_callback_called and self._close_callback is not None:
            self._close_callback_called = True
            self._close_callback()
        super().closeEvent(event)


def apply_app_style(widget: QMainWindow) -> None:
    """Единый стиль и размеры для выравнивания элементов интерфейса."""
    widget.setStyleSheet("""
        QMainWindow, QWidget { background: #f4f7fb; color: #253247; font-size: 13px; }
        QLabel { background: transparent; }
        QLabel#pageTitle { font-size: 23px; font-weight: 700; color: #1e3a5f; padding: 5px 0; }
        QGroupBox { border: 1px solid #cdd8e5; border-radius: 10px; margin-top: 10px; padding: 12px; font-weight: 600; }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 5px; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTextEdit, QListWidget {
            background: #ffffff; border: 1px solid #c6d2e0; border-radius: 6px; padding: 7px; min-height: 20px;
        }
        QLineEdit[focused="true"] { border: 2px solid #3b82f6; }
        QPushButton { background: #2563eb; color: white; border: 0; border-radius: 7px; padding: 9px 13px; min-height: 18px; font-weight: 600; }
        QPushButton:hover, QPushButton[hovered="true"] { background: #1d4ed8; }
        QPushButton:pressed, QPushButton[pressed="true"] { background: #1e40af; }
        QPushButton#secondaryButton { background: #e0e8f2; color: #24364b; }
        QPushButton#secondaryButton:hover { background: #cad8e8; }
        QProgressBar { border: 1px solid #c6d2e0; border-radius: 6px; height: 18px; text-align: center; background: white; }
        QProgressBar::chunk { background: #22a06b; border-radius: 5px; }
        QListWidget::item { padding: 7px; border-bottom: 1px solid #e5ebf2; }
        QListWidget::item:selected { background: #dbeafe; color: #1e3a5f; }
        QStatusBar { background: #e8eef6; color: #42536a; }
    """)
