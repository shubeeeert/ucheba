namespace VideoGamesApp
{
    partial class Form1
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        private void InitializeComponent()
        {
            this.dgvGames = new System.Windows.Forms.DataGridView();
            this.colId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colTitle = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colDeveloper = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colYear = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colPrice = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.colReleased = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.grpEdit = new System.Windows.Forms.GroupBox();
            this.lblTitle = new System.Windows.Forms.Label();
            this.txtTitle = new System.Windows.Forms.TextBox();
            this.lblDeveloper = new System.Windows.Forms.Label();
            this.cmbDeveloper = new System.Windows.Forms.ComboBox();
            this.lblYear = new System.Windows.Forms.Label();
            this.txtYear = new System.Windows.Forms.TextBox();
            this.lblPrice = new System.Windows.Forms.Label();
            this.txtPrice = new System.Windows.Forms.TextBox();
            this.chkReleased = new System.Windows.Forms.CheckBox();
            this.btnAdd = new System.Windows.Forms.Button();
            this.btnUpdate = new System.Windows.Forms.Button();
            this.btnDelete = new System.Windows.Forms.Button();
            this.btnClear = new System.Windows.Forms.Button();
            this.grpFilter = new System.Windows.Forms.GroupBox();
            this.lblFilter = new System.Windows.Forms.Label();
            this.txtFilter = new System.Windows.Forms.TextBox();
            this.btnFilter = new System.Windows.Forms.Button();
            this.btnResetFilter = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dgvGames)).BeginInit();
            this.grpEdit.SuspendLayout();
            this.grpFilter.SuspendLayout();
            this.SuspendLayout();

            // dgvGames
            this.dgvGames.AllowUserToAddRows = false;
            this.dgvGames.AllowUserToDeleteRows = false;
            this.dgvGames.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill;
            this.dgvGames.BackgroundColor = System.Drawing.SystemColors.Window;
            this.dgvGames.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dgvGames.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
                this.colId,
                this.colTitle,
                this.colDeveloper,
                this.colYear,
                this.colPrice,
                this.colReleased
            });
            this.dgvGames.Location = new System.Drawing.Point(14, 78);
            this.dgvGames.MultiSelect = false;
            this.dgvGames.Name = "dgvGames";
            this.dgvGames.ReadOnly = true;
            this.dgvGames.RowHeadersVisible = false;
            this.dgvGames.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dgvGames.Size = new System.Drawing.Size(792, 260);
            this.dgvGames.TabIndex = 1;
            this.dgvGames.CellClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvGames_CellClick);

            // colId
            this.colId.FillWeight = 45F;
            this.colId.HeaderText = "ID";
            this.colId.Name = "colId";
            this.colId.ReadOnly = true;

            // colTitle
            this.colTitle.FillWeight = 160F;
            this.colTitle.HeaderText = "Название";
            this.colTitle.Name = "colTitle";
            this.colTitle.ReadOnly = true;

            // colDeveloper
            this.colDeveloper.FillWeight = 140F;
            this.colDeveloper.HeaderText = "Разработчик";
            this.colDeveloper.Name = "colDeveloper";
            this.colDeveloper.ReadOnly = true;

            // colYear
            this.colYear.FillWeight = 80F;
            this.colYear.HeaderText = "Год выпуска";
            this.colYear.Name = "colYear";
            this.colYear.ReadOnly = true;

            // colPrice
            this.colPrice.FillWeight = 75F;
            this.colPrice.HeaderText = "Цена";
            this.colPrice.Name = "colPrice";
            this.colPrice.ReadOnly = true;

            // colReleased
            this.colReleased.FillWeight = 75F;
            this.colReleased.HeaderText = "Выпущена";
            this.colReleased.Name = "colReleased";
            this.colReleased.ReadOnly = true;

            // grpFilter
            this.grpFilter.Controls.Add(this.lblFilter);
            this.grpFilter.Controls.Add(this.txtFilter);
            this.grpFilter.Controls.Add(this.btnFilter);
            this.grpFilter.Controls.Add(this.btnResetFilter);
            this.grpFilter.Location = new System.Drawing.Point(14, 12);
            this.grpFilter.Name = "grpFilter";
            this.grpFilter.Size = new System.Drawing.Size(792, 58);
            this.grpFilter.TabIndex = 0;
            this.grpFilter.TabStop = false;
            this.grpFilter.Text = "Настройка выборки (фильтрация)";

            // lblFilter
            this.lblFilter.AutoSize = true;
            this.lblFilter.Location = new System.Drawing.Point(14, 26);
            this.lblFilter.Name = "lblFilter";
            this.lblFilter.Size = new System.Drawing.Size(135, 15);
            this.lblFilter.Text = "Название содержит:";

            // txtFilter
            this.txtFilter.Location = new System.Drawing.Point(155, 23);
            this.txtFilter.Name = "txtFilter";
            this.txtFilter.Size = new System.Drawing.Size(340, 23);
            this.txtFilter.TabIndex = 0;

            // btnFilter
            this.btnFilter.Location = new System.Drawing.Point(510, 21);
            this.btnFilter.Name = "btnFilter";
            this.btnFilter.Size = new System.Drawing.Size(130, 27);
            this.btnFilter.TabIndex = 1;
            this.btnFilter.Text = "Применить";
            this.btnFilter.UseVisualStyleBackColor = true;
            this.btnFilter.Click += new System.EventHandler(this.btnFilter_Click);

            // btnResetFilter
            this.btnResetFilter.Location = new System.Drawing.Point(650, 21);
            this.btnResetFilter.Name = "btnResetFilter";
            this.btnResetFilter.Size = new System.Drawing.Size(128, 27);
            this.btnResetFilter.TabIndex = 2;
            this.btnResetFilter.Text = "Сбросить";
            this.btnResetFilter.UseVisualStyleBackColor = true;
            this.btnResetFilter.Click += new System.EventHandler(this.btnResetFilter_Click);

            // grpEdit
            this.grpEdit.Controls.Add(this.lblTitle);
            this.grpEdit.Controls.Add(this.txtTitle);
            this.grpEdit.Controls.Add(this.lblDeveloper);
            this.grpEdit.Controls.Add(this.cmbDeveloper);
            this.grpEdit.Controls.Add(this.lblYear);
            this.grpEdit.Controls.Add(this.txtYear);
            this.grpEdit.Controls.Add(this.lblPrice);
            this.grpEdit.Controls.Add(this.txtPrice);
            this.grpEdit.Controls.Add(this.chkReleased);
            this.grpEdit.Controls.Add(this.btnAdd);
            this.grpEdit.Controls.Add(this.btnUpdate);
            this.grpEdit.Controls.Add(this.btnDelete);
            this.grpEdit.Controls.Add(this.btnClear);
            this.grpEdit.Location = new System.Drawing.Point(14, 346);
            this.grpEdit.Name = "grpEdit";
            this.grpEdit.Size = new System.Drawing.Size(792, 138);
            this.grpEdit.TabIndex = 2;
            this.grpEdit.TabStop = false;
            this.grpEdit.Text = "Добавление и редактирование записи";

            // lblTitle
            this.lblTitle.AutoSize = true;
            this.lblTitle.Location = new System.Drawing.Point(14, 30);
            this.lblTitle.Name = "lblTitle";
            this.lblTitle.Size = new System.Drawing.Size(65, 15);
            this.lblTitle.Text = "Название:";

            // txtTitle
            this.txtTitle.Location = new System.Drawing.Point(115, 27);
            this.txtTitle.Name = "txtTitle";
            this.txtTitle.Size = new System.Drawing.Size(230, 23);
            this.txtTitle.TabIndex = 0;

            // lblDeveloper
            this.lblDeveloper.AutoSize = true;
            this.lblDeveloper.Location = new System.Drawing.Point(14, 64);
            this.lblDeveloper.Name = "lblDeveloper";
            this.lblDeveloper.Size = new System.Drawing.Size(83, 15);
            this.lblDeveloper.Text = "Разработчик:";

            // cmbDeveloper
            this.cmbDeveloper.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbDeveloper.Location = new System.Drawing.Point(115, 61);
            this.cmbDeveloper.Name = "cmbDeveloper";
            this.cmbDeveloper.Size = new System.Drawing.Size(230, 23);
            this.cmbDeveloper.TabIndex = 1;

            // lblYear
            this.lblYear.AutoSize = true;
            this.lblYear.Location = new System.Drawing.Point(375, 30);
            this.lblYear.Name = "lblYear";
            this.lblYear.Size = new System.Drawing.Size(80, 15);
            this.lblYear.Text = "Год выпуска:";

            // txtYear
            this.txtYear.Location = new System.Drawing.Point(470, 27);
            this.txtYear.Name = "txtYear";
            this.txtYear.Size = new System.Drawing.Size(110, 23);
            this.txtYear.TabIndex = 2;
            this.txtYear.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txtNumeric_KeyPress);

            // lblPrice
            this.lblPrice.AutoSize = true;
            this.lblPrice.Location = new System.Drawing.Point(375, 64);
            this.lblPrice.Name = "lblPrice";
            this.lblPrice.Size = new System.Drawing.Size(40, 15);
            this.lblPrice.Text = "Цена:";

            // txtPrice
            this.txtPrice.Location = new System.Drawing.Point(470, 61);
            this.txtPrice.Name = "txtPrice";
            this.txtPrice.Size = new System.Drawing.Size(110, 23);
            this.txtPrice.TabIndex = 3;
            this.txtPrice.KeyPress += new System.Windows.Forms.KeyPressEventHandler(this.txtNumeric_KeyPress);

            // chkReleased
            this.chkReleased.AutoSize = true;
            this.chkReleased.Location = new System.Drawing.Point(615, 29);
            this.chkReleased.Name = "chkReleased";
            this.chkReleased.Size = new System.Drawing.Size(85, 19);
            this.chkReleased.TabIndex = 4;
            this.chkReleased.Text = "Выпущена";

            // btnAdd
            this.btnAdd.Location = new System.Drawing.Point(14, 96);
            this.btnAdd.Name = "btnAdd";
            this.btnAdd.Size = new System.Drawing.Size(150, 30);
            this.btnAdd.TabIndex = 5;
            this.btnAdd.Text = "Добавить запись";
            this.btnAdd.UseVisualStyleBackColor = true;
            this.btnAdd.Click += new System.EventHandler(this.btnAdd_Click);

            // btnUpdate
            this.btnUpdate.Location = new System.Drawing.Point(176, 96);
            this.btnUpdate.Name = "btnUpdate";
            this.btnUpdate.Size = new System.Drawing.Size(150, 30);
            this.btnUpdate.TabIndex = 6;
            this.btnUpdate.Text = "Изменить запись";
            this.btnUpdate.UseVisualStyleBackColor = true;
            this.btnUpdate.Click += new System.EventHandler(this.btnUpdate_Click);

            // btnDelete
            this.btnDelete.Location = new System.Drawing.Point(338, 96);
            this.btnDelete.Name = "btnDelete";
            this.btnDelete.Size = new System.Drawing.Size(180, 30);
            this.btnDelete.TabIndex = 7;
            this.btnDelete.Text = "Удалить выбранную строку";
            this.btnDelete.UseVisualStyleBackColor = true;
            this.btnDelete.Click += new System.EventHandler(this.btnDelete_Click);

            // btnClear
            this.btnClear.Location = new System.Drawing.Point(530, 96);
            this.btnClear.Name = "btnClear";
            this.btnClear.Size = new System.Drawing.Size(130, 30);
            this.btnClear.TabIndex = 8;
            this.btnClear.Text = "Очистить поля";
            this.btnClear.UseVisualStyleBackColor = true;
            this.btnClear.Click += new System.EventHandler(this.btnClear_Click);

            // Form1
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(820, 498);
            this.Controls.Add(this.grpFilter);
            this.Controls.Add(this.dgvGames);
            this.Controls.Add(this.grpEdit);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.Name = "Form1";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Управление базой данных «Видеоигры»";
            ((System.ComponentModel.ISupportInitialize)(this.dgvGames)).EndInit();
            this.grpEdit.ResumeLayout(false);
            this.grpEdit.PerformLayout();
            this.grpFilter.ResumeLayout(false);
            this.grpFilter.PerformLayout();
            this.ResumeLayout(false);
        }

        #endregion

        internal System.Windows.Forms.DataGridView dgvGames;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colId;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colTitle;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colDeveloper;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colYear;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colPrice;
        internal System.Windows.Forms.DataGridViewTextBoxColumn colReleased;
        internal System.Windows.Forms.GroupBox grpEdit;
        internal System.Windows.Forms.Label lblTitle;
        internal System.Windows.Forms.TextBox txtTitle;
        internal System.Windows.Forms.Label lblDeveloper;
        internal System.Windows.Forms.ComboBox cmbDeveloper;
        internal System.Windows.Forms.Label lblYear;
        internal System.Windows.Forms.TextBox txtYear;
        internal System.Windows.Forms.Label lblPrice;
        internal System.Windows.Forms.TextBox txtPrice;
        internal System.Windows.Forms.CheckBox chkReleased;
        internal System.Windows.Forms.Button btnAdd;
        internal System.Windows.Forms.Button btnUpdate;
        internal System.Windows.Forms.Button btnDelete;
        internal System.Windows.Forms.Button btnClear;
        internal System.Windows.Forms.GroupBox grpFilter;
        internal System.Windows.Forms.Label lblFilter;
        internal System.Windows.Forms.TextBox txtFilter;
        internal System.Windows.Forms.Button btnFilter;
        internal System.Windows.Forms.Button btnResetFilter;
    }
}
