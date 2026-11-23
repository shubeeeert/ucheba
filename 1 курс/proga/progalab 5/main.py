"""Графическое приложение для лабораторной работы №5.

Поддерживает генерацию CSV-файла больше 1 ГБ, внешнюю сортировку модулями
C++ и Python, вывод времён этапов, просмотр фрагментов и проверку порядка.
Все обновления Tkinter выполняются в главном потоке через очередь событий.
"""

import csv
import ctypes
import itertools
import os
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

PROGRESS_CB = ctypes.CFUNCTYPE(None, ctypes.c_float)
TIMING_CB = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

try:
    import generate
except ImportError:
    generate = None

try:
    import external_sort as py_sort
except ImportError:
    py_sort = None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Лабораторная работа №5 — внешняя сортировка CSV")
        self.geometry("1180x700")
        self.configure(bg="#f0f0f0")

        self.events = queue.Queue()
        self.file_path = tk.StringVar(value=os.path.join(os.getcwd(), "data.csv"))
        self.file_info = tk.StringVar(value="Файл не выбран")
        self.file_target = tk.StringVar(value="orig")
        self.dll = None
        self.dll_error = ""

        # Callback-объекты должны жить всё время вызова DLL.
        self._progress_cb = PROGRESS_CB(self._cpp_progress)
        self._timing_cb = TIMING_CB(self._cpp_timing)

        self.init_ui()
        self._load_dll()
        self._set_path(self.file_path.get())
        self.after(100, self._process_events)

    # ------------------------------------------------------------------
    # Интерфейс
    # ------------------------------------------------------------------
    def init_ui(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Green.Horizontal.TProgressbar",
            foreground="#28a745",
            background="#28a745",
        )
        separator_style = ttk.Style()
        separator_style.configure("Purple.TSeparator", background="#c72dbf")

        top = tk.Frame(self, bg="#f0f0f0")
        top.pack(side="top", fill="x", padx=10, pady=(8, 0))
        self.progress = ttk.Progressbar(
            top,
            orient="horizontal",
            length=100,
            mode="determinate",
            style="Green.Horizontal.TProgressbar",
        )
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress_label = tk.Label(top, text="0.0 %", width=8, bg="#f0f0f0")
        self.progress_label.pack(side="right", padx=(8, 0))

        main = tk.Frame(self, bg="#f0f0f0")
        main.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        left = tk.Frame(main, bg="#f0f0f0")
        left.pack(side="left", fill="y", padx=(0, 10))
        right = tk.Frame(main)
        right.pack(side="right", fill="both", expand=True)

        tk.Label(left, text="Файл:", font=("Arial", 9, "bold"), bg="#f0f0f0").pack(anchor="w")
        tk.Label(left, textvariable=self.file_info, fg="gray", wraplength=250,
                 justify="left", bg="#f0f0f0").pack(anchor="w")
        self.choose_button = tk.Button(left, text="Выбрать файл", command=self.choose_file)
        self.choose_button.pack(fill="x", pady=5)
        ttk.Separator(left, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=8)

        tk.Label(left, text="Размер генерации, МиБ (1100 > 1 ГБ):", bg="#f0f0f0").pack(anchor="w")
        vcmd = self.register(self.validate_size)
        self.size_entry = tk.Entry(left, validate="key", validatecommand=(vcmd, "%P"))
        self.size_entry.insert(0, "1100")
        self.size_entry.pack(fill="x", pady=2)
        self.gen_button = tk.Button(left, text="Сгенерировать", command=self.start_generate)
        self.gen_button.pack(fill="x", pady=5)
        ttk.Separator(left, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=8)

        tk.Label(left, text="Модуль сортировки:", bg="#f0f0f0").pack(anchor="w")
        self.mod_combo = ttk.Combobox(left, values=("C++", "Python"), state="readonly")
        self.mod_combo.current(0)
        self.mod_combo.pack(fill="x", pady=2)

        tk.Label(left, text="Ключ сортировки:", bg="#f0f0f0").pack(anchor="w")
        self.key_combo = ttk.Combobox(
            left,
            values=("ФИО", "Группа", "Дата рождения", "Рост", "Вес", "Отчисление"),
            state="readonly",
        )
        self.key_combo.current(0)
        self.key_combo.pack(fill="x", pady=2)

        tk.Label(left, text="Направление:", bg="#f0f0f0").pack(anchor="w")
        self.dir_combo = ttk.Combobox(
            left, values=("По убыванию", "По возрастанию"), state="readonly"
        )
        self.dir_combo.current(1)
        self.dir_combo.pack(fill="x", pady=2)

        self.sort_button = tk.Button(left, text="Отсортировать", command=self.start_sort)
        self.sort_button.pack(fill="x", pady=5)
        ttk.Separator(left, orient="horizontal", style="Purple.TSeparator").pack(fill="x", pady=8)

        tk.Label(left, text="Просмотр файла:", bg="#f0f0f0").pack(anchor="w")
        tk.Radiobutton(left, text="Исходный", variable=self.file_target,
                       value="orig", bg="#f0f0f0").pack(anchor="w")
        tk.Radiobutton(left, text="sorted.txt", variable=self.file_target,
                       value="sort", bg="#f0f0f0").pack(anchor="w")

        tk.Label(left, text="Начать со строки:", bg="#f0f0f0").pack(anchor="w")
        self.start_line_entry = tk.Entry(left)
        self.start_line_entry.insert(0, "0")
        self.start_line_entry.pack(fill="x", pady=2)

        tk.Label(left, text="Количество строк (до 1000):", bg="#f0f0f0").pack(anchor="w")
        self.count_line_entry = tk.Entry(left)
        self.count_line_entry.insert(0, "10")
        self.count_line_entry.pack(fill="x", pady=2)

        self.display_button = tk.Button(left, text="Отобразить", command=self.display_content)
        self.display_button.pack(fill="x", pady=5)
        self.verify_button = tk.Button(left, text="Проверить сортировку", command=self.start_verify)
        self.verify_button.pack(fill="x", pady=2)

        self.output = tk.Text(right, width=100, wrap="none", state="disabled",
                              font=("Courier New", 10))
        scroll_y = tk.Scrollbar(right, orient="vertical", command=self.output.yview)
        scroll_x = tk.Scrollbar(right, orient="horizontal", command=self.output.xview)
        self.output.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.output.pack(side="left", fill="both", expand=True)

    @staticmethod
    def validate_size(value: str) -> bool:
        if value == "":
            return True
        try:
            return 1 <= int(value) <= 4096
        except ValueError:
            return False

    # ------------------------------------------------------------------
    # Потокобезопасные обновления UI
    # ------------------------------------------------------------------
    def _post(self, function, *args):
        self.events.put((function, args))

    def _process_events(self):
        while True:
            try:
                function, args = self.events.get_nowait()
            except queue.Empty:
                break
            try:
                function(*args)
            except Exception as exc:  # не даём очереди остановиться из-за одного события
                messagebox.showerror("Ошибка интерфейса", str(exc))
        self.after(100, self._process_events)

    def _cpp_progress(self, value):
        self._post(self.set_progress, float(value))

    def _cpp_timing(self, raw):
        self._post(self.log, raw.decode("utf-8", errors="replace"))

    def py_progress(self, value):
        self._post(self.set_progress, float(value))

    def py_timing(self, text):
        self._post(self.log, str(text))

    def set_progress(self, value):
        percent = max(0.0, min(100.0, float(value) * 100.0))
        self.progress["value"] = percent
        self.progress_label.config(text=f"{percent:.1f} %")

    def log(self, text):
        self.output.config(state="normal")
        self.output.insert(tk.END, str(text))
        self.output.see(tk.END)
        self.output.config(state="disabled")

    def set_busy(self, busy: bool):
        state = "disabled" if busy else "normal"
        for button in (
            self.choose_button,
            self.gen_button,
            self.sort_button,
            self.display_button,
            self.verify_button,
        ):
            button.config(state=state)

    def show_info(self, title, message):
        messagebox.showinfo(title, message)

    def show_error(self, title, message):
        messagebox.showerror(title, message)

    # ------------------------------------------------------------------
    # Загрузка DLL и служебные операции
    # ------------------------------------------------------------------
    def _load_dll(self):
        dll_path = os.path.join(BASE_DIR, "external_sort.dll")
        if not os.path.exists(dll_path):
            self.dll_error = f"DLL не найдена: {dll_path}"
            self.log("[C++] " + self.dll_error + "\nДоступна только Python-версия.\n")
            self.mod_combo.config(values=("Python",))
            self.mod_combo.current(0)
            return

        try:
            dll = ctypes.CDLL(dll_path)
            dll.external_sort_ex.argtypes = [
                ctypes.c_char_p,
                ctypes.c_int,
                ctypes.c_bool,
                PROGRESS_CB,
                TIMING_CB,
            ]
            dll.external_sort_ex.restype = ctypes.c_bool
            self.dll = dll
            self.log("[C++] Модуль external_sort.dll загружен.\n")
        except Exception as exc:
            self.dll_error = str(exc)
            self.log(f"[C++] Не удалось загрузить DLL: {exc}\nДоступна только Python-версия.\n")
            self.mod_combo.config(values=("Python",))
            self.mod_combo.current(0)

    def _set_path(self, path):
        path = os.path.abspath(path)
        self.file_path.set(path)
        self.file_info.set(path)
        self.log(f"Выбран файл: {path}\n")
        threading.Thread(target=self._count_worker, args=(path,), daemon=True).start()

    def _count_worker(self, path):
        try:
            size = os.path.getsize(path)
            with open(path, "r", encoding="utf-8", newline="") as file:
                lines = sum(1 for _ in file)
        except Exception as exc:
            self._post(self.log, f"Не удалось получить информацию о файле: {exc}\n")
            return
        self._post(
            self.file_info.set,
            f"{path}\nСтрок: {lines:,} | Размер: {size / (1024 ** 2):.1f} МиБ",
        )

    def choose_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if path:
            self._set_path(path)

    # ------------------------------------------------------------------
    # Генерация
    # ------------------------------------------------------------------
    def start_generate(self):
        if generate is None:
            self.show_error("Ошибка", "Модуль generate не найден")
            return
        path = self.file_path.get().strip()
        if not path:
            self.show_error("Ошибка", "Укажите путь к data.csv")
            return
        try:
            size_mb = int(self.size_entry.get())
        except ValueError:
            self.show_error("Ошибка", "Введите корректный размер в МиБ")
            return
        if size_mb <= 0:
            self.show_error("Ошибка", "Размер должен быть положительным")
            return

        self.set_busy(True)
        self.set_progress(0)
        note = " (менее 1 ГБ)" if size_mb <= 1024 else ""
        self.log(f"Генерация: {size_mb} МиБ{note} -> {path}\n")
        threading.Thread(
            target=self._generate_worker,
            args=(path, size_mb * 1024 * 1024),
            daemon=True,
        ).start()

    def _generate_worker(self, path, target_bytes):
        try:
            written = generate.generate(path, target_bytes, self.py_progress)
            self._post(self.log, f"Генерация завершена: {written:,} байт\n")
            self._count_worker(path)
            self._post(
                self.show_info,
                "Готово",
                f"data.csv создан.\nРазмер: {written:,} байт",
            )
        except Exception as exc:
            self._post(self.log, f"Ошибка генерации: {exc}\n")
            self._post(self.show_error, "Ошибка генерации", str(exc))
        finally:
            self._post(self.set_busy, False)

    # ------------------------------------------------------------------
    # Сортировка
    # ------------------------------------------------------------------
    def start_sort(self):
        path = self.file_path.get().strip()
        if not os.path.isfile(path):
            self.show_error("Ошибка", "Файл не найден")
            return

        try:
            with open(path, "rb") as file:
                file.seek(-1, os.SEEK_END)
                if file.read(1) != b"\n":
                    self.show_error("Ошибка", "Файл должен заканчиваться переводом строки LF")
                    return
        except OSError as exc:
            self.show_error("Ошибка доступа", str(exc))
            return

        module = self.mod_combo.get()
        if module == "C++" and self.dll is None:
            self.show_error("Ошибка", f"Модуль C++ недоступен:\n{self.dll_error}")
            return
        if module == "Python" and py_sort is None:
            self.show_error("Ошибка", "Модуль Python недоступен")
            return

        key_index = self.key_combo.current()
        if key_index < 0:
            self.show_error("Ошибка", "Выберите ключ сортировки")
            return
        ascending = self.dir_combo.current() == 1

        self.set_busy(True)
        self.set_progress(0)
        self.log(
            f"Сортировка ({module}): ключ «{self.key_combo.get()}», "
            f"направление «{self.dir_combo.get()}»\n"
        )
        threading.Thread(
            target=self._sort_worker,
            args=(module, path, key_index, ascending),
            daemon=True,
        ).start()

    def _sort_worker(self, module, path, key_index, ascending):
        success = False
        try:
            if module == "C++":
                success = bool(
                    self.dll.external_sort_ex(
                        path.encode("utf-8"),
                        key_index,
                        ascending,
                        self._progress_cb,
                        self._timing_cb,
                    )
                )
            else:
                success = bool(
                    py_sort.external_sort(
                        path,
                        key_index,
                        ascending,
                        self.py_progress,
                        self.py_timing,
                    )
                )
        except Exception as exc:
            self._post(self.log, f"Ошибка сортировки: {exc}\n")

        output = os.path.join(os.path.dirname(os.path.abspath(path)), "sorted.txt")
        if success and os.path.isfile(output):
            self._post(self.log, f"Готово: {output}\n")
            self._post(self.show_info, "Успех", "Сортировка завершена.\nРезультат: sorted.txt")
        else:
            self._post(self.show_error, "Ошибка", "Сортировка не выполнена. См. лог.")
        self._post(self.set_busy, False)

    # ------------------------------------------------------------------
    # Просмотр и проверка
    # ------------------------------------------------------------------
    def _target_path(self):
        base = self.file_path.get().strip()
        if not base:
            return ""
        if self.file_target.get() == "orig":
            return base
        return os.path.join(os.path.dirname(os.path.abspath(base)), "sorted.txt")

    def display_content(self):
        target = self._target_path()
        if not target or not os.path.isfile(target):
            self.show_error("Ошибка", "Файл для отображения не найден")
            return
        try:
            start = max(0, int(self.start_line_entry.get()))
            count = max(1, min(1000, int(self.count_line_entry.get())))
        except ValueError:
            self.show_error("Ошибка", "Введите корректные числа")
            return

        self.log(f"--- {target}, строки {start}..{start + count - 1} ---\n")
        try:
            with open(target, "r", encoding="utf-8", newline="") as file:
                rows = itertools.islice(csv.reader(file), start, start + count)
                for row in rows:
                    self.log(", ".join(row) + "\n")
        except OSError as exc:
            self.show_error("Ошибка", str(exc))

    def start_verify(self):
        base = self.file_path.get().strip()
        if not base:
            self.show_error("Ошибка", "Сначала выберите файл")
            return
        target = os.path.join(os.path.dirname(os.path.abspath(base)), "sorted.txt")
        if not os.path.isfile(target):
            self.show_error("Ошибка", "Сначала выполните сортировку")
            return
        key_index = self.key_combo.current()
        ascending = self.dir_combo.current() == 1
        self.set_busy(True)
        self.log(f"Проверка порядка в {target}\n")
        threading.Thread(
            target=self._verify_worker,
            args=(target, key_index, ascending),
            daemon=True,
        ).start()

    def _verify_worker(self, target, key_index, ascending):
        previous = None
        checked = 0
        problem = None
        try:
            with open(target, "r", encoding="utf-8", newline="") as file:
                for line_number, row in enumerate(csv.reader(file), start=1):
                    if not row or not any(cell != "" for cell in row):
                        continue
                    key_value = py_sort.sort_key(py_sort.normalize_row(row), key_index)
                    if previous is not None:
                        if ascending and key_value < previous:
                            problem = f"Строка {line_number}: {key_value} < {previous}"
                            break
                        if not ascending and key_value > previous:
                            problem = f"Строка {line_number}: {key_value} > {previous}"
                            break
                    previous = key_value
                    checked += 1
        except Exception as exc:
            self._post(self.log, f"Ошибка проверки: {exc}\n")
            self._post(self.show_error, "Ошибка проверки", str(exc))
        else:
            if problem is None:
                self._post(
                    self.log,
                    f"Проверка пройдена: {checked:,} строк расположены по выбранному ключу.\n",
                )
                self._post(self.show_info, "Проверка", "Порядок сортировки корректен")
            else:
                self._post(self.log, f"Проверка не пройдена: {problem}\n")
                self._post(self.show_error, "Проверка", problem)
        finally:
            self._post(self.set_busy, False)


if __name__ == "__main__":
    app = App()
    app.mainloop()
