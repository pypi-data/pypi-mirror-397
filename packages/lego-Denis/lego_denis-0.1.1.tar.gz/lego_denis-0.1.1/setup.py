from setuptools import setup, find_packages

setup(
    name='lego_Denis',        # название вашей библиотеки
    version='0.1.1',          # версия
    packages=find_packages(),
    author='Denis',
    author_email='denisfomenko098@gmail.com',
    description='''''
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from openpyxl import Workbook


class ExcelLikeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Похоже на Excel")
        self.geometry("950x750")
        self.resizable(True, True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton",
                        font=("Helvetica", 11, " bold"),
                        padding=6)
        style.configure("Treeview.Heading",
                        font=("Helvetica", 12, "bold"))
        style.configure("Treeview",
                        font=("Helvetica", 11))
        style.map('TButton', background=[('active', '#4CAF50')])

        # Создаем верхний фрейм для настроек
        control_frame = ttk.Frame(self, padding=10)
        control_frame.pack(fill=tk.X)

        # Поля для количества строк и колонок
        lbl_rows = ttk.Label(control_frame, text="Количество строк:", font=("Helvetica", 11))
        lbl_rows.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.rows_entry = ttk.Entry(control_frame, width=5, font=("Helvetica", 11))
        self.rows_entry.insert(0, "2")
        self.rows_entry.grid(row=0, column=1, padx=5, pady=5)

        lbl_cols = ttk.Label(control_frame, text="Количество колонок:", font=("Helvetica", 11))
        lbl_cols.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.columns_entry = ttk.Entry(control_frame, width=5, font=("Helvetica", 11))
        self.columns_entry.insert(0, "3")
        self.columns_entry.grid(row=0, column=3, padx=5, pady=5)

        # Кнопка обновления таблицы
        btn_update = ttk.Button(control_frame, text="Обновить таблицу", command=self.update_table)
        btn_update.grid(row=0, column=4, padx=10, pady=5)

        # Кнопка сохранения в Excel
        btn_save_excel = ttk.Button(control_frame, text="Сохранить в Excel", command=self.save_to_excel)
        btn_save_excel.grid(row=0, column=5, padx=10, pady=5)

        # Создаем область для таблицы с отступами
        self.table_frame = ttk.Frame(self)
        self.table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Изначально создаем 3 колонки
        self.num_columns = 3
        self.num_rows = 2

        # Инициализируем переменные для колонок и данных
        self.columns_vars = []
        self.data = []

        # Создаем названия колонок
        self.create_default_columns()

        # Создаем таблицу
        self.create_table()

        # Изначальные данные
        self.data = [["" for _ in range(self.num_columns)] for _ in range(self.num_rows)]
        self.load_data()

        # Обновляем заголовки
        self.update_columns()

        # Обработчик двойного клика для редактирования
        self.tree.bind('<Double-1>', self.on_double_click)

        self.editing_entry = None
        self.bind('<Configure>', self.on_resize)

    def create_default_columns(self):
        self.columns_vars = []
        for i in range(self.num_columns):
            var = tk.StringVar(value=f"Col{i+1}")
            self.columns_vars.append(var)

    def create_table(self):
        # Удаляем старую таблицу, если есть
        if hasattr(self, 'tree'):
            try:
                self.tree.destroy()
            except:
                pass
        # Создаем новую таблицу
        columns = [var.get() for var in self.columns_vars]
        self.tree = ttk.Treeview(self.table_frame, columns=columns, show='headings')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.update_columns()
        self.tree.bind('<Double-1>', self.on_double_click)

    def update_columns(self):
        if not hasattr(self, 'tree'):
            return
        columns = [var.get() for var in self.columns_vars]
        self.tree.config(columns=columns)
        total_width = self.winfo_width()
        if total_width <= 1:
            total_width = 950
        col_width = max(80, total_width // len(columns) - 10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_width, anchor='center')

    def update_table(self):
        # Обновляем число строк и колонок
        try:
            self.num_rows = int(self.rows_entry.get())
            self.num_columns = int(self.columns_entry.get())
            if self.num_rows < 1 or self.num_columns < 1:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "Введите целые числа больше 0 для строк и колонок")
            return

        self.create_default_columns()
        self.create_table()
        self.data = [["" for _ in range(self.num_columns)] for _ in range(self.num_rows)]
        self.load_data()
        self.update_columns()

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        for row in self.data:
            self.tree.insert('', 'end', values=row)

    def on_double_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            self.edit_cell(row_id, column)

    def edit_cell(self, row_id, column):
        x, y, width, height = self.tree.bbox(row_id, column)
        col_index = int(column.replace('#', '')) - 1
        values = self.tree.item(row_id)['values']
        if col_index >= len(values):
            return
        current_value = values[col_index]

        # Создаем Entry для редактирования
        self.editing_entry = tk.Entry(self.tree)
        self.editing_entry.place(x=x, y=y, width=width, height=height)
        self.editing_entry.insert(0, current_value)
        self.editing_entry.focus()

        def save_edit(event):
            new_value = self.editing_entry.get()
            new_values = list(self.tree.item(row_id)['values'])
            new_values[col_index] = new_value
            self.tree.item(row_id, values=new_values)
            self.editing_entry.destroy()

        self.editing_entry.bind('<Return>', save_edit)
        self.editing_entry.bind('<FocusOut>', lambda e: self.editing_entry.destroy())

    def save_to_excel(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return
        wb = Workbook()
        ws = wb.active

        # Записываем заголовки
        columns = [var.get() for var in self.columns_vars]
        ws.append(columns)

        # Записываем данные
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            ws.append(values)

        try:
            wb.save(file_path)
            messagebox.showinfo("Успех", f"Файл сохранен: {file_path}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {e}")

    def on_resize(self, event):
        if hasattr(self, 'tree'):
            self.update_columns()

if __name__ == "__main__":
    app = ExcelLikeApp()
    app.mainloop()
''''',
    url='https://github.com/Fifaro/lego_Denis',  # если есть
)