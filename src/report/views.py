import pandas as pd

from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from src.report.services import get_material_report_products


class ExportMaterialReportToExcelView(View):
    def get_filters(self):
        start_date = self.request.GET.get('start_date', None)
        end_date = self.request.GET.get('end_date', None)
        industry = self.request.GET.get('industry', None)
        return {
            'start_date': start_date,
            'end_date': end_date,
            'industry': industry,
        }

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        products = get_material_report_products(request.user, **self.get_filters())
        file_name = self.generate_excel(products)

        response['Content-Disposition'] = f'attachment; filename={file_name}.xlsx'
        return response

    def generate_excel(self, products):
        column_names = [
            'Название',
            'Количество до периода',
            'Приход',
            'Расход',
            'Количество после периода',
            'Текущее количество',
        ]
        products_data = [
            (product.name, 'before_count', 'total_income_in_range', 'total_outcome_in_range', 'after_count', 'in_stock')
            for product in products
        ]

        df = pd.DataFrame(products_data, columns=column_names)

        current_datetime = timezone.now().strftime('%Y/%d/%m')
        excel_file_name = f'material_report_{current_datetime}'

        df.to_excel(excel_file_name, index=False)

        return excel_file_name


