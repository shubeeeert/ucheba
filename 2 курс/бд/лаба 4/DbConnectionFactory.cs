using Npgsql;

namespace VideoGamesApp
{
    /// <summary>
    /// Фабрика подключений к базе данных PostgreSQL
    /// </summary>
    public class DbConnectionFactory
    {
        private readonly string _connectionString;

        public DbConnectionFactory(string connectionString)
        {
            _connectionString = connectionString;
        }

        public NpgsqlConnection CreateConnection()
        {
            NpgsqlConnection conn = new NpgsqlConnection(_connectionString);
            conn.Open();
            return conn;
        }
    }
}
