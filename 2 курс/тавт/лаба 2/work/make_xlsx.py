# -*- coding: utf-8 -*-
"""Книга Excel: таблицы 1–5 автомата бота (КНБ-турнир), уточнённые Н.У."""
import os
import sys
from itertools import product

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import MOVES, T1, T2, T3, N_ROUNDS, play, search_pattern

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   'tables', 'tablicy_avtomata.xlsx')

THIN = Side(style='thin', color='FF000000')
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HDR_FILL = PatternFill('solid', fgColor='FFD9E2F3')
ACC_FILL = PatternFill('solid', fgColor='FFFFF2CC')
SUB_FILL = PatternFill('solid', fgColor='FFF2F2F2')
TITLE_FONT = Font(name='Times New Roman', size=12, bold=True)
HDR_FONT = Font(name='Times New Roman', size=11, bold=True)
BODY_FONT = Font(name='Times New Roman', size=11)
CENTER = Alignment(horizontal='center', vertical='center', wrap_text=True)
LEFT = Alignment(horizontal='left', vertical='center', wrap_text=True)


def title(ws, text, ncols, row=1, height=30):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = TITLE_FONT
    c.alignment = CENTER
    ws.row_dimensions[row].height = height


def header(ws, row, values, height=32):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = HDR_FONT
        c.fill = HDR_FILL
        c.alignment = CENTER
        c.border = BORDER
    ws.row_dimensions[row].height = height


def body(ws, row, values, align=CENTER, fill=None, height=20, merge_to=None):
    for j, v in enumerate(values, 1):
        c = ws.cell(row=row, column=j, value=v)
        c.font = BODY_FONT
        c.alignment = align
        c.border = BORDER
        if fill:
            c.fill = fill
    if merge_to:
        ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=merge_to)
    ws.row_dimensions[row].height = height


def note(ws, row, text, ncols, height=46):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=ncols)
    c = ws.cell(row=row, column=1, value=text)
    c.font = BODY_FONT
    c.alignment = LEFT
    ws.row_dimensions[row].height = height


def widths(ws, ws_widths):
    for j, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(j)].width = w


wb = Workbook()

# ============================================================ Пояснения
ws = wb.active
ws.title = 'Пояснения'
title(ws, 'Лабораторная работа № 2. Турнир ботов «камень — ножницы — бумага»\n'
          'Конечный автомат: две стратегии и поиск паттерна в истории', 4, height=44)

r = 3
body(ws, r, ['Начальные установки (Н.У.)'], align=LEFT, fill=HDR_FILL, merge_to=4)
r += 1
for name, val in (('НР', '0 — номер раунда'), ('СП', '0 — счётчик поражений'),
                  ('СН', '0 — счётчик ничьих'), ('С', '0 — номер стратегии'),
                  ('ИСТ', '∅ — история (таблица 4)')):
    body(ws, r, [name, val], align=LEFT, merge_to=4)
    ws.cell(row=r, column=2).alignment = LEFT
    r += 1

r += 1
body(ws, r, ['Переменные автомата'], align=LEFT, fill=HDR_FILL, merge_to=4)
r += 1
vars_ = [
    ('МХ', 'мой ход (выход автомата)'),
    ('ХС', 'ход соперника (вход, приходит от сервера)'),
    ('СХС', 'следующий ход соперника (прогноз по таблице 5)'),
    ('РЗ', 'результат раунда: В — победа, Н — ничья, П — поражение'),
    ('КХ', 'контрход — ход, которым бот отвечает'),
    ('ИСТ', 'история: таблица записей (НР, ХС, МХ, РЗ)'),
    ('СП', 'счётчик поражений'),
    ('СН', 'счётчик ничьих'),
    ('С', 'стратегия: 0 — стратегия 1 (реактивная), 1 — стратегия 2 (по паттерну)'),
]
for name, desc in vars_:
    body(ws, r, [name, desc], align=LEFT, merge_to=4)
    ws.cell(row=r, column=2).alignment = LEFT
    r += 1

r += 1
body(ws, r, ['Таблицы'], align=LEFT, fill=HDR_FILL, merge_to=4)
r += 1
tables = [
    ('Таблица 1', 'Контрход стратегии 1: по фактическому ходу соперника ХС'),
    ('Таблица 2', 'Контрход стратегии 2: по прогнозу следующего хода СХС'),
    ('Таблица 3', 'Определение результата: (МХ, ХС) → РЗ'),
    ('Таблица 4', 'История ИСТ: формат записи и пример заполнения'),
    ('Таблица 5', 'Поиск паттерна: паттерн → СХС'),
]
for name, desc in tables:
    body(ws, r, [name, desc], align=LEFT, merge_to=4)
    ws.cell(row=r, column=2).alignment = LEFT
    r += 1

