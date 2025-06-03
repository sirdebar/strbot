import pandas as pd

# Загружаем Excel файл
file_path = 'credit-0b9d6b53-06a7-4321-91bc-d3635df3642c.xlsx'
data = pd.read_excel(file_path)

# Печатаем названия столбцов и первые несколько строк
print("Columns:", data.columns)
print(data.head())
