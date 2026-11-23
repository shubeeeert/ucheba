"""Внешняя·сортировка·CSV-файла·на·Python.

Используются·только·стандартные·модули:·csv·для·построчного·чтения·блоками,
heapq·для·K-образного·слияния·и·context·managers·для·всех·файлов.·Память
ограничена·размером·одного·блока,·который·зависит·от·размера·исходного·файла.
"""

import csv
import heapq
import os
import shutil
import sys
import time
from pathlib import Path
from typing import Callable, List, Optional

FIELDS = ("name", "group", "dob", "height", "weight", "expulsion")


def _log(message: str) -> None:
····"""Безопасный·вывод:·в·GUI-сборке·sys.stdout·может·отсутствовать."""
    stream = getattr(sys, "stdout", None)
    if stream is not None:
        print(message, end="" if message.endswith("\n") else "\n")


def normalize_row(row: List[str]) -> List[str]:
····"""Приводит·строку·csv·к·шести·полям."""
    result = list(row)
    if len(result) < len(FIELDS):
        result.extend([""] * (len(FIELDS) - len(result)))
    return result[:len(FIELDS)]


def sort_key(row: List[str], keyIndex: int):
····"""Возвращает·сравнимый·ключ·сортировки·для·указанного·поля."""
    if keyIndex < 0 or keyIndex >= len(FIELDS):
········raise·ValueError("Неизвестный·ключ·сортировки")
    value = row[keyIndex].strip()
    if keyIndex == 3:
        return int(value)
    if keyIndex == 4:
        return float(value)
    if keyIndex == 5:
        return value.lower() in ("true", "1", "yes")
    return value


class _Key:
····"""Обёртка·ключа,·позволяющая·использовать·один·heap·для·двух·направлений."""

    __slots__ = ("value", "reverse")

    def __init__(self, value, reverse: bool):
        self.value = value
        self.reverse = reverse

    def __lt__(self, other: "_Key") -> bool:
        if self.reverse:
            return self.value > other.value
        return self.value < other.value


def _row_chars(row: List[str]) -> int:
    return sum(len(cell) for cell in row) + len(row) - 1


def _next_row(reader) -> Optional[List[str]]:
    for row in reader:
        if row and any(cell != "" for cell in row):
            return normalize_row(row)
    return None


def external_sort(
    path,
    keyIndex: int,
    ascending: bool,
    progressCallback: Optional[Callable[[float], None]] = None,
    timingCallback: Optional[Callable[[str], None]] = None,
) -> bool:
····"""Сортирует·CSV-файл·во·внешней·памяти·и·пишет·результат·в·sorted.txt."""
    if keyIndex < 0 or keyIndex >= len(FIELDS):
········_log("[Python]·Некорректный·ключ·сортировки.\n")
        return False

    start_total = time.time()
    path_str = path.decode("utf-8") if isinstance(path, (bytes, bytearray)) else os.fspath(path)
    path_obj = Path(path_str)
    if not path_obj.is_file():
········_log(f"[Python]·Входной·файл·не·найден:·{path_str}\n")
        return False

    total_size = path_obj.stat().st_size
    parent = path_obj.parent if str(path_obj.parent) else Path.cwd()
    out_path = parent / "sorted.txt"
    temp_dir = parent / f".lab5_py_tmp_{os.getpid()}"

    def report(value: float) -> None:
        if progressCallback is None:
            return
        if value < 0.0:
            value = 0.0
        elif value > 1.0:
            value = 1.0
        progressCallback(value)

    if out_path.exists():
        try:
            out_path.unlink()
        except OSError:
            pass

    shutil.rmtree(temp_dir, ignore_errors=True)
    try:
        temp_dir.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
········_log(f"[Python]·Не·удалось·создать·каталог·временных·файлов:·{exc}\n")
        return False

    if total_size == 0:
        with open(out_path, "w", encoding="utf-8", newline=""):
            pass
        shutil.rmtree(temp_dir, ignore_errors=True)
        report(1.0)
        return True

