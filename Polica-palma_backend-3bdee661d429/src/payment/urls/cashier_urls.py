from django.urls import path

from src.payment.views import cashier as api_views

app_name = 'cashier'

urlpatterns = [
    path('', api_views.CashierListView.as_view()),
    path('<int:pk>/', api_views.CashierRetrieveView.as_view()),
    path('display/', api_views.CashierDisplayListView.as_view()),
    path('shifts/create/', api_views.CashierShiftViewSet.as_view({'post': 'create'})),
    path('shifts/close/', api_views.CashierShiftViewSet.as_view({'post': 'close_shift'})),
    path('shifts/', api_views.CashierShiftViewSet.as_view({'get': 'list'})),
    path('shifts/get-current-shift/', api_views.CashierShiftViewSet.as_view({'get': 'get_current_shift'})),
    path('shifts/with-summary/', api_views.CashierShiftViewSet.as_view({'get': 'get_shifts_with_summary'})),

]
