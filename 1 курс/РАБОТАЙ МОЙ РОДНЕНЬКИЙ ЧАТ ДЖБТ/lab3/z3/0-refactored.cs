using System;
using System.Collections.Generic;
using System.Text;

namespace HpcMazeGenerator
{
    [Flags]
    public enum CellState : int
    {
        None = 0,
        North = 1 << 0,
        East  = 1 << 1,
        South = 1 << 2,
        West  = 1 << 3,
        Visited = 1 << 4
    }

    public readonly struct Maze
    {
        public readonly int Width;
        public readonly int Height;
        public readonly int[] Grid;

        public Maze(int width, int height, int[] grid)
        {
            Width = width;
            Height = height;
            Grid = grid;
        }

        public string RenderToString()
        {
            var sb = new StringBuilder();
            for (int i = 0; i < Width; i++) sb.Append(" _");
            sb.AppendLine();

            for (int row = 0; row < Height; row++)
            {
                sb.Append('|');
                for (int col = 0; col < Width; col++)
                {
                    CellState cell = (CellState)Grid[row * Width + col];
                    
                    sb.Append(cell.HasFlag(CellState.South) ? " " : "_");
                    
                    if (cell.HasFlag(CellState.East))
                        sb.Append(((cell | (CellState)Grid[row * Width + col + 1]).HasFlag(CellState.South)) ? " " : "_");
                    else
                        sb.Append('|');
                }
                sb.AppendLine();
            }
            return sb.ToString();
        }
    }

    public sealed class FastMazeGenerator
    {
        private static readonly int[] DRow = { -1, 0, 1, 0 };
        private static readonly int[] DCol = { 0, 1, 0, -1 };
        private static readonly CellState[] CARVE = { CellState.North, CellState.East, CellState.South, CellState.West };
        private static readonly CellState[] OPPOSITE = { CellState.South, CellState.West, CellState.North, CellState.East };

        private static readonly int[][] Permutations = new int[24][];

        static FastMazeGenerator()
        {
            int count = 0;
            for (int i = 0; i < 4; i++)
                for (int j = 0; j < 4; j++)
                {
                    if (j == i) continue;
                    for (int k = 0; k < 4; k++)
                    {
                        if (k == i || k == j) continue;
                        for (int l = 0; l < 4; l++)
                        {
                            if (l == i || l == j || l == k) continue;
                            Permutations[count++] = new int[] { i, j, k, l };
                        }
                    }
                }
        }

        public Maze Generate(int width, int height, int? seed = null)
        {
            if (width <= 0) throw new ArgumentOutOfRangeException(nameof(width));
            if (height <= 0) throw new ArgumentOutOfRangeException(nameof(height));

            long totalCellsLong = (long)width * height;
            if (totalCellsLong > int.MaxValue)
            {
                throw new ArgumentException("Dimensions cause arithmetic overflow.");
            }
            
            int totalCells = (int)totalCellsLong;
            int[] grid = new int[totalCells];
            var rng = seed.HasValue ? new Random(seed.Value) : Random.Shared;
            var stack = new Stack<(int row, int col)>(totalCells / 4);

            int startRow = 0;
            int startCol = 0;
            grid[startRow * width + startCol] |= (int)CellState.Visited;
            stack.Push((startRow, startCol));

            while (stack.Count > 0)
            {
                var (row, col) = stack.Peek();
                int currentIdx = row * width + col;
                bool moved = false;
                
                int[] dirs = Permutations[rng.Next(24)];

                for (int i = 0; i < 4; i++)
                {
                    int d = dirs[i];
                    int nRow = row + DRow[d];
                    int nCol = col + DCol[d];

                    if ((uint)nRow < (uint)height && (uint)nCol < (uint)width)
                    {
                        int neighborIdx = nRow * width + nCol;

                        if ((grid[neighborIdx] & (int)CellState.Visited) == 0)
                        {
                            grid[currentIdx] |= (int)CARVE[d];
                            grid[neighborIdx] |= (int)(OPPOSITE[d] | CellState.Visited);

                            stack.Push((nRow, nCol));
                            moved = true;
                            break;
                        }
                    }
                }

                if (!moved)
                {
                    stack.Pop();
                }
            }

            return new Maze(width, height, grid);
        }
    }
}