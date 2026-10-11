from __future__ import annotations

import csv
import getpass
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from uuid import uuid4

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QMessageBox, QListWidgetItem, QAbstractItemView,
)

from common import EntityMap, ReportWriter, SessionRecord
from models import Student
from ui_components import (
    MainAppWindow, HoverButton, FocusLineEdit, ClickableLabel, HintListWidget,
    SafeComboBox, AnimatedCheckBox, ValidatedSpinBox, CalendarDateEdit,
    NoteTextEdit, StatusProgressBar, GroupPanel, apply_app_style,
)


class StudentRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def exists(self) -> bool:
        return self._path.exists()

    def load(self) -> EntityMap[Student]:
        result: EntityMap[Student] = EntityMap()
        if not self._path.exists():
            return result
        try:
            with self._path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream)
                next(reader, None)
                for row in reader:
                    if len(row) != 7:
                        continue
                    try:
                        student = Student(row[0], row[1], row[2], int(row[3]), int(row[4]), row[5], row[6])
                        result.put(student.entity_id, student)
                    except (ValueError, TypeError):
                        continue
        except OSError:
            return EntityMap()
        return result

    def save(self, students: EntityMap[Student]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("id", "full_name", "group_name", "grade", "attendance", "assessment_date", "notes"))
            for student in students.values():
                writer.writerow((student.entity_id, student.full_name, student.group_name, student.grade, student.attendance, student.assessment_date, student.notes))


