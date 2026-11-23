import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import math
import random as rand
import os

def get_points_in_circle(cx, cy, r):
    points = []
    r_sq = r * r
    for x in range(math.floor(cx - r), math.floor(cx + r) + 1):
        dx = x - cx
        dy_sq = r_sq - dx * dx
        if dy_sq >= 0:
            dy = math.sqrt(dy_sq)
            for y in range(math.floor(cy - dy), math.floor(cy + dy) + 1):
                points.append((x, y))
    return points

def draw_star(canvas, x, y, size=5, color="black"):
    canvas.create_line(x - size, y, x + size, y, fill=color, width=1)
    canvas.create_line(x, y - size, x, y + size, fill=color, width=1)
    canvas.create_line(x - size//1.5, y - size//1.5, x + size//1.5, y + size//1.5, fill=color, width=1)
    canvas.create_line(x - size//1.5, y + size//1.5, x + size//1.5, y - size//1.5, fill=color, width=1)

def lighten_color(color):
    """Светлый оттенок цвета для заливки завершённой окружности."""
    r, g, b = root.winfo_rgb(color)
    return "#%02x%02x%02x" % (
        round(r / 257 * 0.35 + 255 * 0.65),
        round(g / 257 * 0.35 + 255 * 0.65),
        round(b / 257 * 0.35 + 255 * 0.65),
    )

# ==================== ОСНОВНЫЕ ДАННЫЕ ====================
AVAILABLE_COLORS = [
    ("Голубой", "cyan"),
    ("Желтый", "yellow"),
    ("Зеленый", "green"),
    ("Коричневый", "brown"),
    ("Красный", "red"),
    ("Оранжевый", "orange"),
    ("Розовый", "pink"),
    ("Синий", "blue"),
    ("Фиолетовый", "purple"),
]
INITIAL_COLORS = ["red", "blue", "green", "purple", "orange"]
circle_colors = INITIAL_COLORS.copy()
RADIUS = 100
circles_coords = []
all_coords = []
current_file_path = None

try:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    APP_DIR = os.getcwd()

root = tk.Tk()
root.title("5 окружностей - случайные точки")
root.geometry("900x700")
root.resizable(False, False)
menubar = tk.Menu(root)

# ==================== КАСТОМНОЕ ОКНО ОШИБКИ ====================
error_counts = {
    "not_digit": 0,
    "zero_start": 0,
    "leading_zero_removed": 0,
    "max_speed": 0,
}

def show_speed_error(title, message, error_type):
    global error_counts
    error_counts[error_type] += 1
    
    count = error_counts[error_type]
    if count == 1:
        delay = 2000
    elif count == 2:
        delay = 1000
    else:
        delay = 500
        
    dialog = tk.Toplevel(root)
    dialog.title(title)
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.attributes('-topmost', True)
    
    tk.Label(dialog, text=message, padx=20, pady=20, font=("Arial", 10), fg="red").pack()
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")
    
    dialog.after(delay, lambda: dialog.destroy() if dialog.winfo_exists() else None)

# ==================== ФАЙЛ ====================
file_menu = tk.Menu(menubar, tearoff=0)

def save_colors_to_file(filepath):
    try:
        color_names = [c[0] for c in AVAILABLE_COLORS]
        color_values = [c[1] for c in AVAILABLE_COLORS]
        with open(filepath, "w", encoding="utf-8") as f:
            for color_val in circle_colors:
                idx = color_values.index(color_val) if color_val in color_values else 0
                f.write(color_names[idx] + "\n")
        return True
    except Exception as e:
        messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить файл:\n{e}")
        return False

def load_colors_from_file(filepath):
    global circle_colors
    try:
        color_names = [c[0] for c in AVAILABLE_COLORS]
        color_values = [c[1] for c in AVAILABLE_COLORS]
        with open(filepath, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        if len(lines) != 5:
            messagebox.showerror(
                "Ошибка загрузки",
                f"Файл должен содержать ровно 5 названий цветов.\n"
                f"Найдено строк: {len(lines)}"
            )
            return False
            
        new_colors = []
        for name in lines:
            if name not in color_names:
                messagebox.showerror(
                    "Ошибка загрузки",
                    f"Неизвестный цвет: «{name}».\n"
                    f"Проверьте правильность написания."
                )
                return False
            new_colors.append(color_values[color_names.index(name)])
            
        if len(set(new_colors)) != 5:
            messagebox.showerror(
                "Ошибка загрузки",
                "Цвет уже используется"
            )
            return False
            
        circle_colors = new_colors
        canvas.delete("all")
        draw_initial_scene()
        return True
    except Exception as e:
        messagebox.showerror("Ошибка загрузки", f"Не удалось прочитать файл:\n{e}")
        return False

def open_file():
    global current_file_path
    filepath = filedialog.askopenfilename(
        initialdir=APP_DIR,
        filetypes=[("Text files", ".txt"), ("All files", ".*")]
    )
    if filepath:
        if load_colors_from_file(filepath):
            current_file_path = filepath
            messagebox.showinfo("Файл открыт", f"Цвета загружены из файла:\n{filepath}")

def save_file():
    global current_file_path
    if current_file_path:
        if save_colors_to_file(current_file_path):
            messagebox.showinfo("Сохранить", f"Текущие цвета сохранены в:\n{current_file_path}")
    else:
        save_as_file()

def save_as_file():
    global current_file_path
    filepath = filedialog.asksaveasfilename(
        initialdir=APP_DIR,
        defaultextension=".txt",
        filetypes=[("Text files", ".txt"), ("All files", ".*")]
    )
    if filepath:
        if save_colors_to_file(filepath):
            current_file_path = filepath
            messagebox.showinfo("Сохранить как", f"Текущие цвета сохранены в:\n{filepath}")

file_menu.add_command(label="Открыть", command=open_file)
file_menu.add_command(label="Сохранить", command=save_as_file)
menubar.add_cascade(label="Файл", menu=file_menu)

# ==================== НАСТРОЙКИ ====================
settings_menu = tk.Menu(menubar, tearoff=0)

def open_color_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Выбор цветов окружностей")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()
    
    color_names = [c[0] for c in AVAILABLE_COLORS]
    color_values = [c[1] for c in AVAILABLE_COLORS]
    vars_list = []
    squares = []
    comboboxes = []
    last_valid_colors = []
    
    for color_val in circle_colors:
        idx = color_values.index(color_val) if color_val in color_values else 0
        last_valid_colors.append(color_names[idx])
        
    main_frame = tk.Frame(dialog, padx=15, pady=15)
    main_frame.pack()
    
    tk.Label(main_frame, text="Выберите цвет для каждой окружности:",
             font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=3, pady=(0, 10))
             
    def on_color_change(event, index):
        selected_name = vars_list[index].get()
        if selected_name not in color_names:
            return
            
        current_selections = [v.get() for v in vars_list]
        current_selections[index] = selected_name
        
        if current_selections.count(selected_name) > 1:
            messagebox.showerror(
                "Ошибка",
                "Этот цвет уже выбран",
                parent=dialog
            )
            vars_list[index].set(last_valid_colors[index])
            old_val = color_values[color_names.index(last_valid_colors[index])]
            squares[index].config(bg=old_val)
        else:
            last_valid_colors[index] = selected_name
            new_val = color_values[color_names.index(selected_name)]
            squares[index].config(bg=new_val)
            
    for i in range(5):
        tk.Label(main_frame, text=f"Окружность {i+1}:", width=15, anchor="w").grid(
            row=i+1, column=0, padx=5, pady=3, sticky="w")
            
        current_color = circle_colors[i]
        current_idx = color_values.index(current_color) if current_color in color_values else 0
        var = tk.StringVar(value=color_names[current_idx])
        vars_list.append(var)
        
        combo = ttk.Combobox(main_frame, textvariable=var, values=color_names, 
                            state="readonly", width=15, height=len(color_names))
        combo.grid(row=i+1, column=1, padx=5, pady=3, sticky="ew")
        combo.bind("<<ComboboxSelected>>", lambda e, idx=i: on_color_change(e, idx))
        comboboxes.append(combo)
        
        sq = tk.Canvas(main_frame, width=20, height=20, bg=current_color, 
                       highlightthickness=1, highlightbackground="black")
        sq.grid(row=i+1, column=2, padx=5, pady=3)
        squares.append(sq)
        
    btn_frame = tk.Frame(main_frame)
    btn_frame.grid(row=6, column=0, columnspan=3, pady=(15, 0))
    
    def on_cancel(): dialog.destroy()
    
    def on_random():
        available = list(color_names)
        rand.shuffle(available)
        for i in range(5):
            vars_list[i].set(available[i])
            last_valid_colors[i] = available[i]
            val = color_values[color_names.index(available[i])]
            squares[i].config(bg=val)
            
    def on_ok():
        global circle_colors
        selected_colors = [color_values[color_names.index(v.get())] for v in vars_list]
        circle_colors = selected_colors
        canvas.delete("all")
        draw_initial_scene()
        dialog.destroy()
        
    tk.Button(btn_frame, text="Отмена", width=10, command=on_cancel).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Случайно", width=10, command=on_random).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="ОК", width=10, command=on_ok).pack(side=tk.LEFT, padx=5)
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
    y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
    dialog.geometry(f"+{x}+{y}")

settings_menu.add_command(label="Цвет", command=open_color_dialog)
menubar.add_cascade(label="Настройки", menu=settings_menu)

SETTINGS_MENU_INDEX = menubar.index("end")

# ==================== ПОМОЩЬ ====================
help_menu = tk.Menu(menubar, tearoff=0)

def about_program():
    messagebox.showinfo(
        "О программе",
        "5 окружностей — случайные точки\n\n"
        "====================================================================\n"
        "КАК ПОЛЬЗОВАТЬСЯ ПРОГРАММОЙ\n"
        "====================================================================\n\n"
        "Перед вами — небольшая игра-наблюдение: на экране появляются 5 цветных окружностей, "
        "а программа «бросает» в них случайные точки-звёздочки. Побеждает та окружность, "
        "которая первой наберёт 10 звёздочек — она займёт 1-е место, вторая — 2-е и так далее.\n\n"
        "--------------------------------------------------------------------\n"
        "КНОПКИ СПРАВА\n"
        "--------------------------------------------------------------------\n\n"
        "• Старт — запускает бросание точек; повторное нажатие превращает кнопку в «Стоп» "
        "и полностью сбрасывает игру.\n"
        "• Пауза — временно останавливает игру, не сбрасывая результаты; повторное нажатие "
        "«Продолжить» возобновляет её. Нажать «Пауза» можно и до старта — тогда после «Старт» "
        "программа сразу встанет на паузу, и потребуется нажать «Продолжить». Сама по себе "
        "кнопка «Продолжить» до старта ничего не делает — сначала нужно нажать «Старт». "
        "После завершения кнопка переключается, но ничего не делает — для новой игры "
        "нажмите «Стоп».\n"
        "• Выход — закрывает программу.\n\n"
        "--------------------------------------------------------------------\n"
        "СКОРОСТЬ\n"
        "--------------------------------------------------------------------\n\n"
        "Под кнопками находится ползунок «Скорость»: чем больше число, тем быстрее летят точки. "
        "Значение можно двигать мышкой или вписать число от 0 до 100 вручную.\n\n"
        "--------------------------------------------------------------------\n"
        "ЦВЕТА ОКРУЖНОСТЕЙ\n"
        "--------------------------------------------------------------------\n\n"
        "В меню «Настройки -> Цвет» можно выбрать свой цвет для каждой окружности. Доступно "
        "9 основных цветов в алфавитном порядке. Справа от названия цвета в выпадающем списке "
        "виден квадратик с этим цветом — так проще понять, как он выглядит. Кнопка «Случайно» "
        "подберёт цвета за вас, а «ОК» сохранит выбор. Окружность, собравшая 10 звёздочек, "
        "заливается своим цветом.\n\n"
        "--------------------------------------------------------------------\n"
        "СОХРАНЕНИЕ И ЗАГРУЗКА\n"
        "--------------------------------------------------------------------\n\n"
        "В меню «Файл» можно сохранить текущие цвета в текстовый файл, чтобы потом загрузить "
        "их снова. Файл содержит 5 названий цветов — по одному на строку. Диалог выбора файла "
        "открывается сразу в папке с приложением.\n\n"
        "--------------------------------------------------------------------\n"
        "РАЗМЕР ОКНА\n"
        "--------------------------------------------------------------------\n\n"
        "Настройки окна заданы разработчиком: во время выполнения программы (включая "
        "завершённую) изменение размера блокируется до нажатия кнопки «Стоп».\n\n"
        "Приятного наблюдения! 🌟"
    )

def about_author():
    messagebox.showinfo(
        "Об авторе",
        "Студент Шубин Владислав Юрьевич\n"
        "Группа ИВТб-2303\n"
        "ВятГУ, 2026"
    )

help_menu.add_command(label="О программе", command=about_program)
help_menu.add_command(label="Об авторе", command=about_author)
menubar.add_cascade(label="Помощь", menu=help_menu)
root.config(menu=menubar)

# ==================== ОСНОВНОЙ КОНТЕЙНЕР ====================
main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
right_frame = tk.Frame(main_frame, width=180, bg='lightgray')
right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5, pady=5)
right_frame.pack_propagate(False)

# ==================== СОСТОЯНИЕ ====================
running = False
paused = False
finished = False
after_id = None
p = 1
s = [0, 0, 0, 0, 0]
counter_labels = []
ranking_labels = []
circle_oval_ids = []
current_delay = 50

# ==================== ДИНАМИЧЕСКОЕ МАСШТАБИРОВАНИЕ ====================
def update_layout(event=None):
    global circles_coords, all_coords, RADIUS
    w = canvas.winfo_width()
    h = canvas.winfo_height()
    if w < 50 or h < 50: return
    
    RADIUS = min(w, h) // 8 
    margin = RADIUS + 20
    circles_coords = [
        (margin, margin),
        (w - margin, margin),
        (margin, h - margin),
        (w - margin, h - margin),
        (w // 2, h // 2),
    ]
    all_coords = [get_points_in_circle(cx, cy, RADIUS) for cx, cy in circles_coords]
    
    # Перерисовываем сцену без сброса состояния
    canvas.delete("all")
    if circles_coords:
        draw_initial_scene()

canvas.bind("<Configure>", update_layout)

def draw_initial_scene():
    global counter_labels, ranking_labels, circle_oval_ids
    counter_labels = []
    ranking_labels = []
    circle_oval_ids = []
    
    for i, (cx, cy) in enumerate(circles_coords):
        oval_id = canvas.create_oval(cx - RADIUS, cy - RADIUS, cx + RADIUS, cy + RADIUS,
                                     outline=circle_colors[i], width=2)
        circle_oval_ids.append(oval_id)
        canvas.create_oval(cx - 3, cy - 3, cx + 3, cy + 3,
                           fill=circle_colors[i], outline=circle_colors[i])
                           
    for i, (cx, cy) in enumerate(circles_coords):
        label = canvas.create_text(cx, cy - 20, text="0/10",
                                   fill=circle_colors[i], font=("Arial", 10, "bold"))
        counter_labels.append(label)
        rank_label = canvas.create_text(cx, cy - 40, text="",
                                        fill=circle_colors[i], font=("Arial", 10, "bold"))
        ranking_labels.append(rank_label)

# ==================== ОСНОВНАЯ ЛОГИКА ====================
def generate_step():
    global running, paused, p, after_id, finished
    if not running or paused: return
    
    x = rand.randint(0, canvas.winfo_width() - 1)
    y = rand.randint(0, canvas.winfo_height() - 1)
    c = (x, y)
    hit = False
    
    for i in range(5):
        if c in all_coords[i]:
            if s[i] < 10:
                s[i] += 1
                draw_star(canvas, x, y, size=3, color=circle_colors[i])
                canvas.itemconfig(counter_labels[i], text=f"{s[i]}/10")
                if s[i] == 10:
                    canvas.itemconfig(circle_oval_ids[i], fill=lighten_color(circle_colors[i]))
                    canvas.itemconfig(ranking_labels[i], text=f"Место: {p}")
                    p += 1
                    if p == 6:
                        running = False
                        finished = True
                        if after_id is not None:
                            root.after_cancel(after_id)
                            after_id = None
                        # Блокируем меню "Настройки" после завершения программы
                        menubar.entryconfigure(SETTINGS_MENU_INDEX, state="disabled")
                        messagebox.showinfo("Завершено", "Программа завершена")
                        return
            else:
                draw_star(canvas, x, y, size=3, color="gray")
            hit = True
            break
            
    if not hit:
        draw_star(canvas, x, y, size=3, color="gray")
        
    root.update()
    after_id = root.after(current_delay, generate_step)

# ==================== УПРАВЛЕНИЕ ====================
def reset_state():
    global p, s, running, paused, finished, after_id, counter_labels, ranking_labels
    if after_id is not None:
        root.after_cancel(after_id)
        after_id = None
        
    running = False
    paused = False
    finished = False
    p = 1
    s = [0, 0, 0, 0, 0]
    
    canvas.delete("all")
    if circles_coords:
        draw_initial_scene()
        
    btn_start.config(text="Старт", command=start_program)
    btn_pause.config(text="Пауза", command=pause_program, state=tk.NORMAL)
    menubar.entryconfigure(SETTINGS_MENU_INDEX, state="normal")

def start_program():
    global running, paused, finished
    if finished: return
    
    running = True
    btn_start.config(text="Стоп", command=reset_state)
    menubar.entryconfigure(SETTINGS_MENU_INDEX, state="disabled")
    
    if not paused:
        btn_pause.config(text="Пауза", command=pause_program, state=tk.NORMAL)
        
    generate_step()

def pause_program():
    global paused
    paused = True
    btn_pause.config(text="Продолжить", command=resume_program)


def resume_program():
    global paused, after_id
    paused = False
    btn_pause.config(text="Пауза", command=pause_program)
    if running and not finished:
        if after_id is not None:
            root.after_cancel(after_id)
            after_id = None
        generate_step()
    
    paused = False
    btn_pause.config(text="Пауза", command=pause_program)
    generate_step()

def exit_program(): 
    root.destroy()

# ==================== КНОПКИ СПРАВА ====================
btn_start = tk.Button(right_frame, text="Старт", width=15, command=start_program)
btn_start.pack(pady=10, padx=5)
btn_pause = tk.Button(right_frame, text="Пауза", width=15, command=pause_program, state=tk.NORMAL)
btn_pause.pack(pady=10, padx=5)
btn_exit = tk.Button(right_frame, text="Выход", width=15, command=exit_program)
btn_exit.pack(pady=10, padx=5)

# ==================== ПОЛЗУНОК СКОРОСТИ ====================
speed_frame = tk.Frame(right_frame, bg='lightgray')
speed_frame.pack(fill=tk.X, padx=5, pady=10)
tk.Label(speed_frame, text="Скорость:", bg='lightgray', font=("Arial", 9)).pack(anchor="w")

speed_var = tk.StringVar(value="50")
last_valid_speed = "50"
updating = False

def update_speed(value):
    global current_delay
    current_delay = max(1, 101 - value)

def on_scale_change(value):
    global last_valid_speed, updating
    if updating: return
    updating = True
    try:
        entry.delete(0, tk.END)
        entry.insert(0, value)
        last_valid_speed = value
        update_speed(int(value))
    finally:
        updating = False

def on_entry_change(event=None):
    global last_valid_speed, updating
    if updating: return
    updating = True
    try:
        value = speed_var.get()
        
        if value == "":
            if last_valid_speed == "0":
                entry.delete(0, tk.END)
                entry.insert(0, "0")
                entry.icursor(tk.END)
                return
            else:
                scale.set(0)
                update_speed(0)
                return
            
        if not value.isdigit():
            show_speed_error("Ошибка", "Недопустимый символ", "not_digit")
            entry.delete(0, tk.END)
            entry.insert(0, last_valid_speed)
            return
            
        if value.startswith("0") and len(value) > 1:
            show_speed_error("Ошибка", "Незначащие нули удалены", "leading_zero_removed")
            new_value = value.lstrip("0") or "0"
            entry.delete(0, tk.END)
            entry.insert(0, new_value)
            last_valid_speed = new_value
            scale.set(int(new_value))
            update_speed(int(new_value))
            return
            
        num = int(value)
        if num > 100:
            show_speed_error("Ошибка", "Вводите числа от 0 до 100", "max_speed")
            entry.delete(0, tk.END)
            entry.insert(0, "100")
            last_valid_speed = "100"
            scale.set(100)
            update_speed(100)
            return
            
        last_valid_speed = value
        scale.set(num)
        update_speed(num)
    finally:
        updating = False

scale = tk.Scale(speed_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                 command=on_scale_change, showvalue=0, length=120)
scale.set(50)
scale.pack(side=tk.LEFT, padx=2)

entry = tk.Entry(speed_frame, textvariable=speed_var, width=4, font=("Arial", 10))
entry.pack(side=tk.LEFT, padx=2)
entry.bind("<KeyRelease>", on_entry_change)
update_speed(50)

# ==================== ИНИЦИАЛИЗАЦИЯ ====================
root.update_idletasks()
update_layout()
root.mainloop()