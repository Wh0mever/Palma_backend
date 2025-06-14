from django.urls import path

from src.analytics import api_views

app_name = 'analytics'

urlpatterns = [
    path('profit/', api_views.ProfitAnalyticsView.as_view()),
    path('profit-by-industry/', api_views.IndustryProfitAnalyticsView.as_view()),
    path('cashier/', api_views.CashierIncomeAnalyticsView.as_view()),
    path('industry-pie-chart/chart/', api_views.IndustryShareOfTurnoverAnalyticsView.as_view({'get': 'get_chart_data'})),
    path('industry-pie-chart/table/', api_views.IndustryShareOfTurnoverAnalyticsView.as_view({'get': 'get_table_data'})),
    path('turnover-pie-chart/chart/', api_views.OverallTurnoverShareAnalyticsView.as_view({'get': 'get_chart_data'})),
    path('turnover-pie-chart/table/', api_views.OverallTurnoverShareAnalyticsView.as_view({'get': 'get_table_data'})),
    path('products/', api_views.ProductsAnalyticsView.as_view()),
    path('products/options/', api_views.ProductIndicatorOptionsView.as_view()),
    path('florists/', api_views.FloristsAnalyticsView.as_view()),
    path('florists/options/', api_views.FloristsIndicatorOptionsView.as_view()),
    path('salesmen/', api_views.SalesmenAnalyticsView.as_view()),
    path('salesmen/options/', api_views.SalesmenIndicatorOptionsView.as_view()),
    path('write-offs/chart/', api_views.WriteOffsAnalyticsView.as_view({'get': 'get_chart_data'})),
    path('write-offs/tables/', api_views.WriteOffsAnalyticsView.as_view({'get': 'get_tables_data'})),
    path('outlays/chart/', api_views.OutlaysAnalyticsView.as_view({'get': 'get_chart_data'})),
    path('outlays/table/', api_views.OutlaysAnalyticsView.as_view({'get': 'get_table_data'})),
    path('outlays/options/', api_views.OutlaysIndicatorOptionsView.as_view()),
    path('products-factory-sells/chart/', api_views.ProductFactorySellsAnalyticsView.as_view({'get': 'get_chart_data'})),
    path('products-factory-sells/table/', api_views.ProductFactorySellsAnalyticsView.as_view({'get': 'get_table_data'})),

    path('clients/chart/', api_views.ClientsAnalyticsViewSet.as_view({'get': 'get_chart_data'})),
    path('clients/top/', api_views.ClientsAnalyticsViewSet.as_view({'get': 'get_clients'})),
    path('clients/linear/', api_views.ClientsAnalyticsViewSet.as_view({'get': 'get_linear_chart_data'})),
]
