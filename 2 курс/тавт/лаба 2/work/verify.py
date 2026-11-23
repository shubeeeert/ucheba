# -*- coding: utf-8 -*-
"""Проверка модели бота (см. model.py) — без внешних библиотек.

Что проверяется:
  1) трассировка демонстрационного матча совпадает с таблицей в отчёте;
  2) в последнем раунде контрход КХ не вычисляется;
  3) переключение стратегии необратимо и происходит ровно при СП + СН >= 2;
  4) в каждом раунде используются только таблицы 1–3 и таблица 5;
  5) полный перебор 3^5 матчей даёт те же проценты, что в отчёте;
  6) число встреченных историй не превосходит оценки 1+3+9+27+81+243 = 364.

Запуск:  python work/verify.py
"""
from itertools import product

from model import MOVES, N_ROUNDS, SWITCH, T1, T2, T3, play, search_pattern

OK = True


def check(name, cond, extra=''):
    global OK
    print('%-58s %s%s' % (name, 'OK' if cond else 'ОШИБКА',
                          ('  ' + extra) if extra and not cond else ''))
    if not cond:
        OK = False


# ---------------------------------------------------------------- 1. трассировка
DEMO = ['Н', 'К', 'Н', 'К', 'Н']
EXPECTED = [
    # НР, МХ, ХС, РЗ, СП, СН, С, СХС, КХ
    (1, 'К', 'Н', 'В', 0, 0, 0, None, 'К'),
    (2, 'К', 'К', 'Н', 0, 1, 0, None, 'Б'),
    (3, 'Б', 'Н', 'П', 1, 1, 1, 'К', 'Б'),
    (4, 'Б', 'К', 'В', 1, 1, 1, 'Н', 'К'),
    (5, 'К', 'Н', 'В', 1, 1, 1, None, None),
]
rows, score = play(DEMO, log=False)
got = [(r['НР'], r['МХ'], r['ХС'], r['РЗ'], r['СП'], r['СН'], r['С'], r['СХС'], r['КХ'])
       for r in rows]
check('1. трассировка матча Н, К, Н, К, Н', got == EXPECTED, repr(got))
check('2. итог демо-матча В=3 Н=1 П=1',
      (score['В'], score['Н'], score['П']) == (3, 1, 1), repr(score))

# ---------------------------------------------------------------- 2–3. инварианты
bad_last = bad_switch = bad_tables = 0
for seq in product(MOVES, repeat=N_ROUNDS):
    rs, _ = play(list(seq), log=False)
    if rs[-1]['КХ'] is not None:
        bad_last += 1
    prev = 0
    for r in rs:
        if r['С'] < prev:                       # 1 -> 0 невозможно
            bad_switch += 1
        prev = r['С']
        if r['С'] == 1 and r['СП'] + r['СН'] < SWITCH:
            bad_switch += 1
        if r['КХ'] is not None:
            src = T2[r['СХС']] if (r['С'] == 1 and r['паттерн']) else T1[r['ХС']]
            if r['КХ'] != src:
                bad_tables += 1
check('3. в 5-м раунде КХ не вычисляется', bad_last == 0, 'нарушений: %d' % bad_last)
check('4. переключение необратимо и только при СП+СН >= 2', bad_switch == 0,
      'нарушений: %d' % bad_switch)
check('5. КХ всегда берётся из табл. 1 или 2 по правилу', bad_tables == 0,
      'нарушений: %d' % bad_tables)

# ---------------------------------------------------------------- 4. таблица 5
# ИСТ = (Н, К, Н): пар нет, работает уровень k = 1, за ходом Н был К.
hist3 = [{'ХС': x} for x in ['Н', 'К', 'Н']]
check('6. табл. 5: ИСТ=(Н,К,Н) -> СХС=К, k=1',
      search_pattern(hist3)[:2] == ('К', 1), repr(search_pattern(hist3)))
# ИСТ = (Н, К, Н, К): пара (Н, К) была в раундах 1–2, после неё Н.
hist4 = [{'ХС': x} for x in ['Н', 'К', 'Н', 'К']]
check('7. табл. 5: ИСТ=(Н,К,Н,К) -> СХС=Н, k=2',
      search_pattern(hist4)[:2] == ('Н', 2), repr(search_pattern(hist4)))
check('8. табл. 3: диагональ — ничьи, b(x) бьёт x',
      all(T3[m][m] == 'Н' for m in MOVES) and
      all(T3[T1[m]][m] == 'В' for m in MOVES))

# ---------------------------------------------------------------- 5. статистика
wins = draws = losses = 0
histories = set()
for seq in product(MOVES, repeat=N_ROUNDS):
    rs, sc = play(list(seq), log=False)
    wins += sc['В'] > sc['П']
    draws += sc['В'] == sc['П']
    losses += sc['В'] < sc['П']
    # история = последовательность пар (ХС, МХ)
    acc = []
    for r in rs:
        acc.append((r['ХС'], r['МХ']))
        histories.add(tuple(acc))

total = 3 ** N_ROUNDS
print('   перебор: %d матчей -> побед %.1f%%, ничьих %.1f%%, поражений %.1f%%'
      % (total, 100.0 * wins / total, 100.0 * draws / total, 100.0 * losses / total))
check('9. перебор 3^5 = 243 матчей: 39.5 / 21.0 / 39.5 %',
      (wins, draws, losses) == (96, 51, 96), '%d / %d / %d' % (wins, draws, losses))
bound = sum(3 ** k for k in range(N_ROUNDS + 1))
check('10. встречено историй %d <= оценки %d' % (len(histories), bound),
      len(histories) <= bound)

print('\nИТОГ:', 'все проверки пройдены' if OK else 'ЕСТЬ ОШИБКИ')
raise SystemExit(0 if OK else 1)
