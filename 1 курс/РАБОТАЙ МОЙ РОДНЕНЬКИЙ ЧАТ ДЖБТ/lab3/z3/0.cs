using System;
using System.Runtime.CompilerServices;
using System.Text;

namespace HpcMazeGenerator
{
    [Flags]
    public enum CellState : byte
    {
        None = 0,
        North = 1 << 0, // 1
        East  = 1 << 1, // 2
        South = 1 << 2, // 4
        West  = 1 << 3, // 8
        Visited = 1 << 4 // 16
    }
    public readonly struct Maze
    {
        public readonly int Width;
        public readonly int Height;
        public readonly byte[] Grid;

        public Maze(int width, int height, byte[] grid)
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

            for (int y = 0; y < Height; y++)
            {
                sb.Append('|'); 
                for (int x = 0; x < Width; x++)
                {
                    CellState cell = (CellState)Grid[y * Width + x];
                    
                    sb.Append(cell.HasFlag(CellState.South) ? " " : "_");
                    
                    if (cell.HasFlag(CellState.East))
                        sb.Append(((cell | (CellState)Grid[y * Width + x + 1]).HasFlag(CellState.South)) ? " " : "_");
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
        private static readonly int[] DX = { 0, 1, 0, -1 };
        private static readonly int[] DY = { -1, 0, 1, 0 };
        private static readonly CellState[] CARVE = { CellState.North, CellState.East, CellState.South, CellState.West };
        private static readonly CellState[] OPPOSITE = { CellState.South, CellState.West, CellState.North, CellState.East };

        public Maze Generate(int width, int height, int? seed = null)
        {
            if (width <= 0) throw new ArgumentOutOfRangeException(nameof(width), "Width must be > 0.");
            if (height <= 0) throw new ArgumentOutOfRangeException(nameof(height), "Height must be > 0.");

            int totalCells = width * height;
            
            byte[] grid = new byte[totalCells];
            int[] stack = new int[totalCells]; 
            int stackPointer = 0;

            Random rng = seed.HasValue ? new Random(seed.Value) : Random.Shared;

            int currentIdx = 0;
            grid[currentIdx] |= (byte)CellState.Visited;
            stack[stackPointer++] = currentIdx; // Push

            while (stackPointer > 0)
            {
                currentIdx = stack[stackPointer - 1];
                int cx = currentIdx % width;
                int cy = currentIdx / width;

                Span<int> dirs = stackalloc int[4] { 0, 1, 2, 3 };
                
                for (int i = 3; i > 0; i--)
                {
                    int j = rng.Next(i + 1);
                    (dirs[i], dirs[j]) = (dirs[j], dirs[i]);
                }

                bool moved = false;

                for (int i = 0; i < 4; i++)
                {
                    int d = dirs[i];
                    int nx = cx + DX[d];
                    int ny = cy + DY[d];

                    if ((uint)nx < (uint)width && (uint)ny < (uint)height)
                    {
                        int neighborIdx = ny * width + nx;

                        if ((grid[neighborIdx] & (byte)CellState.Visited) == 0)
                        {
                            grid[currentIdx] |= (byte)CARVE[d];
                            grid[neighborIdx] |= (byte)(OPPOSITE[d] | CellState.Visited);

                            stack[stackPointer++] = neighborIdx;
                            moved = true;
                            break; 
                        }
                    }
                }

                if (!moved)
                {
                    stackPointer--;
                }
            }

            return new Maze(width, height, grid);
        }

        [MethodImpl(MethodImplOptions.AggressiveInlining)]
        private static int GetIndex(int x, int y, int width) => y * width + x;
    }
}