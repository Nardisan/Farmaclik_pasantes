import datetime
from typing import List

from odoo.fields import Datetime

spanish_months_map = {
    "January": "Enero",
    "February": "Febrero",
    "March": "Marzo",
    "April": "Abril",
    "May": "Mayo",
    "June": "Junio",
    "July": "Julio",
    "August": "Agosto",
    "September": "Septiembre",
    "October": "Octubre",
    "November": "Noviembre",
    "December": "Diciembre"
}


class MonthRecord:
    month_name: str
    is_available: bool

    def __init__(self, month_name: str, is_available: bool = False):
        self.month_name = month_name
        self.is_available = is_available


def get_previous_months_helper(available_date: Datetime = None) -> List[MonthRecord]:
    now = datetime.datetime.now()
    result = []
    for _ in range(0, 6):

        now = now.replace(day=1) - datetime.timedelta(days=1)

        record = MonthRecord(spanish_months_map[now.strftime("%B")], True)

        if available_date is not None and now < available_date:
            record.is_available = False
        result.append(record)

    # invertir resultados
    return result[::-1]

# print(get_previous_months_helper())

#
# class MonthRecord:
#     def __init__(self, name: str, is_available: bool = False):
#         self.name = name
#         self.is_available = is_available
#
#
# def get_previous_months_helper() -> List[MonthRecord]:
#     now = datetime.datetime.now()
#     result = []
#     for _ in range(0, 6):
#         record = MonthRecord(spanish_months_map[now.strftime("%B")], True)
#         now = now.replace(day=1) - datetime.timedelta(days=1)
#         result.append(record)
#     # invertir resultados
#     return result[::-1]
#
#
# print(get_previous_months_helper())
