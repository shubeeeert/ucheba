using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;

namespace HpcMazeGenerator
{
    [Flags]
    public enum CellState : int
    {
        None = 0,
        North = 1 << 0,
        East = 1 << 1,
        South = 1 << 2,
        West = 1 << 3,
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
        private static readonly int[] PermDirs = new int[96];
        private static readonly int[] DRow = { -1, 0, 1, 0 };
        private static readonly int[] DCol = { 0, 1, 0, -1 };
        private static readonly int[] CARVE = { (int)CellState.North, (int)CellState.East, (int)CellState.South, (int)CellState.West };
        private static readonly int[] OPPOSITE = { (int)CellState.South, (int)CellState.West, (int)CellState.North, (int)CellState.East };

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
                            PermDirs[count++] = i;
                            PermDirs[count++] = j;
                            PermDirs[count++] = k;
                            PermDirs[count++] = l;
                        }
                    }
                }
        }

        public Maze Generate(int width, int height, int? seed = null)
        {
            if (width <= 0) throw new ArgumentOutOfRangeException(nameof(width));
            if (height <= 0) throw new ArgumentOutOfRangeException(nameof(height));

            long totalCellsLong = (long)width * height;
            if (totalCellsLong > int.MaxValue / 3)
            {
                throw new ArgumentException("Dimensions cause arithmetic overflow.");
            }

            int totalCells = (int)totalCellsLong;
            int[] grid = new int[totalCells];
            int[] stack = new int[totalCells * 3];
            int[] dIdx = { -width, 1, width, -1 };

            var rng = seed.HasValue ? new Random(seed.Value) : Random.Shared;

            int ptr = 0;
            stack[ptr++] = 0;
            stack[ptr++] = 0;
            stack[ptr++] = 0;
            grid[0] = (int)CellState.Visited;

            ref int gridRef = ref MemoryMarshal.GetArrayDataReference(grid);
            ref int stackRef = ref MemoryMarshal.GetArrayDataReference(stack);
            ref int permRef = ref MemoryMarshal.GetArrayDataReference(PermDirs);
            ref int dRowRef = ref MemoryMarshal.GetArrayDataReference(DRow);
            ref int dColRef = ref MemoryMarshal.GetArrayDataReference(DCol);
            ref int dIdxRef = ref MemoryMarshal.GetArrayDataReference(dIdx);
            ref int carveRef = ref MemoryMarshal.GetArrayDataReference(CARVE);
            ref int oppRef = ref MemoryMarshal.GetArrayDataReference(OPPOSITE);

            int hMinus1 = height - 1;
            int wMinus1 = width - 1;

            while (ptr > 0)
            {
                int col = Unsafe.Add(ref stackRef, ptr - 1);
                int row = Unsafe.Add(ref stackRef, ptr - 2);
                int idx = Unsafe.Add(ref stackRef, ptr - 3);

                bool moved = false;
                int pOffset = rng.Next(24) << 2;

                for (int i = 0; i < 4; i++)
                {
                    int d = Unsafe.Add(ref permRef, pOffset + i);

                    int nRow = row + Unsafe.Add(ref dRowRef, d);
                    int nCol = col + Unsafe.Add(ref dColRef, d);
                    int nIdx = idx + Unsafe.Add(ref dIdxRef, d);

                    int oobRow = (nRow | (hMinus1 - nRow)) >> 31;
                    int oobCol = (nCol | (wMinus1 - nCol)) >> 31;
                    int safeIdx = nIdx & ~(oobRow | oobCol);

                    if ((Unsafe.Add(ref gridRef, safeIdx) & 16) == 0)
                    {
                        Unsafe.Add(ref gridRef, idx) |= Unsafe.Add(ref carveRef, d);
                        Unsafe.Add(ref gridRef, safeIdx) |= (Unsafe.Add(ref oppRef, d) | 16);

                        Unsafe.Add(ref stackRef, ptr) = nIdx;
                        Unsafe.Add(ref stackRef, ptr + 1) = nRow;
                        Unsafe.Add(ref stackRef, ptr + 2) = nCol;
                        ptr += 3;

                        moved = true;
                        break;
                    }
                }

                if (!moved)
                {
                    ptr -= 3;
                }
            }

            return new Maze(width, height, grid);
        }
    }
}