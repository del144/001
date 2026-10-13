from __future__ import annotations
from common import Entity


class Student(Entity):


    def __init__(self, entity_id: str, full_name: str, group_name: str, grade: int, attendance: int, assessment_date: str, notes: str = "") -> None:
        self.entity_id = entity_id
        self.full_name = full_name
        self.group_name = group_name
        self.grade = grade
        self.attendance = attendance
        self.assessment_date = assessment_date
        self.notes = notes

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        if not str(value).strip():
            raise ValueError("ID студента не может быть пустым")
        self._entity_id = str(value).strip()

    @property
    def full_name(self) -> str:
        return self._full_name

    @full_name.setter
    def full_name(self, value: str) -> None:
        clean_value = " ".join(str(value).split())
        if not clean_value:
            raise ValueError("ФИО не может быть пустым")
        self._full_name = clean_value

    @property
    def group_name(self) -> str:
        return self._group_name

    @group_name.setter
    def group_name(self, value: str) -> None:
        clean_value = str(value).strip()
        if not clean_value:
            raise ValueError("Группа не может быть пустой")
        self._group_name = clean_value

    @property
    def grade(self) -> int:
        return self._grade

    @grade.setter
    def grade(self, value: int) -> None:
        number = int(value)
        if not 0 <= number <= 100:
            raise ValueError("Баллы должны быть от 0 до 100")
        self._grade = number

    @property
    def attendance(self) -> int:
        return self._attendance

    @attendance.setter
    def attendance(self, value: int) -> None:
        number = int(value)
        if not 0 <= number <= 100:
            raise ValueError("Посещаемость должна быть от 0 до 100")
        self._attendance = number

    @property
    def assessment_date(self) -> str:
        return self._assessment_date

    @assessment_date.setter
    def assessment_date(self, value: str) -> None:
        self._assessment_date = str(value).strip()

    @property
    def notes(self) -> str:
        return self._notes

    @notes.setter
    def notes(self, value: str) -> None:
        self._notes = str(value).strip()

    @property
    def scholarship_eligible(self) -> bool:
        return self.grade >= 75

    def summary(self) -> str:
        award = " · стипендия" if self.scholarship_eligible else ""
        return f"{self.full_name}  ·  {self.group_name}  ·  баллы: {self.grade}/100  ·  посещаемость: {self.attendance}%  ·  дата: {self.assessment_date}{award}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Student) and self.entity_id == other.entity_id

    def __repr__(self) -> str:
        return f"Student(entity_id={self.entity_id!r}, full_name={self.full_name!r}, grade={self.grade!r}, group_name={self.group_name!r})"

    def __str__(self) -> str:
        return self.summary()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return (-self.grade, self.full_name.casefold(), self.group_name) < (-other.grade, other.full_name.casefold(), other.group_name)

    def __len__(self) -> int:
        return len(self.full_name)

    def __bool__(self) -> bool:
        return bool(self.full_name)