····#·~1.2%·размера·файла·в·символах,·но·не·более·8·млн·символов,
····#·и·не·более·120·тысяч·строк·в·одном·блоке.·Для·файла·1·ГБ·это·<100·МБ·ОЗУ.
    max_chars = max(200_000, min(8_000_000, int(total_size * 0.012)))
    max_rows = max(2_000, min(120_000, int(total_size * 0.00012)))
    total_chars_estimate = max(1, total_size // 2)

    reverse = not ascending
    chunk_paths: List[Path] = []
    files = []
    success = False

    try:
        report(0.0)
        start_split = time.time()

        batch: List[List[str]] = []
        batch_chars = 0
        processed_chars = 0

        def flush_batch() -> None:
            nonlocal batch, batch_chars
            if not batch:
                return
            batch.sort(key=lambda row: sort_key(row, keyIndex), reverse=reverse)
            chunk_path = temp_dir / f"r{len(chunk_paths):06d}.csv"
            with open(chunk_path, "w", encoding="utf-8", newline="") as chunk_file:
                writer = csv.writer(chunk_file, lineterminator="\n")
                writer.writerows(batch)
            chunk_paths.append(chunk_path)
            batch = []
            batch_chars = 0

        with open(path_str, "r", encoding="utf-8", newline="") as source:
            reader = csv.reader(source)
            for row in reader:
                if not row or not any(cell != "" for cell in row):
                    continue
                normalized = normalize_row(row)
                chars = _row_chars(normalized)
                batch.append(normalized)
                batch_chars += chars
                processed_chars += chars

                if len(batch) >= max_rows or batch_chars >= max_chars:
                    flush_batch()
                    report(processed_chars / total_chars_estimate)

        flush_batch()
        report(min(1.0, processed_chars / total_chars_estimate))
        split_time = time.time() - start_split

        report(0.0)
        start_merge = time.time()

        readers = []
        heap = []
        for index, chunk_path in enumerate(chunk_paths):
            file = open(chunk_path, "r", encoding="utf-8", newline="")
            files.append(file)
            reader = csv.reader(file)
            readers.append(reader)
            first_row = _next_row(reader)
            if first_row is not None:
                heapq.heappush(
                    heap,
                    (_Key(sort_key(first_row, keyIndex), reverse), index, first_row),
                )

        last_report_chars = 0
        written_chars = 0
        with open(out_path, "w", encoding="utf-8", newline="") as output:
            writer = csv.writer(output, lineterminator="\n")
            while heap:
                _, index, row = heapq.heappop(heap)
                writer.writerow(row)
                written_chars += _row_chars(row)

                if written_chars - last_report_chars >= 8 * 1024 * 1024:
                    report(written_chars / total_chars_estimate)
                    last_report_chars = written_chars

                next_row = _next_row(readers[index])
                if next_row is not None:
                    heapq.heappush(
                        heap,
                        (_Key(sort_key(next_row, keyIndex), reverse), index, next_row),
                    )

        report(1.0)
        merge_time = time.time() - start_merge
        total_time = time.time() - start_total

        timing = (
············f"[Python]·Этап·разбиения:·{split_time:.2f}·с.\n"
············f"[Python]·Этап·слияния:·{merge_time:.2f}·с.\n"
············f"[Python]·Общее·время:·{total_time:.2f}·с.\n"
        )
        _log(timing)
        if timingCallback is not None:
            timingCallback(timing)
        success = True
····except·Exception·as·exc:··#·noqa:·BLE001·-·ошибка·передаётся·в·GUI·как·false
········_log(f"[Python]·Ошибка·сортировки:·{exc}\n")
    finally:
        for file in files:
            file.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
        if not success and out_path.exists():
            try:
                out_path.unlink()
            except OSError:
                pass

    return success


if __name__ == "__main__":
    import argparse

····parser·=·argparse.ArgumentParser(description="Внешняя·сортировка·CSV·на·Python")
    parser.add_argument("path", nargs="?", default="data.csv")
    parser.add_argument("key", nargs="?", type=int, default=0)
    parser.add_argument("direction", nargs="?", default="asc", choices=("asc", "desc"))
    args = parser.parse_args()

    def progress(value: float) -> None:
········print(f"\r[Python]·Прогресс:·{value·*·100:5.1f}%",·end="",·flush=True)

    result = external_sort(args.path, args.key, args.direction == "asc", progress)
    print()
    raise SystemExit(0 if result else 1)
