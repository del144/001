from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Generic, Iterable, Iterator, TypeVar

T = TypeVar("T")
DATETIME_FORMAT = "%d.%m.%Y %H:%M:%S"


class Entity(ABC):


    @abstractmethod
    def summary(self) -> str:

        raise NotImplementedError


class EntityMap(Generic[T]):


    def __init__(self) -> None:
        self._pairs: list[tuple[str, T]] = []

    def put(self, key: str, value: T) -> None:
        if not isinstance(key, str) or not key:
            raise ValueError("Ключ должен быть непустой строкой")
        for index, pair in enumerate(self._pairs):
            if pair[0] == key:
                self._pairs[index] = (key, value)
                return
        self._pairs.append((key, value))

    def get(self, key: str, default: T | None = None) -> T | None:
        for stored_key, value in self._pairs:
            if stored_key == key:
                return value
        return default

    def remove(self, key: str) -> bool:
        for index, pair in enumerate(self._pairs):
            if pair[0] == key:
                del self._pairs[index]
                return True
        return False

    def values(self) -> tuple[T, ...]:
        return tuple(value for _, value in self._pairs)

    def items(self) -> tuple[tuple[str, T], ...]:
        return tuple(self._pairs)

    def keys(self) -> tuple[str, ...]:
        return tuple(key for key, _ in self._pairs)

    def __getitem__(self, key: str) -> T:
        value = self.get(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: str, value: T) -> None:
        self.put(key, value)

    def __contains__(self, key: object) -> bool:
        return isinstance(key, str) and any(stored_key == key for stored_key, _ in self._pairs)

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._pairs)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, EntityMap) and self.items() == other.items()

    def __repr__(self) -> str:
        return f"EntityMap({self._pairs!r})"

    def __str__(self) -> str:
        return f"Отображение: {len(self)} объектов"

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, EntityMap):
            return NotImplemented
        return len(self) < len(other)


class SessionRecord(Entity):

    def __init__(self, login: str, time_in: datetime, time_out: datetime | None = None) -> None:
        self.login = login
        self.time_in = time_in
        self.time_out = time_out

    @property
    def login(self) -> str:
        return self._login

    @login.setter
    def login(self, value: str) -> None:
        clean_value = str(value).strip()
        self._login = clean_value if clean_value else "UserName"

    @property
    def time_in(self) -> datetime:
        return self._time_in

    @time_in.setter
    def time_in(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise TypeError("time_in должен иметь тип datetime")
        self._time_in = value

    @property
    def time_out(self) -> datetime | None:
        return self._time_out

    @time_out.setter
    def time_out(self, value: datetime | None) -> None:
        if value is not None and not isinstance(value, datetime):
            raise TypeError("time_out должен иметь тип datetime или None")
        self._time_out = value

    def finish(self, moment: datetime) -> None:
        self.time_out = moment

    def summary(self) -> str:
        end_text = self.time_out.strftime(DATETIME_FORMAT) if self.time_out else "сеанс открыт"
        return f"{self.login}: {self.time_in.strftime(DATETIME_FORMAT)} — {end_text}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, SessionRecord) and (self.login, self.time_in) == (other.login, other.time_in)

    def __repr__(self) -> str:
        return f"SessionRecord(login={self.login!r}, time_in={self.time_in!r}, time_out={self.time_out!r})"

    def __str__(self) -> str:
        return self.summary()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, SessionRecord):
            return NotImplemented
        return self.time_in < other.time_in

    def __len__(self) -> int:
        return len(self.login)

    def __bool__(self) -> bool:
        return bool(self.login)


class ReportWriter:


    def __init__(self, directory: Path) -> None:
        self._directory = directory
        self._csv_path = directory / "sessions.csv"
        self._report_path = directory / "session_report.txt"

    @staticmethod
    def format_datetime(value: datetime | None) -> str:
        return value.strftime(DATETIME_FORMAT) if value else "—"

    def _read_history(self) -> list[SessionRecord]:
        history: list[SessionRecord] = []
        if not self._csv_path.exists():
            return history
        try:
            with self._csv_path.open("r", encoding="utf-8", newline="") as stream:
                reader = csv.reader(stream)
                next(reader, None)
                for row in reader:
                    if len(row) != 3:
                        continue
                    try:
                        start = datetime.strptime(row[1], DATETIME_FORMAT)
                        finish = datetime.strptime(row[2], DATETIME_FORMAT) if row[2] else None
                        history.append(SessionRecord(row[0], start, finish))
                    except ValueError:
                        continue
        except OSError:
            return history
        return history

    def save(self, session: SessionRecord) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        history = self._read_history()
        history.append(session)
        with self._csv_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("login", "time_in", "time_out"))
            for record in history:
                writer.writerow((record.login, self.format_datetime(record.time_in), self.format_datetime(record.time_out)))
        self._write_text_report(history)

    def _write_text_report(self, records: list[SessionRecord]) -> None:
        logins = ["login"] + [record.login for record in records]
        login_width = max(12, *(len(login) for login in logins))
        time_width = max(19, len("time_in"), len("time_out"))
        border = "+-" + "-" * login_width + "-+-" + "-" * time_width + "-+-" + "-" * time_width + "-+"
        rows = [
            border,
            f"| {'login':<{login_width}} | {'time_in':<{time_width}} | {'time_out':<{time_width}} |",
            border,
        ]
        for record in records:
            rows.append(
                f"| {record.login:<{login_width}} | "
                f"{self.format_datetime(record.time_in):<{time_width}} | "
                f"{self.format_datetime(record.time_out):<{time_width}} |"
            )
        rows.append(border)
        with self._report_path.open("w", encoding="utf-8", newline="") as stream:
            stream.write("\n".join(rows) + "\n")
