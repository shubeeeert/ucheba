using System;

namespace VideoGamesApp
{
    /// <summary>
    /// Класс сущности «Разработчик» (родительская таблица lab_schema.developer)
    /// </summary>
    public class Developer
    {
        public long Id { get; set; }
        public string Name { get; set; }

        public Developer() { }

        public Developer(long id, string name)
        {
            Id = id;
            Name = name;
        }

        public override string ToString()
        {
            return Name;
        }
    }
}
