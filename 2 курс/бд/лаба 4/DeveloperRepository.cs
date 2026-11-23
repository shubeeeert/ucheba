using System.Collections.Generic;
using Npgsql;

namespace VideoGamesApp
{
    /// <summary>
    /// Репозиторий для работы с родительской таблицей разработчиков (lab_schema.developer)
    /// </summary>
    public class DeveloperRepository
    {
        private readonly DbConnectionFactory _connectionFactory;

        public DeveloperRepository(DbConnectionFactory connectionFactory)
        {
            _connectionFactory = connectionFactory;
        }

        public List<Developer> GetAll()
        {
            List<Developer> developers = new List<Developer>();
            NpgsqlConnection conn = _connectionFactory.CreateConnection();
            try
            {
                NpgsqlCommand cmd = new NpgsqlCommand("SELECT * FROM lab_schema.get_all_developers()", conn);
                NpgsqlDataReader reader = cmd.ExecuteReader();
                while (reader.Read())
                {
                    long id = reader.GetInt64(0);
                    string name = reader.GetString(1);
                    developers.Add(new Developer(id, name));
                }
                reader.Close();
            }
            finally
            {
                conn.Close();
            }
            return developers;
        }
    }
}
