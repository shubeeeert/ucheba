"""
Высокопроизводительный генератор лабиринтов.
Основан на Randomized Depth-First Search (Recursive Backtracker).
Использует Data-Oriented Design концепции, оптимизированные для CPython (локальное кэширование, bytearray, 1D сетка).
"""

import random
from enum import IntFlag
from dataclasses import dataclass
from typing import List, Tuple, Optional


class CellState(IntFlag):
    """
    Битовые маски для состояний ячейки.
    Используются степени двойки для возможности комбинирования через побитовое ИЛИ (|).
    """
    NONE = 0
    UP = 1 << 0       # 1
    RIGHT = 1 << 1    # 2
    DOWN = 1 << 2     # 4
    LEFT = 1 << 3     # 8
    VISITED = 1 << 4  # 16


# Глобальные константы уровня модуля для минимизации накладных расходов на поиск атрибутов
_CARVE = (CellState.UP, CellState.RIGHT, CellState.DOWN, CellState.LEFT)
_OPPOSITE = (CellState.DOWN, CellState.LEFT, CellState.UP, CellState.RIGHT)
_D_ROW = (-1, 0, 1, 0)
_D_COL = (0, 1, 0, -1)


def _precompute_permutations() -> Tuple[Tuple[int, int, int, int], ...]:
    """
    Приватный метод для предрасчета всех 24 уникальных перестановок направлений (0, 1, 2, 3).
    Избавляет от необходимости использовать модуль itertools в горячем цикле.
    
    Returns:
        Кортеж кортежей, содержащий все комбинации направлений.
    """
    perms: List[Tuple[int, int, int, int]] = []
    for i in range(4):
        for j in range(4):
            if j == i: continue
            for k in range(4):
                if k in (i, j): continue
                for l in range(4):
                    if l in (i, j, k): continue
                    perms.append((i, j, k, l))
    return tuple(perms)


# Кэшируем перестановки один раз при загрузке модуля
_PERM_DIRS = _precompute_permutations()


@dataclass(slots=True, frozen=True)
class Maze:
    """
    Неизменяемая структура данных, представляющая сгенерированный лабиринт.
    Использует slots=True для экономии памяти и быстрого доступа к атрибутам.
    
    Attributes:
        width: Ширина лабиринта в ячейках.
        height: Высота лабиринта в ячейках.
        grid: Одномерный массив байтов (bytearray), хранящий состояния ячеек.
    """
    width: int
    height: int
    grid: bytearray

    def render_to_string(self) -> str:
        """
        Преобразует лабиринт в ASCII-строку для отображения в консоли.
        
        Returns:
            Строковое представление лабиринта.
        """
        lines: List[str] = []
        
        # Верхняя граница
        lines.append(" _" * self.width)
        
        for row in range(self.height):
            row_chars: List[str] = ['|']
            for col in range(self.width):
                idx = row * self.width + col
                cell = self.grid[idx]
                
                # Нижняя стена (DOWN)
                if cell & CellState.DOWN:
                    row_chars.append(" ")
                else:
                    row_chars.append("_")
                
                # Правая стена (RIGHT)
                if cell & CellState.RIGHT:
                    next_cell = self.grid[idx + 1]
                    # Если путь открыт в обе стороны (вправо и у соседней ячейки вниз)
                    if (cell | next_cell) & CellState.DOWN:
                        row_chars.append(" ")
                    else:
                        row_chars.append("_")
                else:
                    row_chars.append("|")
                    
            lines.append("".join(row_chars))
            
        return "\n".join(lines)


class FastMazeGenerator:
    """Генератор лабиринтов с оптимизацией под интерпретатор Python."""

    def generate(self, width: int, height: int, seed: Optional[int] = None) -> Maze:
        """
        Генерирует лабиринт заданного размера.

        Args:
            width: Ширина лабиринта (> 0).
            height: Высота лабиринта (> 0).
            seed: Опциональный сид для воспроизводимости (random seed).

        Returns:
            Объект Maze, содержащий размеры и массив с состоянием каждой ячейки.

        Raises:
            ValueError: Если размеры лабиринта меньше или равны нулю.
        """
        if width <= 0 or height <= 0:
            raise ValueError(f"Размеры лабиринта должны быть положительными, получено: {width}x{height}")

        total_cells = width * height
        
        # bytearray — идеальный C-подобный тип. Тратит ровно 1 байт на ячейку,
        # в то время как обычный list[int] тратил бы ~28 байт на каждый элемент.
        grid = bytearray(total_cells)
        
        rng = random.Random(seed) if seed is not None else random
        rand_choice = rng.choice  # Кэшируем метод для скорости
        
        # Стек реализован через встроенный список. append и pop работают за O(1).
        # Элементы: (index, row, col)
        stack: List[Tuple[int, int, int]] = [(0, 0, 0)]
        grid[0] = CellState.VISITED

        # --- МИКРООПТИМИЗАЦИИ ДЛЯ HOT LOOP ---
        # В CPython обращение к локальным переменным (LOAD_FAST) работает быстрее,
        # чем к глобальным (LOAD_GLOBAL) или атрибутам объектов (LOAD_ATTR).
        d_row = _D_ROW
        d_col = _D_COL
        d_idx = (-width, 1, width, -1)
        carve = _CARVE
        opp = _OPPOSITE
        perms = _PERM_DIRS
        
        stack_append = stack.append
        stack_pop = stack.pop

        # Основной цикл (DFS / Recursive Backtracker)
        while stack:
            idx, row, col = stack[-1]  # Peek без удаления
            moved = False

            # Выбор случайной заранее заготовленной перестановки направлений
            for d in rand_choice(perms):
                n_row = row + d_row[d]
                n_col = col + d_col[d]

                # Pythonic "цепочечное" сравнение быстрее, чем ручные ветвления
                if 0 <= n_row < height and 0 <= n_col < width:
                    n_idx = idx + d_idx[d]

                    # Проверяем, была ли посещена ячейка (проверка бита VISITED)
                    if not (grid[n_idx] & CellState.VISITED):
                        # Ломаем стены между текущей и следующей ячейкой, отмечаем как посещенную
                        grid[idx] |= carve[d]
                        grid[n_idx] |= opp[d] | CellState.VISITED

                        stack_append((n_idx, n_row, n_col))
                        moved = True
                        break

            # Если мы не сдвинулись ни в одном из направлений — откатываемся
            if not moved:
                stack_pop()

        return Maze(width, height, grid)


# Пример использования (запускается при вызове напрямую)
if __name__ == "__main__":
    import time
    
    print("Генерация лабиринта 15x5...")
    generator = FastMazeGenerator()
    maze = generator.generate(15, 5, seed=42)
    print(maze.render_to_string())

    print("\nСтресс-тест 2000x2000...")
    start_time = time.time()
    big_maze = generator.generate(2000, 2000)
    elapsed = time.time() - start_time
    
    print(f"Сгенерировано 4 000 000 ячеек за {elapsed:.3f} секунд.")
    # Использование памяти:
    print(f"Размер сетки (grid) в памяти: {len(big_maze.grid) / 1024 / 1024:.2f} МБ")