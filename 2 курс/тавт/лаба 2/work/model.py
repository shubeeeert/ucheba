# -*- coding: utf-8 -*-
"""
Бот турнира «камень — ножницы — бумага» по уточнённым Н.У.

Переменные (только эти):
    МХ  — мой ход
    ИСТ — история (таблица 4)
    НР  — номер раунда            (НР = 0)
    ХС  — ход соперника
    СХС — следующий ход соперника
    РЗ  — результат
    КХ  — контрход
    СП  — счётчик поражений       (СП = 0)
    СН  — счётчик ничьих          (СН = 0)
    С   — стратегия               (С = 0)

Таблицы:
    1 — контрход стратегии 1 (по ХС)
    2 — контрход стратегии 2 (по СХС)
    3 — определение результата (МХ, ХС) -> РЗ
    4 — история ИСТ
    5 — поиск паттерна
"""
from itertools import product

MOVES = ['К', 'Н', 'Б']
BEAT = {'К': 'Б', 'Н': 'К', 'Б': 'Н'}      # чем бьётся ход = контрход
BEATS = {'Б': 'К', 'К': 'Н', 'Н': 'Б'}     # что бьёт ход

N_ROUNDS = 5
K_PATTERN = 2
SWITCH = 2          # порог переключения стратегии: СП + СН >= 2

# ------------------------------------------------------------------ таблица 3
def result(my, opp):
    if my == opp:
        return 'Н'
    return 'В' if BEATS[my] == opp else 'П'

T3 = {m: {o: result(m, o) for o in MOVES} for m in MOVES}

# ------------------------------------------------------------------ таблицы 1, 2
T1 = {o: BEAT[o] for o in MOVES}
T2 = {o: BEAT[o] for o in MOVES}

# ------------------------------------------------------------------ таблица 5
def search_pattern(hist, ks=(2, 1)):
    """Паттерн — последние k ходов соперника. Сначала ищем самый длинный
    паттерн (k = 2), затем, если он не встречался, — короткий (k = 1).
    СХС — ход, сыгранный после ближайшего более раннего вхождения паттерна."""
    for k in ks:
        if len(hist) < k + 1:
            continue
        pat = tuple(r['ХС'] for r in hist[-k:])
        found, where = None, None
        for i in range(len(hist) - k - 1):
            if tuple(r['ХС'] for r in hist[i:i + k]) == pat:
                found, where = hist[i + k]['ХС'], (i + 1, i + k + 1)
        if found is not None:
            return found, k, where
    return None, None, None


def play(opp_seq, log=True):
    НР = 0
    СП = СН = 0
    С = 0
    ИСТ = []
    МХ = None
    rows = []
    for t, ХС in enumerate(opp_seq, 1):
        НР = t
        if НР == 1:
            МХ = 'К'
        РЗ = T3[МХ][ХС]
        if РЗ == 'П':
            СП += 1
        elif РЗ == 'Н':
            СН += 1
        ИСТ.append({'НР': НР, 'ХС': ХС, 'МХ': МХ, 'РЗ': РЗ})

        row = {'НР': НР, 'МХ': МХ, 'ХС': ХС, 'РЗ': РЗ,
               'СП': СП, 'СН': СН, 'С': С, 'СХС': None,
               'паттерн': False, 'КХ': None}
        if НР == N_ROUNDS:
            rows.append(row)
            break

        if СП + СН >= SWITCH:
            С = 1
        row['С'] = С
        if С == 0:
            КХ = T1[ХС]
        else:
            СХС, lvl, where = search_pattern(ИСТ)
            if СХС is not None:
                row['паттерн'] = True
                row['СХС'] = СХС
                row['уровень'] = lvl
                КХ = T2[СХС]
            else:
                КХ = T1[ХС]
        row['КХ'] = КХ
        rows.append(row)
        МХ = КХ

    score = {'В': sum(1 for r in rows if r['РЗ'] == 'В'),
             'Н': СН, 'П': СП}
    if log:
        print('\nСоперник: %s' % ' '.join(opp_seq))
        print('НР | МХ | ХС | РЗ | СП | СН | С | СХС | патт | КХ')
        for r in rows:
            print('%2d |  %s |  %s |  %s |  %d |  %d | %d |  %s |  %-3s |  %s' % (
                r['НР'], r['МХ'], r['ХС'], r['РЗ'], r['СП'], r['СН'], r['С'],
                r['СХС'] or '—', 'да' if r['паттерн'] else 'нет', r['КХ'] or '—'))
        print('Итог: В=%d Н=%d П=%d' % (score['В'], score['Н'], score['П']))
    return rows, score


if __name__ == '__main__':
    DEMO = ['Н', 'К', 'Н', 'К', 'Н']
    play(DEMO)

    print('\nТаблица 5 для ИСТ = [Н, К, Н] (поиск в 4-м раунде):')
    for a in MOVES:
        for b in MOVES:
            print('  (%s,%s): %s' % (a, b, 'найден' if (a, b) == ('Н', 'К') else '—'))

    # статистика по всем матчам длины 5
    wins = draws = losses = 0
    for seq in product(MOVES, repeat=N_ROUNDS):
        _, sc = play(list(seq), log=False)
        wins += sc['В'] > sc['П']
        draws += sc['В'] == sc['П']
        losses += sc['В'] < sc['П']
    total = 3 ** N_ROUNDS
    print('\nИз %d матчей: побед %.1f%%, ничьих %.1f%%, поражений %.1f%%'
          % (total, 100 * wins / total, 100 * draws / total, 100 * losses / total))
