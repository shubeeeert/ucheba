ROCK = 1      # Камень (К)
PAPER = 2     # Бумага (Б)
SCISSORS = 3  # Ножницы (Н)

# Контрход: фигура, побеждающая ключевую (табл. 1: К->Б, Н->К, Б->Н)
BEATS = {ROCK: PAPER, SCISSORS: ROCK, PAPER: SCISSORS}

# Первые 3 хода фиксированы: Б, К, Н; далее этот же цикл как запасной вариант
FIXED = (PAPER, ROCK, SCISSORS)

PATTERN_LEN = 2       # длина паттерна (последние два хода соперника)
WIN_LIMIT = 3         # СП=3: 3 победы подряд -> сброс СП (стратегия работает, не меняем)
LOSS_LIMIT = 3        # СН=3: 3 поражения подряд -> смена стратегии
DRAW_LIMIT = 3        # 3 ничьи подряд -> смена стратегии (защита от зацикливания)
STRATEGY_COUNT = 3    # стратегии 0, 1, 2 (сдвиг контрхода, табл. 3)

_history = []         # ИСТ: история ходов соперника
_round = 0            # НР: номер раунда
_strategy = 0         # СТР: текущая стратегия
_wins = 0             # СП: счётчик побед подряд
_losses = 0           # СН: счётчик поражений подряд
_draws = 0            # счётчик ничьих подряд (защита от зацикливания)
_last_move = 0        # МХ: наш ход на предыдущем раунде


def set_parameters(set_count: int, wins_per_set: int) -> None:
    pass


def on_game_start() -> None:
    global _history, _round, _strategy, _wins, _losses, _draws, _last_move
    _history = []
    _round = 0
    _strategy = 0
    _wins = 0
    _losses = 0
    _draws = 0
    _last_move = 0


def _update_result(previous_opponent_choice: int) -> None:
    """Определение результата прошлого раунда (РЗ) и обновление СП/СН/СТР."""
    global _strategy, _wins, _losses, _draws
    if _last_move == previous_opponent_choice:      # ничья
        _draws += 1
        _wins = 0
        _losses = 0
    elif BEATS[previous_opponent_choice] == _last_move:  # победа
        _wins += 1
        _losses = 0
        _draws = 0
    else:                                            # поражение
        _losses += 1
        _wins = 0
        _draws = 0
    if _wins >= WIN_LIMIT:
        _wins = 0
    if _losses >= LOSS_LIMIT or _draws >= DRAW_LIMIT:
        _strategy = (_strategy + 1) % STRATEGY_COUNT
        _wins = 0
        _losses = 0
        _draws = 0


def _predict() -> int:
    """Поиск паттерна из последних PATTERN_LEN ходов в истории; 0, если не найден."""
    n = len(_history)
    if n <= PATTERN_LEN:
        return 0
    pattern = _history[n - PATTERN_LEN:]
    # ищем самое позднее вхождение паттерна, за которым есть следующий ход
    for i in range(n - PATTERN_LEN - 1, -1, -1):
        if _history[i:i + PATTERN_LEN] == pattern:
            return _history[i + PATTERN_LEN]
    return 0


def choose(previous_opponent_choice: int) -> int:
    global _round, _last_move

    if previous_opponent_choice != 0:
        _update_result(previous_opponent_choice)
        _history.append(previous_opponent_choice)

    _round += 1

    if _round <= 3:
        move = FIXED[_round - 1]
    else:
        predicted = _predict()
        if predicted:
            # КХ по табл. 1, затем сдвиг по текущей стратегии (табл. 3)
            counter = BEATS[predicted]
            move = (counter - 1 + _strategy) % 3 + 1
        else:
            # паттерн не найден — цикл Б-К-Н
            move = FIXED[(_round - 1) % 3]

    _last_move = move
    return move


def on_game_end() -> None:
    pass