r += 1
body(ws, r, ['Правило работы'], align=LEFT, fill=HDR_FILL, merge_to=4)
r += 1
note(ws, r, '1. Пока сумма СП + СН < 2, работает стратегия 1: бот играет контрход на последний '
            'ход соперника (таблица 1).\n'
            '2. Как только СП + СН ≥ 2, включается стратегия 2 (необратимо, С := 1): бот ищет в '
            'истории такой же паттерн (таблица 5), получает прогноз СХС и играет контрход на '
            'прогноз (таблица 2).\n'
            '3. Если паттерн не найден — используется резервное правило стратегии 1 (таблица 1).\n'
            '4. Матч заканчивается после НР = 5; выводятся СП и СН.', 4, height=80)
widths(ws, [18, 40, 25, 25])

# ============================================================ Таблица 1
ws = wb.create_sheet('Т1_Контрход_стратегии_1')
title(ws, 'Таблица 1 — Контрход стратегии 1 (реактивная стратегия)', 4)
header(ws, 3, ['ХС — ход соперника', 'Код ХС', 'КХ — контрход', 'Код КХ'])
r = 4
code = {'К': 1, 'Н': 2, 'Б': 3}
for o in MOVES:
    body(ws, r, [o, code[o], T1[o], code[T1[o]]])
    r += 1
r += 1
note(ws, r, 'Стратегия 1: бот играет ход, который бьёт последний ход соперника. '
            'Применяется, пока не накопилось двух неудачных раундов (СП + СН < 2).', 4, height=34)
widths(ws, [22, 12, 18, 12])

# ============================================================ Таблица 2
ws = wb.create_sheet('Т2_Контрход_стратегии_2')
title(ws, 'Таблица 2 — Контрход стратегии 2 (проактивная стратегия)', 4)
header(ws, 3, ['СХС — прогноз хода соперника', 'Код СХС', 'КХ — контрход', 'Код КХ'])
r = 4
for o in MOVES:
    body(ws, r, [o, code[o], T2[o], code[T2[o]]])
    r += 1
r += 1
note(ws, r, 'Стратегия 2: бот играет ход, который бьёт прогнозируемый ход соперника СХС '
            '(прогноз даёт таблица 5). Функция контрхода та же, что в таблице 1, но аргумент '
            'другой: не факт ХС, а прогноз СХС.', 4, height=46)
widths(ws, [28, 12, 18, 12])

# ============================================================ Таблица 3
ws = wb.create_sheet('Т3_Определение_результата')
title(ws, 'Таблица 3 — Определение результата РЗ по паре (МХ, ХС)', 4)
header(ws, 3, ['МХ \\ ХС', 'К', 'Н', 'Б'])
r = 4
for m in MOVES:
    body(ws, r, [m] + [T3[m][o] for o in MOVES])
    ws.cell(row=r, column=1).font = HDR_FONT
    r += 1
r += 1
body(ws, r, ['Обозначения'], align=LEFT, fill=HDR_FILL, merge_to=4)
r += 1
for name, desc in (('В', 'бот выиграл раунд'), ('Н', 'ничья'), ('П', 'бот проиграл раунд')):
    body(ws, r, [name, desc], align=LEFT, merge_to=4)
    ws.cell(row=r, column=2).alignment = LEFT
    r += 1
widths(ws, [14, 12, 12, 12])

# ============================================================ Таблица 4
ws = wb.create_sheet('Т4_История')
title(ws, 'Таблица 4 — История ИСТ (формат записи и пример заполнения)', 4)
header(ws, 3, ['НР — номер раунда', 'ХС — ход соперника', 'МХ — мой ход', 'РЗ — результат'])
r = 4
demo = ['Н', 'К', 'Н', 'К', 'Н']
rows, score = play(demo, log=False)
for row in rows:
    body(ws, r, [row['НР'], row['ХС'], row['МХ'], row['РЗ']])
    r += 1
r += 1
note(ws, r, 'Каждый раунд в историю добавляется одна запись. ИСТ используется таблицей 5 для '
            'поиска паттерна; при N = 5 раундах в ИСТ не более 5 записей, поэтому автомат '
            'остаётся конечным (не более 1 + 3 + 9 + 27 + 81 = 121 различной истории).', 4, height=60)
widths(ws, [20, 20, 16, 16])

# ============================================================ Таблица 5
ws = wb.create_sheet('Т5_Поиск_паттерна')
title(ws, 'Таблица 5 — Поиск паттерна в истории (для ИСТ = Н, К, Н, К — 4-й раунд)', 5)
header(ws, 3, ['Уровень (длина паттерна)', 'Паттерн', 'Вхождения в ИСТ (номера раундов)',
               'СХС', 'Паттерн найден'])
r = 4


