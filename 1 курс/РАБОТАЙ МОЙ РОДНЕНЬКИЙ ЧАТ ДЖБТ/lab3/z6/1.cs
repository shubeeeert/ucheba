using System;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Text;

namespace HpcMazeGenerator
{
    /// <summary>
    /// Defines bit flags for the maze cell state and passage availability.
    /// </summary>
    /// <remarks>
    /// Cell states are combined using bitwise operations to achieve maximum performance. 
    /// Computational complexity of state operations: Time O(1), Space O(1).
    /// </remarks>
    [Flags]
    public enum CellState : int
    {
        /// <summary>The cell has no passages and has not been visited.</summary>
        None = 0,
        /// <summary>A passage in the North direction.</summary>
        North = 1 << 0,
        /// <summary>A passage in the East direction.</summary>
        East = 1 << 1,
        /// <summary>A passage in the South direction.</summary>
        South = 1 << 2,
        /// <summary>A passage in the West direction.</summary>
        West = 1 << 3,
        /// <summary>A flag indicating that the cell has been visited by the generation algorithm.</summary>
        Visited = 1 << 4
    }

    /// <summary>
    /// Represents a generated maze as a two-dimensional grid.
    /// </summary>
    /// <remarks>
    /// This struct encapsulates the maze dimensions and its data. Data is stored as a one-dimensional array 
    /// to improve CPU cache locality.
    /// Space complexity of an instance: O(W * H), where W is width, H is height.
    /// </remarks>
    public readonly struct Maze
    {
        /// <summary>The width of the maze in cells.</summary>
        public readonly int Width;
        
        /// <summary>The height of the maze in cells.</summary>
        public readonly int Height;
        
        /// <summary>A one-dimensional array representing the 2D grid of maze cells.</summary>
        public readonly int[] Grid;

        /// <summary>
        /// Initializes a new instance of the <see cref="Maze"/> struct.
        /// </summary>
        /// <param name="width">The width of the maze.</param>
        /// <param name="height">The height of the maze.</param>
        /// <param name="grid">A one-dimensional array of cell states of size width * height.</param>
        /// <remarks>
        /// Time complexity: O(1).
        /// Space complexity: O(1) (the array is passed by reference).
        /// </remarks>
        public Maze(int width, int height, int[] grid)
        {
            Width = width;
            Height = height;
            Grid = grid;
        }

        /// <summary>
        /// Generates an ASCII string representation of the maze.
        /// </summary>
        /// <returns>A string containing the visual representation of the maze.</returns>
        /// <remarks>
        /// The algorithm iterates over all grid cells and formats the maze walls using a <see cref="StringBuilder"/>.
        /// Time complexity: O(W * H), where W is width, H is height.
        /// Space complexity: O(W * H) to allocate memory for the resulting string.
        /// </remarks>
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

    /// <summary>
    /// Provides a high-performance maze generator with minimal memory allocations.
    /// </summary>
    /// <remarks>
    /// The class implements an optimized iterative Randomized Depth-First Search (recursive backtracker) algorithm.
    /// Using arrays as a stack and applying <see cref="Unsafe"/> and <see cref="MemoryMarshal"/> methods 
    /// eliminates the overhead of recursive calls and array bounds checking.
    /// Precomputed direction permutations in the static constructor eliminate the need 
    /// to shuffle collections during the algorithm's execution.
    /// </remarks>
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

        /// <summary>
        /// Generates a maze of the specified size using an iterative DFS algorithm.
        /// </summary>
        /// <param name="width">The width of the maze. Must be greater than zero.</param>
        /// <param name="height">The height of the maze. Must be greater than zero.</param>
        /// <param name="seed">An optional seed value for the pseudo-random number generator. Allows generating deterministic mazes.</param>
        /// <returns>A <see cref="Maze"/> instance containing the generated grid and maze dimensions.</returns>
        /// <exception cref="ArgumentOutOfRangeException">Thrown when <paramref name="width"/> or <paramref name="height"/> is less than or equal to zero.</exception>
        /// <exception cref="ArgumentException">Thrown if the product of width and height causes an arithmetic overflow or exceeds the traversal stack size limits.</exception>
        /// <remarks>
        /// The algorithm traverses the cells using its own flat stack array, completely preventing StackOverflowException.
        /// Out-of-bounds calculations are performed branchlessly using bitwise shifts and masks.
        /// 
        /// Time complexity: O(W * H), where W is the width and H is the height of the maze, since each cell is pushed to and popped from the stack a fixed number of times.
        /// Space complexity: O(W * H) for allocating memory for the grid and the algorithm's local stack arrays.
        /// </remarks>
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