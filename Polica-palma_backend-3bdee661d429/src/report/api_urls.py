from django.urls import path

from src.report import api_views

app_name = 'report'

urlpatterns = [
    path('orders-report/', api_views.OrderReportView.as_view({'get': 'list'})),
    path('orders-report/excel-export/<int:user_id>/', api_views.OrderReportView.as_view({'get': 'get_excel_report'})),
    path(
        'material-report/',
        api_views.MaterialReportView.as_view(
            {
                'get': 'list'
            }
        )
    ),
    path(
        'material-report-test/',
        api_views.MaterialReportTestView.as_view(
            {
                'get': 'list'
            }
        )
    ),
    path(
        'material-report/excel-export/<int:user_id>/',
        api_views.MaterialReportView.as_view(
            {
                'get': 'get_excel_report'
            }
        )
    ),
    path(
        'material-report-test/excel-export/<int:user_id>/',
        api_views.MaterialReportTestView.as_view(
            {
                'get': 'get_excel_report'
            }
        )
    ),
    path('material-report/<int:pk>/', api_views.MaterialReportDetailView.as_view()),
    path('material-report/<int:pk>/orders/', api_views.MaterialReportOrderListView.as_view()),
    path('material-report/<int:pk>/incomes/', api_views.MaterialReportIncomesListView.as_view()),
    path('material-report/<int:pk>/factories/', api_views.MaterialReportProductFactoryListView.as_view()),
    path('material-report/<int:pk>/write-offs/', api_views.MaterialReportWriteOffListView.as_view()),
    path('material-report/<int:pk>/product-returns/', api_views.MaterialReportOrderItemReturnListView.as_view()),
    path('material-report/<int:pk>/factory-item-returns/', api_views.MaterialReportFactoryItemReturnListView.as_view()),

    path('salesmen-report/salesmen/', api_views.SalesmenReportSalesmenListView.as_view()),
    path('salesmen-report/summary/', api_views.SalesmenReportSummaryView.as_view({'get': 'list'})),
    path('salesmen-report/export-excel/<int:user_id>/',
         api_views.SalesmenReportSummaryView.as_view({'get': 'get_excel_report'})),
    path('salesmen-report/<int:pk>/orders/', api_views.SalesmenReportOrderListView.as_view()),
    path('salesmen-report/<int:pk>/incomes/', api_views.WorkerIncomeListView.as_view()),
    path('salesmen-report/<int:pk>/payments/', api_views.WorkerPaymentListView.as_view()),
    path('salesmen-report/<int:pk>/', api_views.SalesmenReportDetailView.as_view()),

    path('florists-report/forists/', api_views.FloristsReportFloristListView.as_view()),
    path('florists-report/summary/', api_views.FloristsReportSummaryView.as_view({'get': 'list'})),
    path('florists-report/export-excel/<int:user_id>/',
         api_views.FloristsReportSummaryView.as_view({'get': 'get_excel_report'})),
    path('florists-report/<int:pk>/', api_views.FloristReportDetailView.as_view()),
    path('florists-report/<int:pk>/factories/', api_views.FloristReportProductFactoryListView.as_view()),
    path('florists-report/<int:pk>/incomes/', api_views.WorkerIncomeListView.as_view()),
    path('florists-report/<int:pk>/payments/', api_views.WorkerPaymentListView.as_view()),

    path('all-workers-report/workers/', api_views.WorkersReportWorkerListView.as_view()),
    path('all-workers-report/summary/', api_views.WorkersReportSummaryView.as_view({'get': 'list'})),
    path('all-workers-report/<int:pk>/', api_views.WorkersReportDetailView.as_view()),
    path('all-workers-report/worker-type-options/', api_views.WorkersTypeOptionsView.as_view()),
    path('all-workers-report/export-excel/<int:user_id>/', api_views.WorkersReportSummaryView.as_view(
        {'get': 'get_excel_report'}
    )),

    path('workers-report/workers/', api_views.OtherWorkersReportListView.as_view()),
    path('workers-report/summary/', api_views.OtherWorkersReportSummaryView.as_view({'get': 'list'})),
    path('workers-report/export-excel/<int:user_id>/',
         api_views.OtherWorkersReportSummaryView.as_view({'get': 'get_excel_report'})),
    path('workers-report/<int:pk>/payments/', api_views.WorkerPaymentListView.as_view()),
    path('workers-report/<int:pk>/', api_views.OtherWorkerReportDetailView.as_view()),

    # path('write-offs-report/', api_views.WriteOffsReportView.as_view()),
    path('write-offs-report/products/', api_views.WriteOffReportProductsListView.as_view()),
    path('write-offs-report/product-factories/', api_views.WriteOffsReportProductFactoriesListView.as_view()),
    path('write-offs-report/summary/', api_views.WriteOffReportSummaryView.as_view({'get': "list"})),
    path('write-offs-report/export-excel/<int:user_id>/',
         api_views.WriteOffReportSummaryView.as_view({'get': 'get_excel_report'})),
    path('write-offs-report/<int:pk>/', api_views.WriteOffsReportDetailView.as_view()),
    path('write-offs-report/<int:pk>/write-offs/', api_views.WriteOffReportWriteOffListView.as_view()),

    path('clients-report/', api_views.ClientsReportView.as_view({'get': 'list'})),
    path('clients-report/export-excel/<int:user_id>/',
         api_views.ClientsReportView.as_view({'get': 'get_excel_report'})),
    path('clients-report/<int:pk>/', api_views.ClientsReportDetailView.as_view()),
    path('clients-report/<int:pk>/orders/', api_views.ClientsReportOrderListView.as_view()),

    # path('product-factories-report/', api_views.ProductFactoriesReportView.as_view()),
    path('product-factories-report/products/', api_views.ProductFactoriesReportProductFactoryListView.as_view()),
    path('product-factories-report/summary/', api_views.ProductFactoriesReportSummaryView.as_view({'get': 'list'})),
    path('product-factories-report/excel-report/<int:user_id>/',
         api_views.ProductFactoriesReportSummaryView.as_view({'get': 'get_excel_report'})),

    path('product-returns-report/product-returns/', api_views.ProductReturnsReportProductReturnListView.as_view()),
    path('product-returns-report/factory-returns/', api_views.ProductReturnsReportFactoriesListView.as_view()),
    path('product-returns-report/summary/', api_views.ProductReturnsReportSummaryView.as_view({'get': 'list'})),
    path('product-returns-report/excel-report/<int:user_id>/',
         api_views.ProductReturnsReportSummaryView.as_view({'get': 'get_excel_report'})),

    path('order-items-report/', api_views.OrderItemsReport.as_view({'get': 'list'})),
    path('order-items-report/order_items/', api_views.OrderItemsReportOrderItemList.as_view()),
    path('order-items-report/order_item_factories/', api_views.OrderItemsReportOrderItemFactoryList.as_view()),
    path('order-items-report/excel-report/<int:user_id>/',
         api_views.OrderItemsReport.as_view({'get': 'get_excel_report'})),

    path('overall-report/', api_views.OverallReportView.as_view())
]
