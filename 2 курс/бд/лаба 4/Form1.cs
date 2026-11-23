using System;
using System.Collections.Generic;
using System.Globalization;
using System.Windows.Forms;

namespace VideoGamesApp
{
    public partial class Form1 : Form
    {
        private const string ConnectionString =
            "Server=127.0.0.1;Port=5432;User Id=lab_test;Password=lab_test;Database=lab_db";

        private readonly DeveloperRepository _developerRepository;
        private readonly GameRepository _gameRepository;
        private long? _currentGameId = null;

        public Form1()
        {
            InitializeComponent();

            DbConnectionFactory connectionFactory = new DbConnectionFactory(ConnectionString);
            _developerRepository = new DeveloperRepository(connectionFactory);
            _gameRepository = new GameRepository(connectionFactory);

            LoadDevelopers();
            LoadGames();
        }

        // Загрузка списка разработчиков (родительская таблица) в ComboBox
        public void LoadDevelopers()
        {
            try
            {
                List<Developer> developers = _developerRepository.GetAll();
                cmbDeveloper.Items.Clear();
                foreach (Developer dev in developers)
                {
                    cmbDeveloper.Items.Add(dev);
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка загрузки разработчиков: {ex.Message}",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // Загрузка игр в DataGridView (с необязательным фильтром через запрос к БД)
        public void LoadGames(string filter = null)
        {
            try
            {
                List<Game> games = string.IsNullOrEmpty(filter)
                    ? _gameRepository.GetAll()
                    : _gameRepository.FilterByTitle(filter);

                dgvGames.Rows.Clear();
                foreach (Game game in games)
                {
                    dgvGames.Rows.Add(
                        game.Id,
                        game.Title,
                        game.DeveloperName,
                        game.ReleaseYear,
                        game.Price.ToString("0.00"),
                        game.IsReleased ? "Да" : "Нет"
                    );
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка загрузки игр: {ex.Message}",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // Запрет ввода знака минус (отрицательных значений) в числовые поля
        private void txtNumeric_KeyPress(object sender, KeyPressEventArgs e)
        {
            if (e.KeyChar == '-')
            {
                e.Handled = true;
                MessageBox.Show("Ввод отрицательных значений запрещён!",
                    "Ограничение ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            }
        }

        // Кнопка «Добавить запись»
        private void btnAdd_Click(object sender, EventArgs e)
        {
            if (!ValidateInput(out int year, out decimal price))
                return;

            string title = txtTitle.Text.Trim();
            Developer selectedDev = (Developer)cmbDeveloper.SelectedItem;

            try
            {
                // Проверка на ввод уже имеющихся данных без записи в таблицу
                if (_gameRepository.ExistsByTitle(title, null))
                {
                    MessageBox.Show(
                        $"Игра с названием «{title}» уже существует в базе данных! Запись данных в таблицу не выполнена.",
                        "Дублирование данных", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                Game newGame = new Game(null, title, selectedDev.Id, selectedDev.Name, year, price, chkReleased.Checked);
                _gameRepository.Save(newGame);

                MessageBox.Show("Игра успешно добавлена!",
                    "Успех", MessageBoxButtons.OK, MessageBoxIcon.Information);
                ClearFields();
                LoadGames();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка добавления: {ex.Message}",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // Кнопка «Изменить запись»
        private void btnUpdate_Click(object sender, EventArgs e)
        {
            if (_currentGameId == null)
            {
                MessageBox.Show("Выберите игру в таблице для изменения!",
                    "Предупреждение", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            if (!ValidateInput(out int year, out decimal price))
                return;

            string title = txtTitle.Text.Trim();
            Developer selectedDev = (Developer)cmbDeveloper.SelectedItem;

            try
            {
                // Проверка на дублирование названия с другой существующей записью
                if (_gameRepository.ExistsByTitle(title, _currentGameId))
                {
                    MessageBox.Show(
                        $"Другая игра с названием «{title}» уже существует в базе данных! Изменение не сохранено.",
                        "Дублирование данных", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    return;
                }

                Game updatedGame = new Game(_currentGameId, title, selectedDev.Id, selectedDev.Name, year, price, chkReleased.Checked);
                _gameRepository.Save(updatedGame);

                MessageBox.Show("Данные игры успешно изменены!",
                    "Успех", MessageBoxButtons.OK, MessageBoxIcon.Information);
                ClearFields();
                LoadGames();
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Ошибка изменения: {ex.Message}",
                    "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        // Кнопка «Удалить выбранную строку» с подтверждением Да/Нет
        private void btnDelete_Click(object sender, EventArgs e)
        {
            if (_currentGameId == null)
            {
                MessageBox.Show("Выберите игру в таблице для удаления!",
                    "Предупреждение", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return;
            }

            DialogResult result = MessageBox.Show(
                "Вы действительно уверены, что хотите удалить выбранную запись?",
                "Подтверждение удаления", MessageBoxButtons.YesNo, MessageBoxIcon.Question);

            if (result == DialogResult.Yes)
            {
                try
                {
                    _gameRepository.Delete(_currentGameId.Value);
                    MessageBox.Show("Запись успешно удалена!",
                        "Успех", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    ClearFields();
                    LoadGames();
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Ошибка удаления: {ex.Message}",
                        "Ошибка", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        // Кнопка «Очистить поля»
        private void btnClear_Click(object sender, EventArgs e)
        {
            ClearFields();
        }

        // Кнопка «Применить» (регистронезависимый фильтр через запрос к БД)
        private void btnFilter_Click(object sender, EventArgs e)
        {
            string filter = txtFilter.Text.Trim();
            LoadGames(string.IsNullOrEmpty(filter) ? null : filter);
        }

        // Кнопка «Сбросить»
        private void btnResetFilter_Click(object sender, EventArgs e)
        {
            txtFilter.Text = "";
            LoadGames();
        }

        // Выбор строки в таблице DataGridView
        private void dgvGames_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex >= 0)
            {
                SelectRow(e.RowIndex);
            }
        }

        public void SelectRow(int rowIndex)
        {
            if (rowIndex >= 0 && rowIndex < dgvGames.Rows.Count)
            {
                dgvGames.ClearSelection();
                dgvGames.Rows[rowIndex].Selected = true;

                _currentGameId = Convert.ToInt64(dgvGames.Rows[rowIndex].Cells[0].Value);
                txtTitle.Text = dgvGames.Rows[rowIndex].Cells[1].Value.ToString();

                string devName = dgvGames.Rows[rowIndex].Cells[2].Value.ToString();
                foreach (Developer item in cmbDeveloper.Items)
                {
                    if (item.Name == devName)
                    {
                        cmbDeveloper.SelectedItem = item;
                        break;
                    }
                }

                txtYear.Text = dgvGames.Rows[rowIndex].Cells[3].Value.ToString();
                txtPrice.Text = dgvGames.Rows[rowIndex].Cells[4].Value.ToString();
                chkReleased.Checked = dgvGames.Rows[rowIndex].Cells[5].Value.ToString() == "Да";
            }
        }

        // Валидация пользовательского ввода (включая запрет отрицательных значений)
        public bool ValidateInput(out int year, out decimal price)
        {
            year = 0;
            price = 0m;

            if (string.IsNullOrWhiteSpace(txtTitle.Text))
            {
                MessageBox.Show("Введите название игры!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            if (cmbDeveloper.SelectedItem == null)
            {
                MessageBox.Show("Выберите разработчика из списка!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            if (!int.TryParse(txtYear.Text.Trim(), out year))
            {
                MessageBox.Show("Год выпуска должен быть целым числом!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            if (year < 0)
            {
                MessageBox.Show("Год выпуска не может быть отрицательным значением!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            if (year < 1970 || year > 2030)
            {
                MessageBox.Show("Год выпуска должен находиться в диапазоне от 1970 до 2030!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            string rawPrice = txtPrice.Text.Trim().Replace(',', '.');
            if (!decimal.TryParse(rawPrice, NumberStyles.Number, CultureInfo.InvariantCulture, out price))
            {
                MessageBox.Show("Введите корректное числовое значение цены!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            if (price < 0)
            {
                MessageBox.Show("Цена не может быть отрицательной!",
                    "Ошибка ввода", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                return false;
            }

            return true;
        }

        // Очистка полей ввода
        public void ClearFields()
        {
            _currentGameId = null;
            txtTitle.Text = "";
            cmbDeveloper.SelectedIndex = -1;
            txtYear.Text = "";
            txtPrice.Text = "";
            chkReleased.Checked = false;
        }
    }
}
