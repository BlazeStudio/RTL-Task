import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta

excel_file = "files/Данные.xlsx"
participants_data = pd.read_excel(excel_file, sheet_name='Договоры участников')
pension_amounts = pd.read_excel(excel_file, sheet_name='Суммы пенсий')
calculation_params = pd.read_excel(excel_file, sheet_name='Параметры расчета', header=None)
calculation_params = calculation_params.set_index(0).transpose()

df_params = pd.DataFrame(calculation_params)

df = pd.merge(pd.DataFrame(participants_data), pd.DataFrame(pension_amounts), on='Номер договора')


# Слияние
def get_last_day_of_month(date):
    next_month = date + relativedelta(months=1)
    last_day = next_month - timedelta(days=next_month.day)
    return last_day


results = []


def add(contract_number, payment_date, current_pension_amount):
    return results.append({
        'Номер договора': contract_number,
        'Дата платежа': payment_date.strftime('%d.%m.%Y'),
        'Размер пенсии': round(current_pension_amount, 2)
    })


# График пенсионных выплат
# Итерация по строкам
for _, row in df.iterrows():
    contract_number = row['Номер договора']
    date_of_birth = row['Дата рождения участника']

    # Начальная дата пенсии
    pension_start_date = get_last_day_of_month(date_of_birth + relativedelta(years=row['Пенсионный возраст']))

    payment_date = pension_start_date
    current_pension_amount = row['Установленный размер пенсии']
    while (payment_date - date_of_birth).days // 365 < df_params['Максимальный возраст, лет'][1]:
        # Индексация в январе
        if payment_date.month == 1 and payment_date != pension_start_date:
            current_pension_amount *= (1 + df_params['Ставка индексации пенсии'][1])
        add(contract_number, payment_date, current_pension_amount)
        next_payment_date = get_last_day_of_month(payment_date + relativedelta(months=1))
        # Проверка на превышение максимального возраста
        if (next_payment_date - date_of_birth).days // 365 >= df_params['Максимальный возраст, лет'][1]:
            add(contract_number, next_payment_date, current_pension_amount)
            break
        payment_date = next_payment_date

df_results = pd.DataFrame(results)
print(df_results)

# Разделение
# print(df_results[df_results['Номер договора'] == 10001])
# print(df_results[df_results['Номер договора'] == 10002])

with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_results.to_excel(writer, sheet_name='Результат', index=False)
