import numpy as np

np.random.seed(2026)
days = 100

# Температура: нормальное распределение + пропуски + отрицательные
temperature = np.random.normal(loc=12, scale=10, size=days).round(1)
# '''Генерируется 100 значений из нормального распределения со средним (loc) = 12°C 
# и стандартным отклонением (scale) = 10°C.
# .round(1) округляет до одного знака после запятой.'''

nan_indices = np.random.choice(days, 5, replace=False)
# '''Выбираются 5 случайных индексов (без повторений)'''
temperature[nan_indices] = np.nan

cold_indices = np.random.choice(days, 8, replace=False)
temperature[cold_indices] = np.random.randint(-30, -14, 8)

# Потребление: гамма-распределение + выбросы
consumption = np.random.gamma(shape=2, scale=8, size=days).astype(int)
outlier_indices = np.random.choice(days, 4, replace=False)
consumption[outlier_indices] = np.random.randint(300, 600, 4)

# Тип дня: 0 – рабочий, 1 – выходной
day_type = np.random.choice([0, 1], size=days, p=[0.7, 0.3])
# '''Генерируется массив из 100 значений, каждое – либо 0, либо 1.
# Вероятность получить 0  = 70%, 1  = 30%'''


##########################################################
###                      РЕШЕНИЕ                       ###
##########################################################

# 1. Кол-во пропусков в temperature
nan_mask = np.isnan(temperature)
nan_count = np.sum(nan_mask)
print(f"1. Количество пропусков: {nan_count}")

# 2. Замена пропусков на медиану
median = np.nanmedian(temperature)
temperature = np.where(np.isnan(temperature), median, temperature)
min_t = np.min(temperature)
max_t = np.max(temperature)
mid_t = np.mean(temperature)
print("2. После замены пропусков")
print(f"Минимальное значение: {min_t}")
print(f"Максимальное значение: {max_t}")
print(f"Среднее значение: {mid_t}")

# 3. Холодные дни
cold_index = np.where(temperature < -17)[0]
print(f"3. Холодные дни: {cold_index}")

# 4. Среднее потребление для рабочих дней, когда temperature > 15
mask_warm_work = (temperature > 15) & (day_type == 0)
mean_consum_warm_work = np.mean(consumption[mask_warm_work])
print(f"4. Среднее потребление для рабочих дней с температурой > 15°C: {mean_consum_warm_work:.2f}")

# 5. Категории и подсчет дней в каждой
conditions = [
    temperature < 0,
    (temperature >= 0) & (temperature <= 20),
    temperature > 20
]
choices = ['cold', 'normal', 'warm']
temp_category = np.select(conditions, choices, default='unknown')
unique, counts = np.unique(temp_category, return_counts=True)
print("5. Количество дней по категориям:")
for cat, cnt in zip(unique, counts):
    print(f"   {cat}: {cnt}")

# 6. Среднее потребление для каждой комбинации day_type (0,1) и temp_category
cat_index = np.select(conditions, [0, 1, 2], default=-1)
combined = day_type * 3 + cat_index
sums = np.bincount(combined, weights=consumption, minlength=6)
counts = np.bincount(combined, minlength=6)
means = np.divide(sums, counts, out=np.full_like(sums, np.nan, dtype=float), where=counts>0)
result = means.reshape(2, 3)
print("6. Среднее потребление для (тип дня, категория):")
print("   (строки: day_type=0,1; столбцы: cold, normal, warm)")
print(result)
