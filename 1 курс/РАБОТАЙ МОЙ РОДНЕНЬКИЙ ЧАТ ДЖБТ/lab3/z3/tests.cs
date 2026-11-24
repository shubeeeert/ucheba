using System;
using System.Linq;
using Xunit;
using HpcMazeGenerator;

namespace MazeTests
{
    public class MazeGeneratorTests
    {
        private readonly FastMazeGenerator _generator = new FastMazeGenerator();

        [Theory]
        [InlineData(0, 10)]
        [InlineData(10, 0)]
        [InlineData(-5, 10)]
        public void Generate_InvalidDimensions_ThrowsArgumentOutOfRangeException(int width, int height)
        {
            Assert.Throws<ArgumentOutOfRangeException>(() => _generator.Generate(width, height));
        }

        [Fact]
        public void Generate_ArithmeticOverflowDimensions_ThrowsArgumentException()
        {
            Assert.Throws<ArgumentException>(() => _generator.Generate(46000, 46000)); 
        }

        [Fact]
        public void Generate_ValidDimensions_SetsPropertiesCorrectly()
        {
            int w = 15;
            int h = 20;

            var maze = _generator.Generate(w, h);

            Assert.Equal(w, maze.Width);
            Assert.Equal(h, maze.Height);
            Assert.Equal(w * h, maze.Grid.Length);
        }

        [Fact]
        public void Generate_WithSameSeed_ProducesIdenticalMazes()
        {
            int w = 50, h = 50, seed = 12345;

            var maze1 = _generator.Generate(w, h, seed);
            var maze2 = _generator.Generate(w, h, seed);

            Assert.True(maze1.Grid.SequenceEqual(maze2.Grid));
        }

        [Fact]
        public void Generate_WithDifferentSeeds_ProducesDifferentMazes()
        {
            int w = 50, h = 50;

            var maze1 = _generator.Generate(w, h, 1);
            var maze2 = _generator.Generate(w, h, 2);

            Assert.False(maze1.Grid.SequenceEqual(maze2.Grid));
        }

        [Theory]
        [InlineData(10, 10)]
        [InlineData(100, 50)]
        public void MazeLogic_AllCellsAreVisited(int width, int height)
        {
            var maze = _generator.Generate(width, height);

            for (int i = 0; i < maze.Grid.Length; i++)
            {
                bool isVisited = (maze.Grid[i] & (int)CellState.Visited) != 0;
                Assert.True(isVisited, $"Cell at index {i} was not visited.");
            }
        }

        [Fact]
        public void MazeLogic_BoundariesAreClosed()
        {
            int w = 20, h = 20;
            var maze = _generator.Generate(w, h);

            for (int col = 0; col < w; col++)
            {
                Assert.False(HasFlag(maze.Grid[0 * w + col], CellState.North));
                Assert.False(HasFlag(maze.Grid[(h - 1) * w + col], CellState.South));
            }

            for (int row = 0; row < h; row++)
            {
                Assert.False(HasFlag(maze.Grid[row * w + 0], CellState.West));
                Assert.False(HasFlag(maze.Grid[row * w + (w - 1)], CellState.East));
            }
        }

        [Fact]
        public void MazeLogic_ConnectionsAreBidirectional()
        {
            int w = 30, h = 30;
            var maze = _generator.Generate(w, h);

            for (int row = 0; row < h; row++)
            {
                for (int col = 0; col < w; col++)
                {
                    int currentCell = maze.Grid[row * w + col];

                    if (HasFlag(currentCell, CellState.East))
                    {
                        int rightCell = maze.Grid[row * w + (col + 1)];
                        Assert.True(HasFlag(rightCell, CellState.West), $"Cell at [{row},{col}] goes East, but right cell doesn't go West.");
                    }

                    if (HasFlag(currentCell, CellState.South))
                    {
                        int bottomCell = maze.Grid[(row + 1) * w + col];
                        Assert.True(HasFlag(bottomCell, CellState.North), $"Cell at [{row},{col}] goes South, but bottom cell doesn't go North.");
                    }
                }
            }
        }

        [Fact]
        public void MazeLogic_IsPerfectMaze_HasExactNumberOfEdges()
        {
            int w = 50, h = 50;
            int totalVertices = w * h;
            int expectedTotalDoors = (totalVertices - 1) * 2;
            var maze = _generator.Generate(w, h);

            int actualTotalDoors = 0;

            for (int i = 0; i < maze.Grid.Length; i++)
            {
                int cell = maze.Grid[i];
                if (HasFlag(cell, CellState.North)) actualTotalDoors++;
                if (HasFlag(cell, CellState.East)) actualTotalDoors++;
                if (HasFlag(cell, CellState.South)) actualTotalDoors++;
                if (HasFlag(cell, CellState.West)) actualTotalDoors++;
            }

            Assert.Equal(expectedTotalDoors, actualTotalDoors);
        }

        [Fact]
        public void RenderToString_DoesNotThrow()
        {
            var maze = _generator.Generate(5, 5);

            var result = Record.Exception(() => maze.RenderToString());

            Assert.Null(result);
            Assert.NotEmpty(maze.RenderToString());
        }

        private static bool HasFlag(int cellValue, CellState flag)
        {
            return (cellValue & (int)flag) != 0;
        }
    }
}