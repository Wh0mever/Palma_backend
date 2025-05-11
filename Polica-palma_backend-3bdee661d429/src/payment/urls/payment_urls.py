from django.urls import path

from src.payment.views import payment as api_views

app_name = 'payment'

urlpatterns = [
    path(
        '',
        api_views.PaymentViewSet.as_view(
            {
                "get": "list",
            }
        )
    ),
    path(
        'with-summary/',
        api_views.PaymentViewSet.as_view(
            {
                "get": "get_with_summary_list",
            }
        )
    ),
    path(
        '<int:pk>/',
        api_views.PaymentViewSet.as_view(
            {
                "get": "retrieve",
                # "put": "partial_update",
                "delete": "destroy",
            }
        )
    ),
    path('create-options/', api_views.PaymentCreateOptionsView.as_view()),
    path('filter-options/', api_views.PaymentModelTypeFilterOptionsView.as_view()),
    path('outlays/', api_views.OutlayPaymentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('outlays/<int:pk>/', api_views.OutlayPaymentViewSet.as_view({'delete': 'destroy', 'put': 'update'})),
    path('providers/', api_views.ProviderPaymentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('providers/<int:pk>/', api_views.ProviderPaymentViewSet.as_view({'delete': 'destroy', 'put': 'update'})),
    path('incomes/', api_views.IncomePaymentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('incomes/<int:pk>/', api_views.IncomePaymentViewSet.as_view({'delete': 'destroy', 'put': 'update'})),
    path('orders/', api_views.OrderPaymentViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('orders/<int:pk>/', api_views.OrderPaymentViewSet.as_view({'delete': 'destroy', 'put': 'update'})),

    path('payment-method-categories/', api_views.PaymentMethodCategoryViewSet.as_view({'get': 'list'})),
    path('payment-methods/', api_views.PaymentMethodViewSet.as_view({'get': 'list'})),
]
