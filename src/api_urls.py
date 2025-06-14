from django.conf import settings
from django.urls import path, include

urlpatterns = [
    path('', include('src.product.api_urls', namespace='product')),
    path('', include('src.warehouse.api_urls', namespace='warehouse')),
    path('', include('src.income.api_urls', namespace='income')),
    path('', include('src.order.api_urls', namespace='order')),
    path('users/', include('src.user.api_urls', namespace='user')),
    path('outlays/', include('src.payment.urls.outlay_urls', namespace='outlay')),
    path('payments/', include('src.payment.urls.payment_urls', namespace='payment')),
    path('cashiers/', include('src.payment.urls.cashier_urls', namespace='cashier')),
    path('factories/', include('src.factory.urls.product_factories_urls', namespace='factory')),
    path('product-factory-categories/', include('src.factory.urls.category_urls', namespace='product-factory-category')),
    path('reports/', include('src.report.api_urls', namespace='report')),
    path('analytics/', include('src.analytics.api_urls', namespace='analytics')),
]