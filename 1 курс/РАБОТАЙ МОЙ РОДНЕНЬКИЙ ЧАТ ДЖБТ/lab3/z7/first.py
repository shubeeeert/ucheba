import random
from enum import IntFlag
from dataclasses import dataclass

class CellState(IntFlag):
    NONE = 0
    NORTH = 1 << 0
    EAST = 1 << 1
    SOUTH = 1 << 2
    WEST = 1 << 3
    VISITED = 1 << 4

# Константы выносятся на уровень модуля для ускорения доступа в hot loop
_CARVE = (CellState.NORTH, CellState.EAST, CellState.SOUTH, CellState.WEST)
_OPPOSITE = (CellState.SOUTH, CellState.WEST, CellState.NORTH, CellState.EAST)
_D_ROW = (-1, 0, 1, 0)
_D_COL = (0, 1, 0, -1)

# Предрасчет перестановок (как в C#)
_PERM_DIRS = []
for i in range(4):
    for j in range(4):
        if j == i: continue
        for k in range(4):
            if k in (i, j): continue
            for l in range(4):
                if l in (i, j, k): continue
                _PERM_DIRS.append((i, j, k, l)) # Группируем в кортежи

@dataclass(slots=True, frozen=True)
class Maze:
    width: int
    height: int
    grid: bytearray

    def render_to_string(self) -> str:
        # Логика рендеринга переносится прямолинейно,
        # string builder заменяется на список строк + join()
        pass

class FastMazeGenerator:
    def generate(self, width: int, height: int, seed: int | None = None) -> Maze:
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive.")
        
        total_cells = width * height
        # Используем bytearray для экономии памяти и кэш-локальности
        grid = bytearray(total_cells)
        
        rng = random.Random(seed) if seed is not None else random
        rand_choice = rng.choice # Кэшируем метод для скорости

        # Инициализация
        stack = [(0, 0, 0)] # (idx, row, col)
        grid[0] = CellState.VISITED
        
        # Кэшируем глобальные переменные локально (ускоряет доступ в CPython на 15-20%)
        d_row = _D_ROW
        d_col = _D_COL
        carve = _CARVE
        opp = _OPPOSITE
        perms = _PERM_DIRS
        
        # Инлайнинг dIdx
        d_idx = (-width, 1, width, -1)

        # Методы списка написаны на C, сохраняем ссылки на них
        stack_append = stack.append
        stack_pop = stack.pop

        while stack:
            idx, row, col = stack[-1]
            moved = False
            
            # rand_choice по заранее сгруппированным кортежам быстрее, 
            # чем математика со сдвигами в Python
            for d in rand_choice(perms):
                n_row = row + d_row[d]
                n_col = col + d_col[d]
                
                # Chain comparisons (быстрее, чем branchless bitwise в Python)
                if 0 <= n_row < height and 0 <= n_col < width:
                    n_idx = idx + d_idx[d]
                    
                    if not (grid[n_idx] & CellState.VISITED):
                        grid[idx] |= carve[d]
                        grid[n_idx] |= (opp[d] | CellState.VISITED)
                        
                        stack_append((n_idx, n_row, n_col))
                        moved = True
                        break
            
            if not moved:
                stack_pop()

        return Maze(width, height, grid)