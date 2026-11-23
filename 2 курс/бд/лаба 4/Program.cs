using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace VideoGamesApp
{
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            if (args.Length > 0 && args[0] == "--screenshots")
            {
                RunScreenshotCapture();
                return;
            }

            Application.Run(new Form1());
        }

        private static void CaptureWindow(Form form, string fileName)
        {
            Application.DoEvents();
            using (Bitmap bmp = new Bitmap(form.Bounds.Width, form.Bounds.Height))
            {
                using (Graphics g = Graphics.FromImage(bmp))
                {
                    g.CopyFromScreen(form.Bounds.Location, Point.Empty, form.Bounds.Size);
                }
                bmp.Save(fileName, ImageFormat.Png);
            }
        }

        private static void CaptureWithMessageBox(Form form, string fileName, Action showMessageBoxAction, string closeKey = "{ENTER}")
        {
            Timer t = new Timer();
            t.Interval = 500;
            t.Tick += (s, e) =>
            {
                t.Stop();
                t.Dispose();
                CaptureWindow(form, fileName);
                SendKeys.SendWait(closeKey);
            };
            t.Start();
            showMessageBoxAction();
        }

        private static void RunScreenshotCapture()
        {
            Form1 form = new Form1();
            form.TopMost = true;
            form.Show();
            form.Activate();
            Application.DoEvents();
            System.Threading.Thread.Sleep(400);
            Application.DoEvents();

            // 1. Главное окно приложения с данными таблицы game и выбором строки
            form.SelectRow(1); // Minecraft
            Application.DoEvents();
            System.Threading.Thread.Sleep(200);
            CaptureWindow(form, "s1.png");

            // 2. Добавление новой записи (выбор внешнего ключа по названию из списка)
            form.ClearFields();
            form.txtTitle.Text = "Half-Life 2";
            for (int i = 0; i < form.cmbDeveloper.Items.Count; i++)
            {
                if (form.cmbDeveloper.Items[i].ToString() == "Valve Corporation")
                {
                    form.cmbDeveloper.SelectedIndex = i;
                    break;
                }
            }
            form.txtYear.Text = "2004";
            form.txtPrice.Text = "9.99";
            form.chkReleased.Checked = true;
            Application.DoEvents();

            CaptureWithMessageBox(form, "s2.png", () =>
            {
                form.btnAdd.PerformClick();
            });
            Application.DoEvents();
            System.Threading.Thread.Sleep(200);

            // 3. Попытка повторного ввода уже имеющихся данных (дубликат)
            form.txtTitle.Text = "Half-Life 2";
            for (int i = 0; i < form.cmbDeveloper.Items.Count; i++)
            {
                if (form.cmbDeveloper.Items[i].ToString() == "Valve Corporation")
                {
                    form.cmbDeveloper.SelectedIndex = i;
                    break;
                }
            }
            form.txtYear.Text = "2004";
            form.txtPrice.Text = "9.99";
            form.chkReleased.Checked = true;
            Application.DoEvents();

            CaptureWithMessageBox(form, "s3.png", () =>
            {
                form.btnAdd.PerformClick();
            });
            Application.DoEvents();

            // 4. Запрет ввода отрицательного значения цены
            form.txtPrice.Text = "-15.00";
            Application.DoEvents();
            CaptureWithMessageBox(form, "s4.png", () =>
            {
                form.ValidateInput(out _, out _);
            });
            Application.DoEvents();

            // 5. Изменение записи
            int lastRow = form.dgvGames.Rows.Count - 1;
            form.SelectRow(lastRow);
            form.txtPrice.Text = "14.99";
            Application.DoEvents();
            CaptureWithMessageBox(form, "s5.png", () =>
            {
                form.btnUpdate.PerformClick();
            });
            Application.DoEvents();

            // 6. Регистронезависимая фильтрация через запрос (ввод в нижнем регистре)
            form.txtFilter.Text = "hollow";
            form.btnFilter.PerformClick();
            Application.DoEvents();
            System.Threading.Thread.Sleep(200);
            CaptureWindow(form, "s6.png");

            // Сброс фильтра и удаление тестовой записи с подтверждением Да/Нет
            form.btnResetFilter.PerformClick();
            Application.DoEvents();
            lastRow = form.dgvGames.Rows.Count - 1;
            form.SelectRow(lastRow);
            Application.DoEvents();

            int step = 0;
            Timer tDel = new Timer();
            tDel.Interval = 500;
            tDel.Tick += (s, e) =>
            {
                step++;
                if (step == 1)
                {
                    CaptureWindow(form, "s7.png");
                    SendKeys.SendWait("{ENTER}");
                }
                else if (step == 2)
                {
                    tDel.Stop();
                    tDel.Dispose();
                    SendKeys.SendWait("{ENTER}");
                }
            };
            tDel.Start();
            form.btnDelete.PerformClick();
            Application.DoEvents();

            form.Close();
        }
    }
}