def pattern_rows(hist_moves, k):
    """Все паттерны длины k и ход, шедший за последним более ранним вхождением."""
    out = []
    for pat in product(MOVES, repeat=k):
        occ = []
        sxs = None
        for i in range(len(hist_moves) - k - 1):
            if tuple(hist_moves[i:i + k]) == pat:
                occ.append('%d–%d' % (i + 1, i + k))
                sxs = hist_moves[i + k]
        out.append((pat, occ, sxs))
    return out


hist_moves = [x['ХС'] for x in rows[:4]]          # ИСТ после 4-го раунда
body(ws, r, ['ИСТ = (%s)' % ', '.join(hist_moves), '', '', '', ''],
     align=LEFT, fill=SUB_FILL, merge_to=5)
r += 1
for k in (2, 1):
    for pat, occ, sxs in pattern_rows(hist_moves, k):
        hit = (k == 2 and pat == tuple(hist_moves[-2:]) and sxs is not None)
        body(ws, r, [k, '(%s)' % ', '.join(pat), ', '.join(occ) if occ else '—',
                     sxs or '—', 'да' if sxs else 'нет'],
             fill=ACC_FILL if hit else None)
        r += 1

r += 1
body(ws, r, ['ИСТ = (%s)' % ', '.join(hist_moves[:3]), '', '', '', ''],
     align=LEFT, fill=SUB_FILL, merge_to=5)
r += 1
for k in (2, 1):
    for pat, occ, sxs in pattern_rows(hist_moves[:3], k):
        body(ws, r, [k, '(%s)' % ', '.join(pat), ', '.join(occ) if occ else '—',
                     sxs or '—', 'да' if sxs else 'нет'])
        r += 1

r += 1
note(ws, r, 'Паттерн — последние k ходов соперника в ИСТ. Поиск идёт от длинного паттерна '
            '(k = 2) к короткому (k = 1) и останавливается на первом уровне, где есть более '
            'раннее вхождение. СХС — ход, сыгранный соперником сразу после самого позднего '
            'из таких вхождений.\n'
            'Верхний блок: ИСТ = (Н, К, Н, К) — состояние после 4-го раунда. На уровне k = 2 '
            'паттерн (Н, К) уже встречался в раундах 1–2, за ним соперник сыграл Н, поэтому '
            'СХС = Н (строка выделена).\n'
            'Нижний блок: ИСТ = (Н, К, Н) — состояние после 3-го раунда. Пары ещё не '
            'повторялись (k = 2 не даёт результата), поэтому работает уровень k = 1: ход Н '
            'уже был в 1-м раунде, за ним сыграно К, значит СХС = К.', 5, height=110)
widths(ws, [14, 14, 26, 10, 16])

# ============================================================ Трассировка
ws = wb.create_sheet('Доп_Трассировка')
title(ws, 'Трассировка матча (соперник: Н, К, Н, К, Н)', 11)
header(ws, 3, ['НР', 'МХ', 'ХС', 'РЗ', 'СП', 'СН', 'С', 'СХС', 'Паттерн найден',
               'КХ (→ МХ след. раунда)', 'ИСТ после раунда'])
r = 4
for i, row in enumerate(rows):
    ist_txt = ', '.join(x['ХС'] for x in rows[:i + 1])
    body(ws, r, [row['НР'], row['МХ'], row['ХС'], row['РЗ'], row['СП'], row['СН'],
                 row['С'], row['СХС'] or '—', 'да' if row['паттерн'] else 'нет',
                 row['КХ'] or '— (матч окончен)', ist_txt])
    r += 1
body(ws, r, ['Итог', '', '', 'В: %d  Н: %d  П: %d' % (score['В'], score['Н'], score['П']),
             rows[-1]['СП'], rows[-1]['СН'], '', '', '', '', ''], fill=SUB_FILL)
r += 2
note(ws, r, 'В 3-м раунде паттерн найден на уровне k = 1 (пара ещё не повторялась), '
            'в 4-м — на уровне k = 2. Оба раза бот сыграл контрход на прогноз по таблице 2 '
            'и выиграл раунд.', 11, height=34)
widths(ws, [8, 8, 8, 8, 8, 8, 8, 8, 16, 24, 20])

# ============================================================ Протокол
ws = wb.create_sheet('Доп_Протокол')
title(ws, 'Протокол матча (бланк для заполнения)', 11)
header(ws, 3, ['НР', 'МХ', 'ХС', 'РЗ', 'СП', 'СН', 'С', 'СХС', 'Паттерн найден',
               'КХ (→ МХ след. раунда)', 'ИСТ после раунда'])
r = 4
for i in range(1, N_ROUNDS + 1):
    body(ws, r, [i, '', '', '', '', '', '', '', '', '', ''])
    r += 1
body(ws, r, ['Итог', '', '', '', '', '', '', '', '', '', ''], fill=SUB_FILL)
widths(ws, [8, 8, 8, 8, 8, 8, 8, 8, 16, 24, 20])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
wb.save(OUT)
print('Сохранено:', OUT)
