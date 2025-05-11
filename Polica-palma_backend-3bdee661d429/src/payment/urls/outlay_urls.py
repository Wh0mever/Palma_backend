from django.urls import path

from src.payment.views import outlay as api_views

app_name = 'outlay'

urlpatterns = [
    path(
        '',
        api_views.OutlayViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        '<int:pk>/',
        api_views.OutlayViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy",
            }
        )
    ),
    path('<int:pk>/payments/', api_views.OutlayPaymentListView.as_view()),
    path('types/', api_views.OutlayTypeOptionsView.as_view())
]
