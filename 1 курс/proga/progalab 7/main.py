import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends._backend_tk import NavigationToolbar2Tk
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ======================== ЭТАП 0-1: ИНИЦИАЛИЗАЦИЯ ========================
VARIANT_NUMBER = 8
DATA_PATH = Path(__file__).resolve().parent / 'data.csv'

df_raw: Optional[pd.DataFrame] = None
df_processed: Optional[pd.DataFrame] = None  # Обработанные данные (ОДИН РАЗ)
df_work: Optional[pd.DataFrame] = None       # Рабочая копия для графика
fig: plt.Figure
canvas: Optional[FigureCanvasTkAgg] = None
current_chart: str = "line"
available_vehicles: List[int] = []  # Список НЕ редких vehicle_id

root = tk.Tk()
root.title(f"Дашборд: Вариант {VARIANT_NUMBER} — GPS телеметрия")
root.geometry("1100x750")
root.configure(bg="#f0f2f5")

vehicle_var = tk.StringVar(value="Все")
agg_var = tk.StringVar(value="mean")
window_var = tk.IntVar(value=45)

# Настройка шрифтов для кириллицы
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_theme(style="whitegrid", palette="muted")

# ======================== ЗАГРУЗКА ДАННЫХ ========================
def load_data() -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(DATA_PATH, parse_dates=False)
        if df.empty:
            messagebox.showerror("Ошибка", "Файл data.csv пуст.")
            return None
        
        # Добавление 4 категориальных признаков (Этап 0)
        np.random.seed(42)
        df['region'] = np.random.choice(['Москва', 'СПб', 'Казань', 'Новосибирск'], size=len(df))
        df['road_type'] = pd.Categorical(np.random.choice(['город', 'трасса', 'бездорожье'], size=len(df)))
        df['weather'] = pd.Categorical(np.random.choice(['ясно', 'дождь', 'снег', 'туман'], size=len(df)))
        df['vehicle_class'] = pd.Categorical(np.random.choice(['легковой', 'грузовой', 'автобус'], size=len(df)))
        
        return df
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить CSV: {e}")
        return None

df_raw = load_data()
if df_raw is None:
    raise SystemExit("Данные недоступны")

