using System;
using System.Collections.Generic;
using Npgsql;
using NpgsqlTypes;

namespace VideoGamesApp
{
    /// <summary>
    /// Репозиторий для работы с таблицей видеоигр (lab_schema.game)
    /// </summary>
    public class GameRepository
    {
        private readonly DbConnectionFactory _connectionFactory;

        public GameRepository(DbConnectionFactory connectionFactory)
        {
            _connectionFactory = connectionFactory;
        }

        // Получение всех записей таблицы game с названиями разработчиков
        public List<Game> GetAll()
        {
            List<Game> games = new List<Game>();
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand("SELECT * FROM lab_schema.get_games_with_developers()", conn);
                NpgsqlDataReader reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    games.Add(new Game(
                        reader.GetInt64(0),
                        reader.GetString(1),
                        0,
                        reader.GetString(2),
                        reader.GetInt32(3),
                        reader.GetDecimal(4),
                        reader.GetBoolean(5)
                    ));
                }
                reader.Close();
            }
            finally
            {
                conn.Close();
            }
            return games;
        }

        // Регистронезависимая фильтрация записей по названию через запрос к БД (используется UPPER)
        public List<Game> FilterByTitle(string titlePattern)
        {
            List<Game> games = new List<Game>();
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand("SELECT * FROM lab_schema.filter_games_by_title(@pattern)", conn);
                NpgsqlParameter paramPattern = new NpgsqlParameter("@pattern", NpgsqlDbType.Varchar);
                paramPattern.Value = "%" + titlePattern + "%";
                cmd.Parameters.Add(paramPattern);

                NpgsqlDataReader reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    games.Add(new Game(
                        reader.GetInt64(0),
                        reader.GetString(1),
                        0,
                        reader.GetString(2),
                        reader.GetInt32(3),
                        reader.GetDecimal(4),
                        reader.GetBoolean(5)
                    ));
                }
                reader.Close();
            }
            finally
            {
                conn.Close();
            }
            return games;
        }

        // Проверка наличия дубликата в БД (без учёта регистра)
        public bool ExistsByTitle(string title, long? excludeId = null)
        {
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                string sql = @"SELECT EXISTS (
                    SELECT 1 FROM lab_schema.game
                    WHERE UPPER(TRIM(title)) = UPPER(TRIM(@title))
                      AND (@exclude_id IS NULL OR id <> @exclude_id)
                )";
                NpgsqlCommand cmd = new NpgsqlCommand(sql, conn);

                NpgsqlParameter paramTitle = new NpgsqlParameter("@title", NpgsqlDbType.Varchar);
                paramTitle.Value = title.Trim();
                cmd.Parameters.Add(paramTitle);

                NpgsqlParameter paramExcludeId = new NpgsqlParameter("@exclude_id", NpgsqlDbType.Bigint);
                paramExcludeId.Value = excludeId.HasValue ? (object)excludeId.Value : DBNull.Value;
                cmd.Parameters.Add(paramExcludeId);

                object result = cmd.ExecuteScalar();
                return result != null && Convert.ToBoolean(result);
            }
            finally
            {
                conn.Close();
            }
        }

        // Сохранение (добавление или изменение) строки с помощью функции PL/pgSQL save_game
        public long Save(Game game)
        {
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand(
                    "SELECT lab_schema.save_game(@id, @title, @dev_id, @year, @price, @released)", conn);

                NpgsqlParameter pId = new NpgsqlParameter("@id", NpgsqlDbType.Bigint);
                pId.Value = game.Id.HasValue ? (object)game.Id.Value : DBNull.Value;
                cmd.Parameters.Add(pId);

                NpgsqlParameter pTitle = new NpgsqlParameter("@title", NpgsqlDbType.Varchar);
                pTitle.Value = game.Title.Trim();
                cmd.Parameters.Add(pTitle);

                NpgsqlParameter pDevId = new NpgsqlParameter("@dev_id", NpgsqlDbType.Bigint);
                pDevId.Value = game.DeveloperId;
                cmd.Parameters.Add(pDevId);

                NpgsqlParameter pYear = new NpgsqlParameter("@year", NpgsqlDbType.Integer);
                pYear.Value = game.ReleaseYear;
                cmd.Parameters.Add(pYear);

                NpgsqlParameter pPrice = new NpgsqlParameter("@price", NpgsqlDbType.Numeric);
                pPrice.Value = game.Price;
                cmd.Parameters.Add(pPrice);

                NpgsqlParameter pReleased = new NpgsqlParameter("@released", NpgsqlDbType.Boolean);
                pReleased.Value = game.IsReleased;
                cmd.Parameters.Add(pReleased);

                object result = cmd.ExecuteScalar();
                return Convert.ToInt64(result);
            }
            finally
            {
                conn.Close();
            }
        }

        // Удаление строки с помощью функции PL/pgSQL delete_game
        public void Delete(long id)
        {
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand("SELECT lab_schema.delete_game(@id)", conn);
                NpgsqlParameter pId = new NpgsqlParameter("@id", NpgsqlDbType.Bigint);
                pId.Value = id;
                cmd.Parameters.Add(pId);

                cmd.ExecuteNonQuery();
            }
            finally
            {
                conn.Close();
            }
        }
    }
}
