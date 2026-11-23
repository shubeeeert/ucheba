import tkinter as tk
from tkinter import ttk, messagebox
from ctypes import *
from functools import wraps
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

mod = None
struct = None
buttons = []
grid = None
combobox = None
mods = {}
root = None

def load_mod(path: str):
    if path == "mod2":
        import mod2
        return mod2

    dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), path)
    if not os.path.exists(dll_path):
        raise FileNotFoundError(f"Библиотека не найдена: {dll_path}")
    lib = CDLL(dll_path)

    lib.make.restype = c_void_p
    lib.make.argtypes = []
    lib.push.argtypes = [c_void_p, c_int]
    lib.pop.argtypes = [c_void_p]
    lib.pop.restype = c_int
    lib.clear.argtypes = [c_void_p]
    lib.destroy.argtypes = [c_void_p]
    lib.getSize.argtypes = [c_void_p]
    lib.getSize.restype = c_int
    lib.isEmpty.argtypes = [c_void_p]
    lib.isEmpty.restype = c_bool
    lib.display.argtypes = [c_void_p, POINTER(c_int), c_int]
    lib.display.restype = c_int

    return lib

def process_stack(operation, position):
    size = mod.getSize(struct)
    if size == 0:
        messagebox.showinfo("Информация", "Стек пуст!")
        return

    ArrayType = c_int * size
    buffer = ArrayType()
    copied = mod.display(struct, buffer, size)

    elements = copied if isinstance(copied, list) else list(buffer)[:copied]

    if operation == "sum":
        result = sum(elements)
        op_name = "Сложение"
    else:
        result = 1
        for x in elements:
            result *= x
        op_name = "Умножение"

    pos_map = {"top": 0, "middle": size // 2, "bottom": size}
    idx = pos_map[position]
    pos_name = {"top": "начало (верх)", "middle": "середину", "bottom": "конец (низ)"}[position]

    mod.clear(struct)
    desired = elements[:idx] + [result] + elements[idx:]

    for val in reversed(desired):
        mod.push(struct, int(val))

    print(f"[✓] {op_name} завершено. Результат: {result}. Вставлено в {pos_name} стека.", flush=True)

def open_process_dialog():
    global root
    def execute():
        op = var_op.get()
        pos = var_pos.get()
        try:
            process_stack(op, pos)
            draw()
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка обработки", str(e))
            print(f"[✗] Ошибка обработки: {e}", flush=True)

    dialog = tk.Toplevel(root)
    dialog.title("Обработка элементов стека")
    dialog.geometry("300x240")
    dialog.transient(root)
    dialog.grab_set()
    dialog.resizable(False, False)

    tk.Label(dialog, text="Выберите операцию:", font=("Arial", 10)).pack(pady=(10,0))
    var_op = tk.StringVar(value="sum")
    tk.Radiobutton(dialog, text="Сложение всех элементов", variable=var_op, value="sum").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Умножение всех элементов", variable=var_op, value="mul").pack(anchor="w", padx=20)

    tk.Label(dialog, text="Куда поместить результат?", font=("Arial", 10)).pack(pady=(10,0))
    var_pos = tk.StringVar(value="middle")
    tk.Radiobutton(dialog, text="Начало (верх стека)", variable=var_pos, value="top").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Середина", variable=var_pos, value="middle").pack(anchor="w", padx=20)
    tk.Radiobutton(dialog, text="Конец (низ стека)", variable=var_pos, value="bottom").pack(anchor="w", padx=20)

    tk.Button(dialog, text="Выполнить", command=execute, width=20, bg="white", fg="black").pack(pady=15)

def draw():
    global mod, struct, grid
    if mod is None: return
    try:
        size = mod.getSize(struct)
    except Exception:
        size = 0

    if size == 0:
        grid.fill_grid([])
        return

    try:
        ArrayType = c_int * size
        buffer = ArrayType()
        copied = mod.display(struct, buffer, size)

        if isinstance(copied, int):
            grid.fill_grid(list(buffer)[:copied])
        else:
            grid.fill_grid(copied)
    except Exception as e:
        print(f"[✗] Ошибка отображения: {e}", flush=True)
        grid.fill_grid([])

def redraw(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            messagebox.showerror("Ошибка операции", str(e))
            print(f"[✗] Операция прервана: {e}", flush=True)
        draw()
    return wrapper

def on_select(event=None):
    global mod, struct
    value = combobox.get()
    if not value: return

    print(f"[↻] Смена модуля: {value}. Инициализация...", flush=True)

    if mod is not None:
        for btn in buttons:
            btn.config(state="disabled")
        try:
            mod.destroy(struct)
        except Exception:
            pass
        grid.clear_grid()

    mod = mods[value]
    struct = mod.make()
    for btn in buttons:
        btn.config(state="normal")
    draw()

class Int32Entry(tk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        vcmd = (self.register(self.validate_input), '%P')
        self.config(validate='key', validatecommand=vcmd)

    def validate_input(self, new_value):
        if new_value == "": return True
        if not new_value.lstrip('-').isdigit(): return False
        try:
            return -2147483648 <= int(new_value) <= 2147483647
        except ValueError:
            return False


class NumberGrid:
    def __init__(self, master, canvas):
        self.master = master
        self.canvas = canvas
        self.cell_height = 30
        self.cell_width = 400
        self.labels = []

    def clear_grid(self):
        for label in self.labels:
            label.destroy()
        self.labels.clear()
        self.master.update_idletasks()

    def fill_grid(self, numbers):
        self.clear_grid()
        if not numbers:
            self.canvas.configure(scrollregion=(0, 0, 300, 0))
            return

        w = self.canvas.winfo_width()
        if w <= 20:
            w = 100

        cell_width = w - 24
        total_height = len(numbers) * self.cell_height + 20

        self.master.config(height=total_height, width=cell_width)

        for i, number in enumerate(numbers):
            y = 10 + i * self.cell_height
            label = ttk.Label(self.master, text=str(number), width=10, relief="ridge", padding=2, anchor="center")
            label.place(x=0, y=y, width=self.cell_width, height=self.cell_height)
            self.labels.append(label)

        self.master.update_idletasks()
        self.canvas.configure(scrollregion=(0, 0, cell_width, total_height))

def main():
    global buttons, combobox, grid, root

    root = tk.Tk()
    root.title("Визуализатор стека")
    root.geometry("800x600")

    left_frame = tk.Frame(root, bg="lightgray")
    right_frame = tk.Frame(root, bg="lightblue")
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(right_frame, bg="lightblue", highlightthickness=0)
    scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="lightblue")

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")



    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    left_top_frame = tk.Frame(left_frame, bg="lightgray")
    left_bottom_frame = tk.Frame(left_frame, bg="lightgray")
    left_top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
    left_bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

    combobox_options = list(mods.keys())
    combobox = ttk.Combobox(left_top_frame, values=combobox_options, state="readonly", )
    combobox.bind("<<ComboboxSelected>>", on_select)
    combobox.pack(pady=10, padx=20, fill=tk.X)
    if combobox_options: combobox.current(0)

    entry = Int32Entry(left_top_frame, width=30)
    entry.pack(pady=5, padx=20, fill=tk.X)

    @redraw
    def f1():
        value = entry.get()
        if not value: return
        mod.push(struct, int(value))
        # entry.delete(0, tk.END)
        print(f"[+] Элемент помещён в стек: {value}", flush=True)

    @redraw
    def f2():
        if mod.isEmpty(struct):
            print("[-] Стек пуст. Нечего забирать.", flush=True)
            return
        value = mod.pop(struct)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        print(f"[-] Элемент изъят из стека: {value}", flush=True)

    def f3():
        if mod.isEmpty(struct):
            print("[-] Стек пуст. Обработка невозможна.", flush=True)
            return
        open_process_dialog()

    def f4():
        mod.clear(struct)
        draw()
        print("[*] Стек полностью очищен.", flush=True)

    @redraw
    def f5():
        value = mod.getSize(struct)
        entry.delete(0, tk.END)
        entry.insert(0, str(value))
        print(f"[i] Текущий размер стека: {value}", flush=True)

    button_nf = [
        ("Вставить", f1),
        ("Забрать", f2),
        ("Обработать элементы", f3),
        ("Очистить", f4),
        ("Узнать размер", f5),
    ]

    for text, cmd in button_nf:
        btn = tk.Button(left_bottom_frame, text=text, command=cmd, state="disabled")
        btn.pack(pady=5, padx=20, fill=tk.X)
        buttons.append(btn)

    grid = NumberGrid(scrollable_frame, canvas)

    on_select()
    root.mainloop()

if __name__ == "__main__":
    mods = {
        "C++ (mod1)": load_mod("mod1.dll"),
        "Python (mod2)": load_mod("mod2"),
        "STL (mod3)": load_mod("mod3.dll"),
    }
    main()