# ======================== ЭТАП 2: ПРЕДОБРАБОТКА (ОДИН РАЗ) ========================
def preprocess_data(df_input: pd.DataFrame) -> Tuple[pd.DataFrame, List[int]]:
    """
    Общая предобработка данных (выполняется ОДИН РАЗ при старте)
    Возвращает: (обработанный DataFrame, список НЕ редких vehicle_id)
    """
    df = df_input.copy()
    
    # 1. Фильтрация по условию варианта
    df = df.query('speed >= 0 and fuel <= 100')
    
    # 2. Безопасная замена NaN/Inf медианами
    for col in ['speed', 'fuel', 'engine']:
        clean_col = df[col].replace([np.inf, -np.inf], np.nan)
        df[col] = clean_col.fillna(clean_col.median())
    
    # Ограничение физических диапазонов
    df['fuel'] = df['fuel'].clip(lower=0, upper=100)
    df['speed'] = df['speed'].clip(lower=0)
    df['engine'] = df['engine'].clip(lower=0)
    
    # Clip engine по 85-му перцентилю
    p85_engine = df['engine'].quantile(0.85)
    df['engine'] = df['engine'].clip(upper=p85_engine)
    
    # 3. Feature Engineering
    df['dt'] = pd.to_datetime(df['ts'], unit='s')
    
    # Эффективность использования топлива (speed/fuel)
    df['fuel_eff'] = df['speed'] / (df['fuel'] + 1e-8)
    df['fuel_eff'] = df['fuel_eff'].replace([np.inf, -np.inf], 0.0)
    
    # Нагрузка на двигатель (engine/speed)
    df['engine_load'] = df['engine'] / (df['speed'] + 1e-8)
    df['engine_load'] = df['engine_load'].replace([np.inf, -np.inf], 0.0)
    
    # Биннинг скорости по категориям
    df['speed_category'] = pd.cut(
        df['speed'], 
        bins=[0, 30, 60, 90, 200],
        labels=['низкая', 'средняя', 'высокая', 'очень высокая']
    ).astype('category')
    
    # Сезон на основе месяца
    season_map = {
        1: 'зима', 2: 'зима', 12: 'зима',
        3: 'весна', 4: 'весна', 5: 'весна',
        6: 'лето', 7: 'лето', 8: 'лето',
        9: 'осень', 10: 'осень', 11: 'осень'
    }
    df['season'] = df['dt'].dt.month.map(season_map).astype('category')
    
    df = df.sort_values(['vehicle_id', 'ts']).reset_index(drop=True)
    
    # Скользящее среднее скорости и тренд
    df['speed_ma'] = df.groupby('vehicle_id')['speed'].transform(
        lambda x: x.rolling(window=45, min_periods=1).mean()
    )
    df['speed_diff'] = df.groupby('vehicle_id')['speed_ma'].transform(
        lambda x: x.diff().fillna(0)
    )
    df['speed_trend'] = np.sign(df['speed_diff']).map(
        {-1: 'торможение', 0: 'стабильно', 1: 'разгон'}
    ).astype('category')
    
    # 4. Обрезка выбросов (IQR по группам vehicle_id для speed)
    grp = df.groupby('vehicle_id')['speed']
    q1 = grp.transform(lambda x: x.quantile(0.25))
    q3 = grp.transform(lambda x: x.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    median_grp = grp.transform('median')
    is_outlier = (df['speed'] < lower_bound) | (df['speed'] > upper_bound)
    df.loc[is_outlier, 'speed'] = median_grp[is_outlier]
    
    # 5. Оптимизация: редкие vehicle_id → 0
    threshold = int(0.01 * len(df))
    counts = df['vehicle_id'].value_counts()
    rare_ids = counts[counts < threshold].index
    
    # СОХРАНЯЕМ список НЕ редких vehicle_id ДО замены
    non_rare_vehicles = sorted([v for v in df['vehicle_id'].unique() if v not in rare_ids and v != 0])
    
    # Заменяем редкие на 0
    df.loc[df['vehicle_id'].isin(rare_ids), 'vehicle_id'] = 0
    df['vehicle_id'] = df['vehicle_id'].astype('category')
    df['dt'] = df['dt'].astype('datetime64[ns]')
    
    return df, non_rare_vehicles

# ======================== ОДНОКРАТНАЯ ОБРАБОТКА ========================
df_processed, available_vehicles = preprocess_data(df_raw)
print(f"✓ Загружено {len(df_processed)} записей")
print(f"✓ Доступные автомобили (не редкие): {available_vehicles[:10]}...")
print(f"✓ Всего уникальных автомобилей в df_processed: {df_processed['vehicle_id'].nunique()}")

# ======================== ЭТАП 3: GUI ========================
plot_frame = tk.Frame(root, bg="white", relief=tk.SUNKEN, bd=1)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

fig = plt.Figure(figsize=(10, 6), dpi=100)
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
toolbar.pack(side=tk.TOP, fill=tk.X)

# ======================== ЭТАП 4: ОТРИСОВКА ========================
def clear_figure() -> plt.Axes:
    fig.clear()
    return fig.add_subplot(111)

def plot_line() -> None:
    """Линейный график: динамика скорости по времени (скользящее среднее)"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    df_plot = df_work.copy()
    
    # Агрегация по неделям
    df_plot['week'] = df_plot['dt'].dt.to_period('W').dt.start_time
    agg_df = df_plot.groupby(['week', 'vehicle_id'])['speed_ma'].mean().reset_index()
    
    # Показываем ТОЛЬКО автомобили из текущего df_work
    current_vehicles = sorted(agg_df['vehicle_id'].unique())[:5]  # Ограничиваем 5 для читаемости
    for v_id in current_vehicles:
        group = agg_df[agg_df['vehicle_id'] == v_id]
        ax.plot(group['week'], group['speed_ma'], label=f'Авто {int(v_id)}', 
                linewidth=1.5, alpha=0.7)
    
    ax.set_title("Динамика скорости (скользящее среднее, агрегация по неделям)")
    ax.set_xlabel("Дата")
    ax.set_ylabel("Скорость, км/ч")
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), ncol=1, fontsize=8)
    fig.autofmt_xdate()
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_bar() -> None:
    """Столбчатая диаграмма: средний расход топлива по классам авто"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    agg_method = agg_var.get()
    agg_df = df_work.groupby('vehicle_class')['fuel'].agg(agg_method).reset_index()
    agg_df.columns = ['vehicle_class', f'fuel_{agg_method}']
    
    colors = ['#4A90E2', '#7ED321', '#F5A623']
    sns.barplot(data=agg_df, x='vehicle_class', y=f'fuel_{agg_method}', 
                palette=colors, ax=ax, errorbar=None)
    
    ax.set_title(f"Уровень топлива по классам авто ({agg_method})")
    ax.set_xlabel("Класс авто")
    ax.set_ylabel(f"Топливо, % ({agg_method})")
    ax.tick_params(axis='x', rotation=0)
    fig.tight_layout()
    canvas.draw_idle()

def plot_scatter() -> None:
    """Точечная диаграмма: скорость vs обороты двигателя"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    df_plot = df_work.copy()
    
    # Сэмплирование для производительности
    if len(df_plot) > 5000:
        df_plot = df_plot.sample(n=5000, random_state=42)
    
    sns.scatterplot(data=df_plot, x='speed', y='engine', 
                    hue='road_type', ax=ax, alpha=0.6, s=30)
    
    ax.set_title("Зависимость оборотов двигателя от скорости")
    ax.set_xlabel("Скорость, км/ч")
    ax.set_ylabel("Обороты двигателя, тыс/мин")
    ax.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    fig.tight_layout(rect=[0, 0.03, 0.88, 0.95])
    canvas.draw_idle()

def plot_heat_map() -> None:
    """Тепловая карта: матрица корреляции числовых признаков"""
    ax = clear_figure()
    if df_work is None or df_work.empty:
        return
    
    # Выбираем только числовые колонки для корреляции
    numeric_cols = ['speed', 'fuel', 'engine', 'acc', 'fuel_eff', 'engine_load']
    df_corr = df_work[numeric_cols].corr()
    
    sns.heatmap(df_corr, annot=True, cmap='coolwarm', center=0, ax=ax, fmt='.2f',
                cbar_kws={'label': 'Корреляция'})
    
    ax.set_title("Матрица корреляции показателей телеметрии")
    fig.tight_layout()
    canvas.draw_idle()

# ======================== ЭТАП 5-6: УПРАВЛЕНИЕ ========================
def apply_filters_and_redraw() -> None:
    """
    Применяет фильтры к УЖЕ ОБРАБОТАННЫМ данным (df_processed).
    НЕ вызывает preprocess_data() повторно!
    """
    global df_work
    if df_processed is None:
        return
    
    # 1. Создаём копию уже обработанных данных (БЫСТРО!)
    df_work = df_processed.copy()
    
    # 2. Применяем фильтр по vehicle_id
    selected_vehicle = vehicle_var.get()
    if selected_vehicle != "Все":
        vehicle_value = int(selected_vehicle)
        mask = df_work['vehicle_id'] == vehicle_value
        df_work = df_work.loc[mask].copy()
        print(f"✓ Фильтр применён: vehicle_id={vehicle_value}, строк={len(df_work)}")
    else:
        print("✓ Фильтр: Все данные")
    
    # 3. Перерисовываем текущий график
    if current_chart == "line":
        plot_line()
    elif current_chart == "bar":
        plot_bar()
    elif current_chart == "scatter":
        plot_scatter()
    elif current_chart == "heatmap":
        plot_heat_map()

def set_chart_type(chart_type: str):
    """Переключает тип графика"""
    global current_chart
    current_chart = chart_type
    apply_filters_and_redraw()

def export_plot() -> None:
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("PDF", "*.pdf")]
    )
    if filepath:
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        messagebox.showinfo("Экспорт", "График сохранён")

# ======================== ПАНЕЛЬ УПРАВЛЕНИЯ ========================
ctrl_frame = tk.Frame(root, bg="#f0f2f5")
ctrl_frame.pack(fill=tk.X, padx=10, pady=8)

# Фильтр по vehicle_id - ТОЛЬКО НЕ РЕДКИЕ
tk.Label(ctrl_frame, text="Автомобиль:", bg="#f0f2f5").pack(side=tk.LEFT, padx=5)
vehicle_values = ["Все", "0"] + [str(v) for v in available_vehicles]
vehicle_combo = ttk.Combobox(ctrl_frame, textvariable=vehicle_var, values=vehicle_values,
                              width=10, state="readonly")
vehicle_combo.pack(side=tk.LEFT, padx=5)

# Отслеживаем изменения
vehicle_var.trace_add("write", lambda *_: apply_filters_and_redraw())

# Агрегация
tk.Label(ctrl_frame, text="Агрегация:", bg="#f0f2f5").pack(side=tk.LEFT, padx=(15, 5))
for agg in ["mean", "median", "sum"]:
    tk.Radiobutton(ctrl_frame, text=agg.capitalize(), variable=agg_var,
                   value=agg, bg="#f0f2f5",
                   command=apply_filters_and_redraw).pack(side=tk.LEFT, padx=2)

# Кнопки типов графиков
tk.Button(ctrl_frame, text="Линейный", command=lambda: set_chart_type("line"),
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Столбчатый", command=lambda: set_chart_type("bar"),
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Точечный", command=lambda: set_chart_type("scatter"),
          width=10).pack(side=tk.LEFT, padx=4)
tk.Button(ctrl_frame, text="Тепловая карта", command=lambda: set_chart_type("heatmap"),
          width=12).pack(side=tk.LEFT, padx=4)

# Служебные кнопки
tk.Button(ctrl_frame, text="🔄 Обновить", command=apply_filters_and_redraw,
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)
tk.Button(ctrl_frame, text="💾 Экспорт", command=export_plot,
          width=12, bg="#e0e0e0").pack(side=tk.RIGHT, padx=4)

# ======================== ЗАПУСК ========================
if __name__ == '__main__':
    # Инициализация рабочей копии
    df_work = df_processed.copy()
    plot_line()
    root.mainloop()