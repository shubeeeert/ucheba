using System;

namespace VideoGamesApp
{
    /// <summary>
    /// Класс сущности «Видеоигра» (дочерняя таблица lab_schema.game)
    /// </summary>
    public class Game
    {
        public long? Id { get; set; }
        public string Title { get; set; }
        public long DeveloperId { get; set; }
        public string DeveloperName { get; set; }
        public int ReleaseYear { get; set; }
        public decimal Price { get; set; }
        public bool IsReleased { get; set; }

        public Game() { }

        public Game(long? id, string title, long developerId, string developerName, int releaseYear, decimal price, bool isReleased)
        {
            Id = id;
            Title = title;
            DeveloperId = developerId;
            DeveloperName = developerName;
            ReleaseYear = releaseYear;
            Price = price;
            IsReleased = isReleased;
        }
    }
}
