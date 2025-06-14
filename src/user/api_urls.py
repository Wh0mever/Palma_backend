from django.urls import path

from src.user import api_views

app_name = 'user'

urlpatterns = [
    path(
        "",
        api_views.UserViewSet.as_view(
            {
                "get": "list"
            }
        )
    ),
    path(
        "workers/",
        api_views.UserViewSet.as_view(
            {
                "get": "workers"
            }
        )
    ),
    path(
        "product-factory-creators/",
        api_views.UserViewSet.as_view(
            {
                "get": "product_factory_creators"
            }
        )
    ),
    path(
        "have-orders/",
        api_views.UserViewSet.as_view(
            {
                "get": "have_orders"
            }
        )
    ),
    path(
        "have-orders-created/",
        api_views.UserViewSet.as_view(
            {
                "get": "have_orders_created"
            }
        )
    ),
    path(
        "salesmen-list/",
        api_views.UserViewSet.as_view(
            {
                "get": "salesmen_list"
            }
        )
    ),
    path(
        "payment-creators/",
        api_views.UserViewSet.as_view(
            {
                "get": "payment_creators"
            }
        )
    ),
    path(
        "has-shift/",
        api_views.UserViewSet.as_view(
            {
                "get": "has_active_shift"
            }
        )
    ),
    path(
        "profile/",
        api_views.UserProfileViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update"
            }
        )
    ),
    path('login/', api_views.UserLoginView.as_view()),
    path('register/', api_views.UserRegistrationView.as_view()),
    path('change-password/', api_views.UserChangePasswordView.as_view()),
    path('types/', api_views.UserTypeOptionsView.as_view()),
    path('worker-income/types/', api_views.WorkerIncomeTypeOptionsView.as_view()),
    path('worker-income/reasons/', api_views.WorkerIncomeReasonOptionsView.as_view()),
]
