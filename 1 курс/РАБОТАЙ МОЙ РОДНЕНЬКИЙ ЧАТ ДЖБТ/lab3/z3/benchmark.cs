using System;
using BenchmarkDotNet.Attributes;
using BenchmarkDotNet.Running;
using HpcMazeGenerator;

namespace MazeBenchmark
{
    [MemoryDiagnoser]
    [SimpleJob(launchCount: 1, warmupCount: 3, iterationCount: 5)]
    [MinColumn, MaxColumn, MeanColumn, MedianColumn]
    public class MazeGeneratorBenchmark
    {
        private FastMazeGenerator _generator;
        private const int Seed = 42;

        [Params(100, 500, 2000)]
        public int Size { get; set; }

        [GlobalSetup]
        public void Setup()
        {
            _generator = new FastMazeGenerator();
        }

        [Benchmark(Baseline = true)]
        public Maze GenerateFastMaze()
        {
            return _generator.Generate(Size, Size, Seed);
        }
    }

    class Program
    {
        static void Main(string[] args)
        {
            BenchmarkRunner.Run<MazeGeneratorBenchmark>();
        }
    }
}