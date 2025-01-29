import pandas as pd

# Загружаем Excel файл
file_path = 'credit-0b9d6b53-06a7-4321-91bc-d3635df3642c.xlsx'
data = pd.read_excel(file_path)

# Фильтруем данные для заявок от магистров и считаем количество заявок по университетам
masters_data = data[data['level'] == 'master']
university_counts = masters_data['university'].value_counts()

# Находим университет с вторым по числу заявок
second_university = university_counts.index[1]

# Фильтруем данные по найденному университету для бакалавров и находим минимальную сумму кредита
bachelors_data = data[(data['university'] == second_university) & (data['level'] == 'bachelor')]
min_initial_credit = bachelors_data['initial_credit_amount'].min()

# Выводим результат в нужном формате (число без пробелов)
print(int(min_initial_credit))
