import sys
import time
import threading
import ctypes
from datetime import date, datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from PIL import ImageGrab

from database import Database
from models import GameItem, Review
from repositories import GameRepository, ReviewRepository


class ReviewApp(tk.Tk):
    """Главное окно графического приложения для работы с таблицей отзывов (lab_schema.review)."""

    def __init__(self):
        super().__init__()
        self.title("Управление базой данных «Отзывы на видеоигры»")
        self.geometry("830x520")
        self.resizable(False, False)

        db = Database()
        self._game_repo = GameRepository(db)
        self._review_repo = ReviewRepository(db)

        self._games_map = {}
        self._current_review_id = None

        self._init_ui()
        self.load_games()
        self.load_reviews()

    def _init_ui(self):
        # 1. Блок фильтрации
        self.grp_filter = ttk.LabelFrame(self, text="Настройка выборки (фильтрация)", padding=10)
        self.grp_filter.pack(fill=tk.X, padx=12, pady=(10, 6))

        ttk.Label(self.grp_filter, text="Автор отзыва содержит:").pack(side=tk.LEFT, padx=(0, 8))
        self.ent_filter = ttk.Entry(self.grp_filter, width=42)
        self.ent_filter.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_filter = ttk.Button(self.grp_filter, text="Применить", width=16, command=self.on_filter)
        self.btn_filter.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_reset = ttk.Button(self.grp_filter, text="Сбросить", width=16, command=self.on_reset_filter)
        self.btn_reset.pack(side=tk.LEFT)

        # 2. Таблица Treeview
        table_frame = ttk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)

        columns = ("id", "game", "reviewer", "score", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse", height=11)

        self.tree.heading("id", text="ID")
        self.tree.heading("game", text="Игра")
        self.tree.heading("reviewer", text="Автор отзыва")
        self.tree.heading("score", text="Оценка")
        self.tree.heading("date", text="Дата отзыва")

        self.tree.column("id", width=55, anchor=tk.CENTER)
        self.tree.column("game", width=230, anchor=tk.W)
        self.tree.column("reviewer", width=200, anchor=tk.W)
        self.tree.column("score", width=110, anchor=tk.CENTER)
        self.tree.column("date", width=160, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # 3. Блок добавления и редактирования записи
        self.grp_edit = ttk.LabelFrame(self, text="Добавление и редактирование записи", padding=10)
        self.grp_edit.pack(fill=tk.X, padx=12, pady=(6, 12))

        form_grid = ttk.Frame(self.grp_edit)
        form_grid.pack(fill=tk.X, pady=(0, 10))

        # Игра (внешний ключ из родительской таблицы)
        ttk.Label(form_grid, text="Игра:").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        self.cmb_game = ttk.Combobox(form_grid, state="readonly", width=30)
        self.cmb_game.grid(row=0, column=1, sticky=tk.W, padx=(0, 28), pady=4)

        # Автор отзыва
        ttk.Label(form_grid, text="Автор отзыва:").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=4)
        self.ent_reviewer = ttk.Entry(form_grid, width=33)
        self.ent_reviewer.grid(row=1, column=1, sticky=tk.W, padx=(0, 28), pady=4)

        # Оценка
        ttk.Label(form_grid, text="Оценка (1–10):").grid(row=0, column=2, sticky=tk.W, padx=(0, 8), pady=4)
        self.ent_score = ttk.Entry(form_grid, width=18)
        self.ent_score.grid(row=0, column=3, sticky=tk.W, pady=4)
        self.ent_score.bind("<KeyPress>", self.on_numeric_keypress)

        # Дата отзыва (календарь)
        ttk.Label(form_grid, text="Дата отзыва:").grid(row=1, column=2, sticky=tk.W, padx=(0, 8), pady=4)
        self.cal_date = DateEntry(
            form_grid,
            width=16,
            date_pattern="yyyy-mm-dd",
            background="darkblue",
            foreground="white",
            borderwidth=2,
        )
        self.cal_date.grid(row=1, column=3, sticky=tk.W, pady=4)

        # Кнопки действий
        btn_frame = ttk.Frame(self.grp_edit)
        btn_frame.pack(fill=tk.X)

        self.btn_add = ttk.Button(btn_frame, text="Добавить запись", width=20, command=self.on_add)
        self.btn_add.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_update = ttk.Button(btn_frame, text="Изменить запись", width=20, command=self.on_update)
        self.btn_update.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_delete = ttk.Button(btn_frame, text="Удалить выбранную строку", width=25, command=self.on_delete)
        self.btn_delete.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_clear = ttk.Button(btn_frame, text="Очистить поля", width=18, command=self.clear_fields)
        self.btn_clear.pack(side=tk.LEFT)

    def load_games(self):
        """Загрузка списка игр из родительской таблицы в выпадающий список."""
        try:
            games = self._game_repo.get_all()
            self._games_map = {g.title: g.id for g in games}
            self.cmb_game["values"] = [g.title for g in games]
        except Exception as ex:
            messagebox.showerror("Ошибка", f"Ошибка загрузки списка игр: {ex}", parent=self)

    def load_reviews(self, filter_pattern: str = None):
        """Загрузка отзывов в таблицу Treeview."""
        try:
            reviews = (
                self._review_repo.get_all()
                if not filter_pattern
                else self._review_repo.filter_by_reviewer(filter_pattern)
            )
            for item in self.tree.get_children():
                self.tree.delete(item)
            for r in reviews:
                date_str = r.review_date.strftime("%Y-%m-%d") if isinstance(r.review_date, (date, datetime)) else str(r.review_date)
                self.tree.insert("", tk.END, values=(r.id, r.game_title, r.reviewer_name, r.score, date_str))
        except Exception as ex:
            messagebox.showerror("Ошибка", f"Ошибка загрузки отзывов: {ex}", parent=self)

    def on_numeric_keypress(self, event):
        """Запрет ввода отрицательных значений (символа минус)."""
        if event.char == "-":
            messagebox.showwarning("Ограничение ввода", "Ввод отрицательных значений запрещён!", parent=self)
            return "break"

    def validate_input(self):
        """Проверка корректности введённых данных."""
        game_title = self.cmb_game.get().strip()
        if not game_title or game_title not in self._games_map:
            messagebox.showwarning("Ошибка ввода", "Выберите игру из выпадающего списка!", parent=self)
            return None

        reviewer = self.ent_reviewer.get().strip()
        if not reviewer:
            messagebox.showwarning("Ошибка ввода", "Введите имя автора отзыва!", parent=self)
            return None

        raw_score = self.ent_score.get().strip()
        try:
            score = int(raw_score)
        except ValueError:
            messagebox.showwarning("Ошибка ввода", "Оценка должна быть целым числом!", parent=self)
            return None

        if score < 0:
            messagebox.showwarning("Ошибка ввода", "Оценка не может быть отрицательной!", parent=self)
            return None

        if score < 1 or score > 10:
            messagebox.showwarning("Ошибка ввода", "Оценка должна находиться в диапазоне от 1 до 10!", parent=self)
            return None

        review_date = self.cal_date.get_date()
        return self._games_map[game_title], game_title, reviewer, score, review_date

    def on_add(self):
        """Добавление новой записи."""
        validated = self.validate_input()
        if not validated:
            return
        game_id, game_title, reviewer, score, review_date = validated

        try:
            if self._review_repo.exists(game_id, reviewer, None):
                messagebox.showwarning(
                    "Дублирование данных",
                    f"Отзыв от автора «{reviewer}» на игру «{game_title}» уже существует в базе данных! "
                    "Запись данных в таблицу не выполнена.",
                    parent=self,
                )
                return

            new_review = Review(
                id=None,
                game_id=game_id,
                game_title=game_title,
                reviewer_name=reviewer,
                score=score,
                review_date=review_date,
            )
            self._review_repo.save(new_review)
            messagebox.showinfo("Успех", "Отзыв успешно добавлен в таблицу!", parent=self)
            self.clear_fields()
            self.load_reviews()
        except Exception as ex:
            messagebox.showerror("Ошибка добавления", str(ex), parent=self)

    def on_update(self):
        """Изменение выбранной записи."""
        if self._current_review_id is None:
            messagebox.showwarning("Предупреждение", "Выберите запись в таблице для изменения!", parent=self)
            return

        validated = self.validate_input()
        if not validated:
            return
        game_id, game_title, reviewer, score, review_date = validated

        try:
            if self._review_repo.exists(game_id, reviewer, self._current_review_id):
                messagebox.showwarning(
                    "Дублирование данных",
                    f"Другой отзыв от автора «{reviewer}» на игру «{game_title}» уже существует! "
                    "Изменение не сохранено.",
                    parent=self,
                )
                return

            updated = Review(
                id=self._current_review_id,
                game_id=game_id,
                game_title=game_title,
                reviewer_name=reviewer,
                score=score,
                review_date=review_date,
            )
            self._review_repo.save(updated)
            messagebox.showinfo("Успех", "Данные отзыва успешно изменены!", parent=self)
            self.clear_fields()
            self.load_reviews()
        except Exception as ex:
            messagebox.showerror("Ошибка изменения", str(ex), parent=self)

    def on_delete(self):
        """Удаление выбранной записи при подтверждении Да/Нет."""
        if self._current_review_id is None:
            messagebox.showwarning("Предупреждение", "Выберите запись в таблице для удаления!", parent=self)
            return

        confirmed = messagebox.askyesno(
            "Подтверждение удаления",
            "Вы действительно уверены, что хотите удалить выбранную запись?",
            parent=self,
        )
        if confirmed:
            try:
                self._review_repo.delete(self._current_review_id)
                messagebox.showinfo("Успех", "Запись успешно удалена!", parent=self)
                self.clear_fields()
                self.load_reviews()
            except Exception as ex:
                messagebox.showerror("Ошибка удаления", str(ex), parent=self)

    def on_filter(self):
        """Применение регистронезависимого фильтра через запрос к БД."""
        pattern = self.ent_filter.get().strip()
        self.load_reviews(pattern if pattern else None)

    def on_reset_filter(self):
        """Сброс фильтра."""
        self.ent_filter.delete(0, tk.END)
        self.load_reviews()

    def on_tree_select(self, _event=None):
        """Заполнение полей ввода при выборе строки в таблице."""
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        if not values:
            return
        self._current_review_id = int(values[0])
        self.cmb_game.set(values[1])

        self.ent_reviewer.delete(0, tk.END)
        self.ent_reviewer.insert(0, values[2])

        self.ent_score.delete(0, tk.END)
        self.ent_score.insert(0, str(values[3]))

        try:
            dt = datetime.strptime(str(values[4]), "%Y-%m-%d").date()
            self.cal_date.set_date(dt)
        except ValueError:
            pass

    def select_row_by_index(self, idx: int):
        children = self.tree.get_children()
        if 0 <= idx < len(children):
            item_id = children[idx]
            self.tree.selection_set(item_id)
            self.tree.see(item_id)
            self.on_tree_select()

    def clear_fields(self):
        """Очистка полей ввода."""
        self._current_review_id = None
        self.tree.selection_remove(self.tree.selection())
        self.cmb_game.set("")
        self.ent_reviewer.delete(0, tk.END)
        self.ent_score.delete(0, tk.END)
        self.cal_date.set_date(date.today())


def _get_window_bbox(app: ReviewApp):
    app.update_idletasks()
    app.update()
    x = app.winfo_rootx() - 8
    y = app.winfo_rooty() - 31
    w = app.winfo_width() + 16
    h = app.winfo_height() + 39
    return (x, y, x + w, y + h)


def _capture_window(app: ReviewApp, filename: str):
    bbox = _get_window_bbox(app)
    img = ImageGrab.grab(bbox=bbox)
    img.save(filename)


def _press_enter():
    VK_RETURN = 0x0D
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 0, 0)
    ctypes.windll.user32.keybd_event(VK_RETURN, 0, 2, 0)


