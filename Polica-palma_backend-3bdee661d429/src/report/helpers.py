import datetime
from abc import ABC
from typing import List, Dict

import pandas as pd

from io import BytesIO

from django.utils import timezone


class DateRangeFiltersDataMixin:
    def get_date_range_data(self):
        column_names = ['Дата начала периода', 'Дата конца периода']
        data = [
            (
                timezone.localtime(self.start_date).strftime("%d.%m.%Y %H:%M:%S"),
                timezone.localtime(self.end_date).strftime("%d.%m.%Y %H:%M:%S"),
            )
        ]
        return column_names, data


class BaseExcelExport(ABC):
    cell_head_format_props = {
        'border': 2,
        'bg_color': '#ddebf7',
        'bold': True,
    }
    cell_format_props = {
        'border': 2
    }
    cell_foot_format_props = {
        "align": "right",
        'border': 2,
        'bg_color': '#ddebf7',
        'bold': True,
    }

    def __init__(self):
        self.data_frames: List[Dict] = []

    def get_excel_file(self):
        byte_buffer = BytesIO()
        writer = pd.ExcelWriter(byte_buffer, engine='xlsxwriter')
        # test
        self.create_excel_sheets(writer)

        writer.close()
        byte_buffer.seek(0)
        return byte_buffer

    def create_excel_sheets(self, writer):
        pass


class OrderReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, orders, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.orders = orders
        self.summary = summary

    # Define a function to apply style to the last row

    def get_orders_data(self):
        column_names = [
            '№',
            'Продажа',
            'Продавец',
            'Создал',
            # 'Магазин',
            'Сумма',
            'Сумма со скидкой',
            'Сумма себестоимости',
            'Сумма скидки',
            'Сумма наценки',
            'Сумма прибыли',
            'Оплачено',
            'Долг',
            'Статус',
        ]
        data = [
            (
                str(index + 1),
                str(order),
                order.salesman.get_full_name() if order.salesman else '-',
                order.created_user.get_full_name(),
                order.total + order.products_discount - order.total_charge,
                order.total_with_discount,
                order.total_self_price,
                order.total_discount,
                order.total_charge,
                order.total_profit,
                order.amount_paid,
                order.debt,
                order.get_status_display(),
            ) for index, order in enumerate(self.orders)
        ]

        data.append(self.get_orders_summary_row())
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_orders_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            '-',
            '-',
            self.summary.get('total_sale_amount', '-'),
            self.summary.get('total_sale_with_discount_amount', '-'),
            self.summary.get('total_self_price_amount', '-'),
            self.summary.get('total_discount_amount', '-'),
            self.summary.get('total_charge_amount', '-'),
            self.summary.get('total_profit_amount', '-'),
            self.summary.get('total_paid_amount', '-'),
            self.summary.get('total_debt_amount', '-'),
            '-',
        )
        return summary_data

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def create_orders_sheet(self, writer):
        df = self.get_orders_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Продажы', startrow=start_row - 1, index=False)
        ws = writer.sheets['Продажы']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по продажам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:L{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:L{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:L{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_orders_sheet(writer)


class MaterialReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, products, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.products = products

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_products_data(self):
        column_names = [
            'Название',
            'Количество до периода',
            'Приход',
            'Расход',
            'Количество после периода',
            'Текущее количество',
        ]
        products_data = [
            (
                product.name,
                product.before_count,
                product.total_income_in_range,
                product.total_outcome_in_range,
                product.after_count,
                product.in_stock
            ) for product in self.products
        ]
        df = pd.DataFrame(columns=column_names, data=products_data)
        return df

    def create_products_sheet(self, writer):
        df = self.get_products_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Товары', startrow=start_row - 1, index=False)
        ws = writer.sheets['Товары']
        cell_format_title = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Материальный товар с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_title)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        ws.conditional_format(f'A{start_row}:F{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:F{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_products_sheet(writer)


class SalesmanReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, salesmen, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.salesmen = salesmen
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_salesman_data(self):
        column_names = [
            'Имя',
            'Магазин',
            'Баланс',
            'Количество продаж',
            'Сумма продаж',
            'Сумма начислений',
            'Сумма платежей',
        ]
        salesmen_data = [
            (
                salesman.get_full_name(),
                salesman.industry if salesman.industry else '-',
                salesman.balance,
                salesman.orders_count,
                salesman.order_total_sum,
                salesman.income_sum,
                salesman.payment_sum,
            ) for salesman in self.salesmen
        ]
        salesmen_data.append(self.get_salesmen_summary_row())
        df = pd.DataFrame(columns=column_names, data=salesmen_data)
        return df

    def get_salesmen_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            '-',
            self.summary.get('total_orders_count', '-'),
            self.summary.get('total_orders_sum', '-'),
            self.summary.get('total_income_sum', '-'),
            self.summary.get('total_payments_sum', '-'),
        )
        return summary_data

    def create_salesman_sheet(self, writer):
        df = self.get_salesman_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Продавцы', startrow=start_row - 1, index=False)
        ws = writer.sheets['Продавцы']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по продавцам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:G{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_salesman_sheet(writer)


class OtherWorkersReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, workers, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.workers = workers
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_salesman_data(self):
        column_names = [
            'Имя',
            'Баланс',
            'Сумма платежей',
        ]
        worker_data = [
            (
                worker.get_full_name(),
                worker.balance,
                worker.payment_sum,
            ) for worker in self.workers
        ]
        worker_data.append(self.get_worker_summary_row())
        df = pd.DataFrame(columns=column_names, data=worker_data)
        return df

    def get_worker_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            self.summary.get('total_payments_sum', '-'),
        )
        return summary_data

    def create_worker_sheet(self, writer):
        df = self.get_salesman_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Сотрудники', startrow=start_row - 1, index=False)
        ws = writer.sheets['Сотрудники']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по сотрудникам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:C{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:C{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:C{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_worker_sheet(writer)


class FloristReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, florists, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.florists = florists
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_florists_data(self):
        column_names = [
            'Имя флориста',
            'Тип флориста',
            'Общее кол-во букетов',
            'Кол-во собранных букетов',
            'Кол-во проданых букетов',
            'Кол-во списанных букетов',
            'Сумма начислений',
            'Сумма платежей',
        ]
        florists_data = [
            (
                florist.get_full_name(),
                florist.get_type_display(),
                florist.finished_product_count + florist.sold_product_count + florist.written_off_product_count,
                florist.sold_product_count,
                florist.finished_product_count,
                florist.written_off_product_count,
                florist.income_sum,
                florist.payment_sum,
            ) for florist in self.florists
        ]
        florists_data.append(self.get_florists_summary_row())
        df = pd.DataFrame(columns=column_names, data=florists_data)
        return df

    def get_florists_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            self.summary.get('total_product_count', '-'),
            self.summary.get('total_sold_product_count', '-'),
            self.summary.get('total_finished_product_count', '-'),
            self.summary.get('total_written_off_product_count', '-'),
            self.summary.get('total_income_sum', '-'),
            self.summary.get('total_payment_sum', '-'),
        )
        return summary_data

    def create_florists_sheet(self, writer):
        df = self.get_florists_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Флористы', startrow=start_row - 1, index=False)
        ws = writer.sheets['Флористы']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по флористам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:H{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:H{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:H{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_florists_sheet(writer)


class WorkersReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, workers, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.workers = workers
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_workers_data(self):
        column_names = [
            'Имя сотрудника',
            'Тип сотрудника',
            'Магазин',
            'Сумма начислений',
            'Сумма платежей',
            'Баланс',
            'Количество продаж',
            'Сумма продаж',
            'Общее кол-во букетов',
            'Кол-во собранных букетов',
            'Кол-во проданых букетов',
            'Кол-во списанных букетов',

        ]
        workers_data = [
            (
                worker.get_full_name(),
                worker.get_type_display(),
                worker.industry if worker.industry else '-',
                worker.income_sum,
                worker.payment_sum,
                worker.balance,
                worker.orders_count,
                worker.order_total_sum,
                worker.finished_product_count + worker.sold_product_count + worker.written_off_product_count,
                worker.sold_product_count,
                worker.finished_product_count,
                worker.written_off_product_count,
            ) for worker in self.workers
        ]
        workers_data.append(self.get_workers_summary_row())
        df = pd.DataFrame(columns=column_names, data=workers_data)
        return df

    def get_workers_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            '-',
            self.summary.get('total_income_sum', '-'),
            self.summary.get('total_payment_sum', '-'),
            '-',
            self.summary.get('total_orders_count', '-'),
            self.summary.get('total_orders_sum', '-'),
            self.summary.get('total_product_count', '-'),
            self.summary.get('total_sold_product_count', '-'),
            self.summary.get('total_finished_product_count', '-'),
            self.summary.get('total_written_off_product_count', '-'),
        )
        return summary_data

    def create_workers_sheet(self, writer):
        df = self.get_workers_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Сотрудники', startrow=start_row - 1, index=False)
        ws = writer.sheets['Сотрудники']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по Сотрудникам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:L{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:L{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:L{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_workers_sheet(writer)


class WriteOffReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, products, factories, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.products = products
        self.factories = factories
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_products_data(self):
        column_names = [
            'Название',
            'Категория',
            'Количество списания',
            'Общая себестоимость',
            'Код товара',
        ]
        products_data = [
            (
                product.name,
                product.category.name,
                product.product_count,
                product.self_price_sum,
                product.code,
            ) for product in self.products
        ]
        products_data.append(self.get_products_summary_row())

        df = pd.DataFrame(columns=column_names, data=products_data)
        return df

    def get_products_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            self.summary.get('total_product_count', '-'),
            self.summary.get('total_self_price_sum', '-'),
            '-'
        )
        return summary_data

    def get_factories_data(self):
        column_names = [
            'Название',
            'Категория',
            'Количество списания',
            'Общая себестоимость',
            'Код товара',
        ]
        factories_data = [
            (
                factory.name,
                factory.category,
                1,
                factory.self_price,
                factory.product_code,
            ) for factory in self.factories
        ]
        factories_data.append(self.get_factories_summary_row())
        df = pd.DataFrame(columns=column_names, data=factories_data)
        return df

    def get_factories_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            self.summary.get('total_product_factory_count', '-'),
            self.summary.get('total_product_factory_self_price_sum', '-'),
            '-'
        )
        return summary_data

    def get_summary_data(self):
        column_names = [
            '',
            'Кол-во',
            'Общая себестоимость',
        ]
        data = [
            (
                'Товары',
                self.summary.get('total_product_count', '-'),
                self.summary.get('total_self_price_sum', '-')
            ),
            (
                'Букеты',
                self.summary.get('total_product_factory_count', '-'),
                self.summary.get('total_product_factory_self_price_sum', '-')
            ),
            (
                'Итого',
                self.summary.get('total_count', '-'),
                self.summary.get('total_self_price', '-')
            )
        ]
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def create_products_sheet(self, writer):
        df = self.get_products_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Товары', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Товары']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по списаниям с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:E{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_factories_sheet(self, writer):
        df = self.get_factories_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Букеты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Букеты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по списаниям с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:E{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_summary_sheet(self, writer):
        df = self.get_summary_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Общие итоги', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Общие итоги']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по списаниям с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:E{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_products_sheet(writer)
        self.create_factories_sheet(writer)
        self.create_summary_sheet(writer)


class ClientsReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, clients, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.clients = clients
        self.summary = summary

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_clients_data(self):
        columns_names = [
            'Имя',
            'Номер телефона',
            'Кол-во покупок',
            'Сумма покупок',
            'Сумма долг',
            'Сумма скидок',
        ]
        clients_data = [
            (
                client.full_name,
                client.phone_number,
                client.orders_count,
                client.orders_sum,
                client.debt,
                client.total_discount_sum,
            ) for client in self.clients
        ]
        clients_data.append(self.get_clients_summary_row())
        df = pd.DataFrame(columns=columns_names, data=clients_data)
        return df

    def get_clients_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            self.summary.get('total_orders_count', '-'),
            self.summary.get('total_orders_sum', '-'),
            self.summary.get('total_debt', '-'),
            '-',
        )
        return summary_data

    def create_clients_sheet(self, writer):
        df = self.get_clients_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Клиенты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Клиенты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по клиентам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:F{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:F{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:F{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_clients_sheet(writer)


class ProductFactoryReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, finished_products, sold_products, written_off_products, summary, start_date, end_date):
        super().__init__()
        self.finished_products = finished_products
        self.sold_products = sold_products
        self.written_off_products = written_off_products
        self.summary = summary
        self.start_date = start_date
        self.end_date = end_date

    def get_product_factories_data(self, factories):
        column_names = [
            'Название',
            'Категория',
            'Тип продажи',
            'Себестоимость',
            'Цена продажи',
            'Продан за',
            'Флорист',
            'Статус',
            'Код товара',
            'Дата окончания',
        ]
        data = [
            (
                factory.name,
                factory.category.name,
                factory.get_sales_type_display(),
                factory.self_price,
                factory.price,
                factory.sold_price,
                factory.florist,
                factory.get_status_display(),
                factory.product_code,
                timezone.localtime(factory.finished_at).strftime('%d.%m.%Y %H:%M'),
            ) for factory in factories
        ]
        data.append(self.get_product_factories_summary_data(factories))
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_product_factories_summary_data(self, factories):
        if factories == self.finished_products:
            data = (
                'Итого',
                '-', '-',
                self.summary.get('total_finished_self_price', '-'),
                self.summary.get('total_finished_price', '-'),
                '0', '-', '-', '-', '-'
            )
        elif factories == self.sold_products:
            data = (
                'Итого',
                '-', '-',
                self.summary.get('total_sold_self_price', '-'),
                self.summary.get('total_sold_price', '-'),
                self.summary.get('total_sale_sum', '-'),
                '-', '-', '-', '-'
            )
        else:
            data = (
                'Итого',
                '-', '-',
                self.summary.get('total_written_off_self_price', '-'),
                self.summary.get('total_written_off_price', '-'),
                '0', '-', '-', '-', '-'
            )
        return data

    def create_finished_products_sheet(self, writer):
        df = self.get_product_factories_data(self.finished_products)

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Завершенные букеты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Завершенные букеты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по букетам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:J{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_sold_products_sheet(self, writer):
        df = self.get_product_factories_data(self.sold_products)

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Проданные букеты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Проданные букеты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по букетам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:J{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_written_off_products_sheet(self, writer):
        df = self.get_product_factories_data(self.written_off_products)

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Списанные букеты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Списанные букеты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по букетам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:J{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:J{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def get_summary_data(self):
        column_names = [
            '',
            'Общее кол-во',
            'Общая сумма',
            'Общая себестоимость',
            'Общая сумма продаж',
        ]
        data = [
            (
                'Собранные букеты',
                self.summary.get('total_finished_count', '-'),
                self.summary.get('total_finished_price', '-'),
                self.summary.get('total_finished_self_price', '-'),
                '-',
            ),
            (
                'Проданне букеты',
                self.summary.get('total_sold_count', '-'),
                self.summary.get('total_sold_price', '-'),
                self.summary.get('total_sold_self_price', '-'),
                self.summary.get('total_sale_sum', '-'),
            ),
            (
                'Списанные букеты',
                self.summary.get('total_written_off_count', '-'),
                self.summary.get('total_written_off_price', '-'),
                self.summary.get('total_written_off_self_price', '-'),
                '-',
            ),
            (
                'Итого',
                self.summary.get('total_product_count', '-'),
                self.summary.get('total_product_price', '-'),
                self.summary.get('total_product_self_price', '-'),
                self.summary.get('total_sale_sum', '-'),
            )
        ]
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def create_summary_sheet(self, writer):
        df = self.get_summary_data()
        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Общие итоги', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Общие итоги']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по букетам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:E{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:E{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_finished_products_sheet(writer)
        self.create_sold_products_sheet(writer)
        self.create_written_off_products_sheet(writer)
        self.create_summary_sheet(writer)


class ProductReturnReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, product_returns, product_factory_returns, summary, start_date, end_date):
        super().__init__()
        self.product_returns = product_returns
        self.product_factory_returns = product_factory_returns
        self.summary = summary
        self.start_date = start_date
        self.end_date = end_date

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def get_product_returns_data(self):
        columns_names = [
            'Заказ',
            'Товар',
            'Кол-во',
            'Цена',
            'Общая сумма',
            'Общая себестоимость',
            'Дата возврата',
        ]
        product_returns_data = [
            (
                str(product_return.order),
                product_return.order_item.product.name,
                product_return.count,
                product_return.order_item.product.price,
                product_return.total,
                product_return.total_self_price,
                timezone.localtime(product_return.created_at).strftime('%d.%m.%Y %H:%M'),
            ) for product_return in self.product_returns
        ]
        product_returns_data.append(self.get_product_returns_summary())
        df = pd.DataFrame(columns=columns_names, data=product_returns_data)
        return df

    def get_product_returns_summary(self):
        data = (
            'Итого',
            '-',
            self.summary.get('total_product_returns', '-'),
            '-',
            self.summary.get('total_product_returns_price', '-'),
            self.summary.get('total_product_returns_self_price', '-'),
            '-',
        )
        return data

    def get_factory_returns_data(self):
        columns_names = [
            'Заказ',
            'Букет',
            'Кол-во',
            'Цена',
            'Общая сумма',
            'Общая себестоимость',
            'Дата возврата',
        ]
        product_returns_data = [
            (
                str(factory_return.order),
                factory_return.product_factory.name,
                1,
                factory_return.price,
                factory_return.price,
                factory_return.product_factory.self_price,
                timezone.localtime(factory_return.returned_at).strftime('%d.%m.%Y %H:%M'),
            ) for factory_return in self.product_factory_returns
        ]
        product_returns_data.append(self.get_factory_returns_summary_data())
        df = pd.DataFrame(columns=columns_names, data=product_returns_data)
        df.style.set_caption("Возвраты товаров")
        return df

    def get_factory_returns_summary_data(self):
        data = (
            'Итого',
            '-',
            self.summary.get('total_product_factory_returns', '-'),
            '-',
            self.summary.get('total_product_factory_returns_price', '-'),
            self.summary.get('total_product_factory_returns_self_price', '-'),
            '-',
        )
        return data

    def create_product_returns_sheet(self, writer):
        df = self.get_product_returns_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Товары', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Товары']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по возвратам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:G{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_factory_returns_sheet(self, writer):
        df = self.get_factory_returns_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Букеты', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Букеты']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по возвратам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:G{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:G{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def get_summary_data(self):
        column_names = [
            '',
            'Кол-во',
            'Цена продажи',
            'Себестоимость',
        ]
        data = [
            (
                'Товары',
                self.summary.get('total_product_returns', '-'),
                self.summary.get('total_product_returns_price', '-'),
                self.summary.get('total_product_returns_self_price', '-'),
            ),
            (
                'Букеты',
                self.summary.get('total_product_factory_returns', '-'),
                self.summary.get('total_product_factory_returns_price', '-'),
                self.summary.get('total_product_factory_returns_self_price', '-'),
            ),
            (
                'Итого',
                self.summary.get('total_returns', '-'),
                self.summary.get('total_price', '-'),
                self.summary.get('total_self_price', '-'),
            )
        ]
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def create_summary_sheet(self, writer):
        df = self.get_summary_data()
        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Общие итоги', startrow=start_row - 1, index=False, float_format="%0.1f")
        ws = writer.sheets['Общие итоги']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по возвратам с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:D{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:D{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:D{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_product_returns_sheet(writer)
        self.create_factory_returns_sheet(writer)
        self.create_summary_sheet(writer)


class OrderItemsReportExcelExport(DateRangeFiltersDataMixin, BaseExcelExport):
    def __init__(self, order_items, order_item_factories, summary, start_date, end_date):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.order_items = order_items
        self.order_item_factories = order_item_factories
        self.summary = summary

    def get_order_items_data(self):
        order_item_column_names = [
            'Товар',
            'Магазин',
            'Продажа',
            'Клиент',
            'Цена',
            'Кол-во',
            'Кол-во возврата',
            'Сумма без скидки/наценки',
            'Сумма со скидкой/наценкой',
            # 'Скидка',
            'Сумма скидки',
            'Сумма наценки',
            'Сумма себестоимости',
            'Сумма прибыли',
            'Дата',
        ]
        order_items_data = [
            (
                order_item.product.name,
                order_item.product.category.industry.name,
                str(order_item.order),
                order_item.order.client.full_name,
                order_item.price,
                order_item.count,
                order_item.returned_count,
                order_item.total - order_item.returned_total_sum + order_item.total_discount - order_item.total_charge,
                order_item.total - order_item.returned_total_sum,
                # order_item.discount,
                order_item.total_discount,
                order_item.total_charge,
                order_item.total_self_price,
                order_item.total_profit,
                timezone.localtime(order_item.order.created_at).strftime("%d.%m.%Y %H:%M:%S"),
            ) for order_item in self.order_items
        ]

        order_item_factories_data = [
            (
                order_item.product_factory.name,
                order_item.product_factory.category.industry.name,
                str(order_item.order),
                order_item.order.client.full_name,
                order_item.price,
                order_item.count,
                order_item.returned_count,
                order_item.total + order_item.total_discount - order_item.total_charge,
                order_item.total,
                # order_item.discount,
                order_item.total_discount,
                order_item.total_charge,
                order_item.total_self_price,
                order_item.total_profit,
                timezone.localtime(order_item.order.created_at).strftime("%d.%m.%Y %H:%M:%S"),
            ) for order_item in self.order_item_factories
        ]

        data = order_items_data + order_item_factories_data
        sorted_data = sorted(data, key=lambda x: timezone.datetime.strptime(x[13], "%d.%m.%Y %H:%M:%S"), reverse=True)
        sorted_data.append(self.get_orders_summary_row())
        order_items_df = pd.DataFrame(columns=order_item_column_names, data=sorted_data)
        return order_items_df

    def get_orders_summary_row(self):
        summary_data = (
            'Итого',
            '-',
            '-',
            '-',
            '-',
            self.summary.get('total_count_sum', '-'),
            self.summary.get('total_returned_count_sum', '-'),
            self.summary.get('total_sum_without_discount', '-'),
            self.summary.get('total_sum', '-'),
            # '-',
            self.summary.get('total_discount_sum', '-'),
            self.summary.get('total_charge_sum', '-'),
            self.summary.get('total_self_price_sum', '-'),
            self.summary.get('total_profit_sum', '-'),
            '-',
        )
        return summary_data

    def get_filters_data(self):
        column_names, data = self.get_date_range_data()
        df = pd.DataFrame(columns=column_names, data=data)
        return df

    def create_orders_sheet(self, writer):
        df = self.get_order_items_data()

        start_row = 3
        end_row = start_row + len(df)
        df.to_excel(writer, sheet_name='Продажы товаров', startrow=start_row - 1, index=False)
        ws = writer.sheets['Продажы товаров']
        cell_format_e = writer.book.add_format(
            {
                "align": "center",
                "font_size": 14,
                'bold': True
            }
        )
        ws.merge_range("A1:G1",
                       f"Отчет по продажам товаров с "
                       f"{timezone.localtime(self.start_date).strftime('%d.%m.%Y %H:%M')}"
                       f" до {timezone.localtime(self.end_date).strftime('%d.%m.%Y %H:%M')}",
                       cell_format_e)
        cell_format = writer.book.add_format(
            self.cell_format_props
        )
        cell_format_head = writer.book.add_format(
            self.cell_head_format_props
        )
        cell_format_foot = writer.book.add_format(
            self.cell_foot_format_props
        )
        ws.conditional_format(f'A{start_row}:N{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format,
        })
        ws.conditional_format(f'A{start_row}:N{start_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_head,
        })
        ws.conditional_format(f'A{end_row}:N{end_row}', {
            'type': 'cell',
            'criteria': '>=',
            'value': 0,
            'format': cell_format_foot,
        })
        ws.autofit()
        ws.set_column(0, 0, 15)

    def create_excel_sheets(self, writer):
        self.create_orders_sheet(writer)
