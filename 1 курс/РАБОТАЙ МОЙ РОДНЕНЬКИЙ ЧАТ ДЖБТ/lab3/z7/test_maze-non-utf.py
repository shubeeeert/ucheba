"""
Модульные тесты для FastMazeGenerator.
Проверяет связность лабиринта (BFS), обработку исключений и корректность битовых масок.
"""

import unittest
from collections import deque
from maze_generator import FastMazeGenerator, CellState


class TestMazeGenerator(unittest.TestCase):
    """Тестовые сценарии для проверки логики генерации лабиринта."""

    def setUp(self):
        """Инициализация перед каждым тестом."""
        self.generator = FastMazeGenerator()

    def test_connectivity_bfs(self):
        """
        Проверка связности графа на примере 3x3.
        Использует Breadth-First Search (BFS), чтобы убедиться, что из стартовой
        клетки (0, 0) можно добраться до любой другой клетки лабиринта.
        """
        width, height = 3, 3
        maze = self.generator.generate(width, height, seed=42)
        
        visited_cells = set()
        queue = deque([0])  # Начинаем с индекса 0
        visited_cells.add(0)
        
        while queue:
            curr_idx = queue.popleft()
            cell = maze.grid[curr_idx]
            
            # Проверка пути вверх (UP)
            if cell & CellState.UP:
                neighbor = curr_idx - width
                if neighbor not in visited_cells:
                    visited_cells.add(neighbor)
                    queue.append(neighbor)
                    
            # Проверка пути вправо (RIGHT)
            if cell & CellState.RIGHT:
                neighbor = curr_idx + 1
                if neighbor not in visited_cells:
                    visited_cells.add(neighbor)
                    queue.append(neighbor)
                    
            # Проверка пути вниз (DOWN)
            if cell & CellState.DOWN:
                neighbor = curr_idx + width
                if neighbor not in visited_cells:
                    visited_cells.add(neighbor)
                    queue.append(neighbor)
                    
            # Проверка пути влево (LEFT)
            if cell & CellState.LEFT:
                neighbor = curr_idx - 1
                if neighbor not in visited_cells:
                    visited_cells.add(neighbor)
                    queue.append(neighbor)

        # Проверяем, что алгоритм обошел все клетки
        self.assertEqual(
            len(visited_cells), width * height,
            "Не все клетки достижимы. Лабиринт содержит изолированные зоны."
        )

    def test_invalid_dimensions(self):
        """Проверка генерации исключения ValueError при некорректных размерах."""
        with self.assertRaises(ValueError):
            self.generator.generate(-5, 10)
            
        with self.assertRaises(ValueError):
            self.generator.generate(10, 0)

    def test_bitmasks_and_boundaries(self):
        """
        Проверка корректности битовых масок стен и границ лабиринта.
        - Ни одна клетка на границах не должна вести "наружу".
        - Пути между соседними клетками должны быть взаимными (reciprocal).
        - Все клетки должны быть помечены как посещенные.
        """
        width, height = 4, 4
        maze = self.generator.generate(width, height, seed=123)
        
        for r in range(height):
            for c in range(width):
                idx = r * width + c
                cell = maze.grid[idx]
                
                # 1. Все клетки должны быть помечены как посещенные
                self.assertTrue(
                    cell & CellState.VISITED, 
                    f"Клетка ({r}, {c}) не помечена как посещенная."
                )
                
                # 2. Проверка границ (стен на краях сетки быть не должно)
                if r == 0:
                    self.assertFalse(cell & CellState.UP, f"Клетка ({r}, {c}) имеет выход за верхнюю границу.")
                if r == height - 1:
                    self.assertFalse(cell & CellState.DOWN, f"Клетка ({r}, {c}) имеет выход за нижнюю границу.")
                if c == 0:
                    self.assertFalse(cell & CellState.LEFT, f"Клетка ({r}, {c}) имеет выход за левую границу.")
                if c == width - 1:
                    self.assertFalse(cell & CellState.RIGHT, f"Клетка ({r}, {c}) имеет выход за правую границу.")
                
                # 3. Взаимность путей (если есть проход вправо, у правого соседа должен быть проход влево)
                if cell & CellState.RIGHT:
                    right_neighbor = maze.grid[idx + 1]
                    self.assertTrue(
                        right_neighbor & CellState.LEFT, 
                        f"У клетки ({r}, {c}) пробит путь вправо, но у соседа нет пути влево."
                    )
                    
                if cell & CellState.DOWN:
                    down_neighbor = maze.grid[idx + width]
                    self.assertTrue(
                        down_neighbor & CellState.UP, 
                        f"У клетки ({r}, {c}) пробит путь вниз, но у соседа нет пути вверх."
                    )


# =====================================================================
# Кастомный Test Runner для красивого вывода статуса [PASS] / [FAIL]
# =====================================================================
class PassFailTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        super().addSuccess(test)
        print(f"[PASS] {test._testMethodName}")
        
    def addFailure(self, test, err):
        super().addFailure(test, err)
        print(f"[FAIL] {test._testMethodName}")
        
    def addError(self, test, err):
        super().addError(test, err)
        print(f"[ERROR] {test._testMethodName}")


if __name__ == '__main__':
    # Запускаем тесты с нашим кастомным выводом
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMazeGenerator)
    runner = unittest.TextTestRunner(resultclass=PassFailTestResult, verbosity=0)
    
    print("=== Запуск тестов MazeGeneratorPython ===")
    result = runner.run(suite)
    print("=========================================")
    
    # Завершаем скрипт с корректным кодом возврата для CI/CD
    if not result.wasSuccessful():
        exit(1)