def _capture_with_dialog(app: ReviewApp, filename: str, action, extra_enter: bool = False):
    bbox = _get_window_bbox(app)

    def worker():
        time.sleep(0.55)
        ImageGrab.grab(bbox=bbox).save(filename)
        time.sleep(0.1)
        _press_enter()
        if extra_enter:
            time.sleep(0.45)
            _press_enter()

    threading.Thread(target=worker, daemon=True).start()
    action()


def run_screenshots():
    app = ReviewApp()
    app.attributes("-topmost", True)
    app.update_idletasks()
    # Центрируем окно
    sw = app.winfo_screenwidth()
    sh = app.winfo_screenheight()
    x = (sw - 830) // 2
    y = (sh - 520) // 2
    app.geometry(f"830x520+{x}+{y}")
    app.deiconify()
    app.lift()
    app.focus_force()
    app.update()
    time.sleep(0.5)

    # 1. Главное окно приложения с данными и выбором строки
    app.select_row_by_index(2)  # Builder228 - Minecraft
    app.update()
    time.sleep(0.25)
    _capture_window(app, "s1.png")

    # 2. Ввод даты с помощью выпадающего календаря (DateEntry)
    app.clear_fields()
    app.update()
    app.cmb_game.set("Elden Ring")
    app.ent_reviewer.insert(0, "TarnishedHero")
    app.ent_score.insert(0, "10")
    app.cal_date.set_date(date(2025, 2, 20))
    app.update()
    app.cal_date.drop_down()
    app.update()
    cx = app.cal_date.winfo_rootx()
    cy = app.cal_date.winfo_rooty() - app.cal_date._top_cal.winfo_reqheight() - 4
    app.cal_date._top_cal.geometry(f"+{cx}+{cy}")
    app.update()
    time.sleep(0.35)
    _capture_window(app, "s8.png")
    app.cal_date._top_cal.withdraw()
    app.update()
    time.sleep(0.15)

    # 3. Добавление новой записи (выбор игры из списка и даты из календаря)
    _capture_with_dialog(app, "s2.png", app.on_add)
    app.update()
    time.sleep(0.2)

    # 4. Попытка повторного ввода уже имеющихся данных (дубликат)
    app.cmb_game.set("Elden Ring")
    app.ent_reviewer.insert(0, "TarnishedHero")
    app.ent_score.insert(0, "10")
    app.cal_date.set_date(date(2025, 2, 20))
    app.update()
    _capture_with_dialog(app, "s3.png", app.on_add)
    app.update()

    # 5. Запрет ввода отрицательного значения оценки
    app.ent_score.delete(0, tk.END)
    app.ent_score.insert(0, "-5")
    app.update()
    _capture_with_dialog(app, "s4.png", app.validate_input)
    app.update()

    # 6. Изменение записи
    children = app.tree.get_children()
    app.select_row_by_index(len(children) - 1)
    app.update()
    time.sleep(0.15)
    app.ent_score.delete(0, tk.END)
    app.ent_score.insert(0, "9")
    app.update()
    _capture_with_dialog(app, "s5.png", app.on_update)
    app.update()

    # 7. Регистронезависимая фильтрация по автору (ввод в нижнем регистре)
    app.ent_filter.delete(0, tk.END)
    app.ent_filter.insert(0, "indie")
    app.on_filter()
    app.select_row_by_index(0)
    app.update()
    time.sleep(0.25)
    _capture_window(app, "s6.png")

    # 8. Подтверждение удаления записи (Да/Нет) и очистка тестовой строки
    app.on_reset_filter()
    app.update()
    children = app.tree.get_children()
    app.select_row_by_index(len(children) - 1)
    app.update()
    time.sleep(0.15)
    _capture_with_dialog(app, "s7.png", app.on_delete, extra_enter=True)
    app.update()

    app.destroy()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--screenshots":
        run_screenshots()
    else:
        app = ReviewApp()
        app.mainloop()