class StudentJournalWindow(MainAppWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ООП · Журнал успеваемости")
        self.resize(1000, 790)
        self._data_directory = Path(__file__).resolve().parent / "data"
        self._repository = StudentRepository(self._data_directory / "students.csv")
        self._students = self._repository.load()
        if not self._repository.exists():
            self._students = self._demo_students()
            self._repository.save(self._students)
        self._session = SessionRecord(getpass.getuser() or "UserName", datetime.now())
        self._report_writer = ReportWriter(self._data_directory)
        self.set_close_callback(self._save_report)
        self._build_ui()
        self._refresh_students()

    @staticmethod
    def _demo_students() -> EntityMap[Student]:
        result: EntityMap[Student] = EntityMap()
        today = date.today()
        samples = (
            ("Иванов Артём Сергеевич", "МТ-21", 92, 96),
            ("Петрова Анна Игоревна", "МТ-21", 88, 100),
            ("Смирнов Максим Олегович", "МТ-21", 74, 83),
            ("Кузнецова Мария Андреевна", "МТ-22", 97, 98),
            ("Попов Дмитрий Павлович", "МТ-22", 68, 79),
            ("Соколова Елена Романовна", "МТ-21", 81, 91),
            ("Лебедев Кирилл Денисович", "МТ-23", 76, 87),
            ("Новикова Дарья Максимовна", "МТ-22", 93, 99),
            ("Морозов Илья Викторович", "МТ-23", 59, 72),
            ("Волкова Софья Никитична", "МТ-21", 85, 94),
        )
        for index, item in enumerate(samples, start=1):
            student = Student(f"student-{index:03d}", item[0], item[1], item[2], item[3], (today - timedelta(days=index)).isoformat(), "Демонстрационная запись")
            result.put(student.entity_id, student)
        return result

    def _build_ui(self) -> None:
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)
        title = ClickableLabel("Журнал успеваемости студентов")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title.setToolTip("Нажмите, чтобы обновить журнал")
        title.clicked.connect(self._refresh_students)
        root.addWidget(title)

        form = GroupPanel("Добавить студента")
        grid = QGridLayout(form)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(9)
        self.name_input = FocusLineEdit()
        self.name_input.setPlaceholderText("Фамилия, имя и отчество")
        self.group_input = FocusLineEdit()
        self.group_input.setPlaceholderText("Например, МТ-21")
        self.grade_input = ValidatedSpinBox()
        self.grade_input.setRange(0, 100)
        self.grade_input.setValue(80)
        self.attendance_input = ValidatedSpinBox()
        self.attendance_input.setRange(0, 100)
        self.attendance_input.setValue(90)
        self.date_input = CalendarDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd.MM.yyyy")
        self.date_input.setDate(QDate.currentDate())
        self.notes_input = NoteTextEdit()
        self.notes_input.setPlaceholderText("Комментарий преподавателя (необязательно). Ctrl+Enter добавляет запись.")
        self.notes_input.setMaximumHeight(66)
        grid.addWidget(QLabel("ФИО"), 0, 0)
        grid.addWidget(self.name_input, 0, 1, 1, 3)
        grid.addWidget(QLabel("Группа"), 1, 0)
        grid.addWidget(self.group_input, 1, 1)
        grid.addWidget(QLabel("Баллы (0–100)"), 1, 2)
        grid.addWidget(self.grade_input, 1, 3)
        grid.addWidget(QLabel("Посещаемость (%)"), 2, 0)
        grid.addWidget(self.attendance_input, 2, 1)
        grid.addWidget(QLabel("Дата оценки"), 2, 2)
        grid.addWidget(self.date_input, 2, 3)
        grid.addWidget(QLabel("Комментарий"), 3, 0, Qt.AlignmentFlag.AlignTop)
        grid.addWidget(self.notes_input, 3, 1, 1, 3)
        root.addWidget(form)

        action_row = QHBoxLayout()
        action_row.setSpacing(8)
        self.add_button = HoverButton("Добавить студента")
        self.remove_button = HoverButton("Удалить выбранного")
        self.remove_button.setObjectName("secondaryButton")
        action_row.addWidget(self.add_button)
        action_row.addWidget(self.remove_button)
        action_row.addStretch(1)
        self.scholarship_filter = AnimatedCheckBox("Только студенты с баллами от 75")
        action_row.addWidget(self.scholarship_filter)
        root.addLayout(action_row)

        list_panel = GroupPanel("Студенты")
        list_layout = QVBoxLayout(list_panel)
        filter_row = QHBoxLayout()
        filter_row.addWidget(QLabel("Группа:"))
        self.group_filter = SafeComboBox()
        self.group_filter.addItems(("Все группы", "МТ-21", "МТ-22", "МТ-23"))
        self.group_filter.setMaximumWidth(200)
        filter_row.addWidget(self.group_filter)
        filter_row.addStretch(1)
        self.average_label = QLabel("Средний балл: —")
        filter_row.addWidget(self.average_label)
        list_layout.addLayout(filter_row)
        self.student_list = HintListWidget()
        self.student_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.student_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.student_list, 1)
        self.progress = StatusProgressBar()
        self.progress.setRange(0, 100)
        list_layout.addWidget(self.progress)
        root.addWidget(list_panel, 1)

        self.setCentralWidget(central)
        self.statusBar().showMessage("Список сохраняется в CSV автоматически")
        self.add_button.clicked.connect(self._add_student)
        self.remove_button.clicked.connect(self._remove_selected)
        self.scholarship_filter.toggled.connect(self._refresh_students)
        self.group_filter.currentTextChanged.connect(self._refresh_students)
        self.notes_input.submitRequested.connect(self._add_student)
        apply_app_style(self)

    def _add_student(self) -> None:
        full_name = self.name_input.text().strip()
        group_name = self.group_input.text().strip()
        if not full_name or not group_name:
            QMessageBox.warning(self, "Не хватает данных", "Заполните ФИО и группу.")
            return
        student = Student(
            f"student-{uuid4().hex[:10]}", full_name, group_name,
            self.grade_input.value(), self.attendance_input.value(),
            self.date_input.date().toString("yyyy-MM-dd"), self.notes_input.toPlainText(),
        )
        self._students.put(student.entity_id, student)
        self._save_students()
        self.name_input.clear()
        self.group_input.clear()
        self.notes_input.clear()
        self._refresh_students()
        self.statusBar().showMessage("Студент добавлен", 3000)

    def _remove_selected(self) -> None:
        item = self.student_list.currentItem()
        if item is None:
            self.statusBar().showMessage("Сначала выберите студента", 3000)
            return
        student = self._students.get(str(item.data(Qt.ItemDataRole.UserRole)))
        if student is not None:
            self._students.remove(student.entity_id)
            self._save_students()
            self._refresh_students()
            self.statusBar().showMessage("Студент удалён", 3000)

    def _refresh_students(self, *_args) -> None:
        self.student_list.clear()
        group_mode = self.group_filter.currentText() if hasattr(self, "group_filter") else "Все группы"
        scholarship_only = self.scholarship_filter.isChecked() if hasattr(self, "scholarship_filter") else False
        visible: list[Student] = []
        for student in sorted(self._students.values()):
            if group_mode != "Все группы" and student.group_name != group_mode:
                continue
            if scholarship_only and not student.scholarship_eligible:
                continue
            visible.append(student)
            item = QListWidgetItem(student.summary())
            item.setData(Qt.ItemDataRole.UserRole, student.entity_id)
            item.setForeground(QColor("darkgreen") if student.scholarship_eligible else QColor("darkblue"))
            self.student_list.addItem(item)
        average = sum(student.grade for student in visible) / len(visible) if visible else 0
        self.average_label.setText(f"Средний балл: {average:.1f}" if visible else "Средний балл: —")
        self.progress.setValue(round(average))
        self.progress.setFormat(f"Средний балл по выборке: {average:.1f}/100 (%p%)")
        self.statusBar().showMessage(f"Всего студентов: {len(self._students)} · отображается: {len(visible)}")

    def _save_students(self) -> None:
        self._repository.save(self._students)

    def _save_report(self) -> None:
        self._session.finish(datetime.now())
        self._report_writer.save(self._session)


class AppLauncher:
    @staticmethod
    def run() -> None:
        application = QApplication(sys.argv)
        application.setApplicationName("ООП · Журнал успеваемости")
        window = StudentJournalWindow()
        window.show()
        sys.exit(application.exec())


if __name__ == "__main__":
    AppLauncher.run()
