"""Генератор тестовых CSV-данных для лабораторной работы №5.

Предметная область сохранена прежней: студент (ФИО, группа, дата рождения,
рост, вес, признак отчисления). Генерация не использует глобальное состояние,
поэтому функцию можно вызывать повторно.
"""

import csv
from datetime import datetime
from random import choice, randint


male_names = [
    "Александр ", "Дмитрий ", "Максим ", "Сергей ", "Андрей ", "Алексей ", "Артем ",
    "Илья ", "Кирилл ", "Михаил ", "Никита ", "Матвей ", "Роман ", "Егор ", "Арсений ",
    "Иван ", "Денис ", "Евгений ", "Даниил ", "Тимофей ", "Владислав ", "Игорь ",
    "Владимир ", "Павел ", "Марк ", "Константин ", "Тимур ", "Олег ", "Ярослав ",
    "Антон ", "Николай ", "Глеб ", "Виктор ", "Юрий ", "Борис ", "Геннадий ", "Руслан "
]
female_names = [
    "Анна ", "Мария ", "Елена ", "Ольга ", "Наталья ", "Екатерина ", "Татьяна ",
    "Ирина ", "Светлана ", "Юлия ", "Анастасия ", "Дарья ", "Виктория ", "Ксения ",
    "Алина ", "Полина ", "Вероника ", "Валерия ", "Ангелина ", "Диана ", "Варвара ",
    "Ева ", "София ", "Алиса ", "Милана ", "Арина ", "Кира ", "Елизавета ", "Ульяна ",
    "Вера ", "Надежда ", "Зоя ", "Лариса ", "Нина ", "Марина ", "Инна ", "Кристина "
]
male_surnames = [
    "Иванов ", "Петров ", "Сидоров ", "Смирнов ", "Кузнецов ", "Попов ", "Васильев ",
    "Соколов ", "Михайлов ", "Новиков ", "Федоров ", "Морозов ", "Волков ", "Алексеев ",
    "Лебедев ", "Семенов ", "Егоров ", "Павлов ", "Козлов ", "Степанов ", "Николаев ",
    "Орлов ", "Андреев ", "Макаров ", "Захаров ", "Зайцев ", "Соловьев ", "Борисов ",
    "Яковлев ", "Григорьев ", "Романов ", "Киселев ", "Ильин ", "Ковалев ", "Гусев ",
    "Титов ", "Медведев ", "Белов ", "Чернов ", "Быков ", "Морозов ", "Жуков "
]
female_surnames = [
    "Иванова ", "Петрова ", "Сидорова ", "Смирнова ", "Кузнецова ", "Попова ", "Васильева ",
    "Соколова ", "Михайлова ", "Новикова ", "Федорова ", "Морозова ", "Волкова ", "Алексеева ",
    "Лебедева ", "Семенова ", "Егорова ", "Павлова ", "Козлова ", "Степанова ", "Николаева ",
    "Орлова ", "Андреева ", "Макарова ", "Захарова ", "Зайцева ", "Соловьева ", "Борисова ",
    "Яковлева ", "Григорьева ", "Романова ", "Киселева ", "Ильина ", "Ковалева ", "Гусева ",
    "Титова ", "Медведева ", "Белова ", "Чернова ", "Быкова ", "Морозова ", "Жукова "
]

specialties = [
    'ИВТ', 'ПИ', 'ИС', 'КБ', 'ЭК', 'МН', 'ФН', 'СМ', 'БМТ', 'Э', 'ИФ', 'ФАД',
    'ФВиСКН', 'ФУ', 'ЮФ', 'ИЛ', 'ЦИР', 'ЦСА', 'ИВКА', 'ИФИ', 'ИЕиМИ', 'ФФ',
    'ФМОПиЗР', 'ИП', 'СФ'
]
study_forms = ['б', 'к', 'о', 'з']

CURRENT_DATE = datetime(2026, 8, 26)
MAX_BIRTH_DATE = datetime(2008, 8, 26)


def build_groups():
    """Формирует все допустимые обозначения учебных групп."""
    groups = []
    for spec in specialties:
        for form in study_forms:
            for year in range(20, 25):
                for stream in range(1, 5):
                    for group in range(1, 10):
                        for subgroup in range(2):
                            name = (
                                f"{spec}{form}-{year:02d}{stream:02d}-"
                                f"{group:02d}-{subgroup:02d}"
                            )
                            base_birth = 2002 + (year - 20) - (stream - 1) * 2
                            groups.append({
                                "name": name,
                                "min_birth": max(1994, base_birth - 1),
                                "max_birth": min(2008, base_birth + 2),
                            })
    return groups


ALL_GROUPS = build_groups()


def gen_line():
    """Возвращает одну случайную запись в виде списка из шести полей."""
    group_info = choice(ALL_GROUPS)
    group_name = group_info["name"]

    is_male = choice([True, False])
    if is_male:
        name = f"{choice(male_surnames)}{choice(male_names)}"
    else:
        name = f"{choice(female_surnames)}{choice(female_names)}"

    birth_year = randint(group_info["min_birth"], group_info["max_birth"])
    if birth_year > MAX_BIRTH_DATE.year:
        birth_year = MAX_BIRTH_DATE.year

    if birth_year == MAX_BIRTH_DATE.year:
        birth_month = randint(1, MAX_BIRTH_DATE.month)
        birth_day = randint(1, 26 if birth_month == MAX_BIRTH_DATE.month else 28)
    else:
        birth_month = randint(1, 12)
        birth_day = randint(1, 28)

    dob = f"{birth_year}.{birth_month:02d}.{birth_day:02d}"
    height = str(randint(150, 200))
    weight = f"{randint(45, 120)}.{randint(0, 9)}"
    expulsion = "true" if randint(0, 99) <= 5 else "false"

    return [name, group_name, dob, height, weight, expulsion]


def generate(path: str, size_max: int, func=None) -> int:
    """Создаёт data.csv размером не менее size_max байт.

    Вызов func получает долю готовности в интервале [0, 1]. Функция не хранит
    состояние между вызовами, поэтому повторная генерация работает корректно.
    """
    target = int(size_max)
    if target <= 0:
        raise ValueError("Размер файла должен быть положительным")

    report_step = max(target // 100, 1024 * 1024)
    next_report = report_step

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        written = 0

        while written < target:
            row = gen_line()
            writer.writerow(row)
            # Поля не содержат запятых и кавычек, поэтому длина строки
            # совпадает с длиной склеенных полей + разделители и LF.
            written += len(",".join(row).encode("utf-8")) + 1

            if func is not None and written >= next_report:
                func(min(1.0, written / target))
                next_report += report_step

    if func is not None:
        func(1.0)
    return written


if __name__ == "__main__":
    # Более 1 ГБ: 1100 МиБ.
    target_size = 1100 * 1024 * 1024
    written_size = generate("data.csv", target_size, lambda p: print(f"{p:.1%}", end="\r"))
    print(f"\nГотово: data.csv, {written_size} байт")
