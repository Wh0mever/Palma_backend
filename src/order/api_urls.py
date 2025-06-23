from django.urls import path

from src.order import api_views

app_name = 'order'

urlpatterns = [
    path(
        "clients/",
        api_views.ClientViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "clients/<int:pk>/",
        api_views.ClientViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='client-detail'
    ),
    path(
        "clients/summary/",
        api_views.ClientViewSet.as_view(
            {
                "get": "get_summary",
            }
        )
    ),
    path(
        "departments/",
        api_views.DepartmentViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "departments/<int:pk>/",
        api_views.DepartmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='department-detail'
    ),
    path(
        "orders/",
        api_views.OrderViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "orders/summary/",
        api_views.OrderViewSet.as_view(
            {
                "get": "get_summary",
            }
        )
    ),
    path(
        "orders/export-excel/<int:user_id>/",
        api_views.OrderViewSet.as_view(
            {
                "get": "export_excel",
            }
        )
    ),
    path(
        "orders/<int:pk>/",
        api_views.OrderViewSet.as_view(
            {
                "get": "retrieve",
                "put": "partial_update",
                "delete": "destroy"
            }
        ),
        name='order-detail'
    ),
    path(
        "orders/<int:order_id>/order-items/",
        api_views.OrderItemViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "orders/<int:order_id>/order-items/<int:pk>/",
        api_views.OrderItemViewSet.as_view(
            {
                "put": "partial_update",
                "delete": "destroy"
            }
        )
    ),
    path(
        "orders/<int:order_id>/factory-product-order_items/",
        api_views.OrderItemProductFactoryViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        )
    ),
    path(
        "orders/<int:order_id>/factory-product-order_items/<int:pk>/",
        api_views.OrderItemProductFactoryViewSet.as_view(
            {
                "put": "partial_update",
                "delete": "destroy"
            }
        )
    ),
    # path("orders/<int:pk>/update-status/", api_views.OrderUpdateStatusView.as_view()),
    path('orders/statuses/', api_views.OrderStatusOptionsView.as_view()),
    path('orders/<int:pk>/complete-order/', api_views.OrderCompleteView.as_view()),
    path('orders/<int:pk>/cancel-order/', api_views.OrderCancelView.as_view()),
    path('orders/<int:pk>/restore-order/', api_views.OrderRestoreView.as_view()),
    path(
        'orders/<int:pk>/update-discount/',
        api_views.OrderViewSet.as_view(
            {
                "put": "update_discount"
            }
        )
    ),
    path(
        'orders/<int:order_id>/order-items/<int:order_item_id>/returns/',
        api_views.OrderItemProductReturnViewSet.as_view(
            {
                "get": "list",
                "post": "create",
            }
        )
    ),
    path(
        'orders/<int:order_id>/order-items/<int:order_item_id>/returns/<int:pk>/',
        api_views.OrderItemProductReturnViewSet.as_view(
            {
                "get": "retrieve",
                "delete": "destroy",
            }
        )
    ),
    path(
        "orders/<int:order_id>/factory-product-order_items/<int:pk>/returns/",
        api_views.OrderItemProductFactoryViewSet.as_view(
            {
                "get": "returned_products_list",
                "post": "return_product",
                "delete": "cancel_return_product"
            }
        )
    ),
]
