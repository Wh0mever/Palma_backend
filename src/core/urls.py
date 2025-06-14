from django.urls import path

from . import views


urlpatterns = [
    path("print-barcode/product/<int:product_id>/", views.print_barcode, name='print-product-barcode'),
    path("print-receipt/order/<int:order_id>/", views.print_receipt, name='print-order-receipt'),
    path("print-receipt/factory/<int:factory_id>/", views.print_factory_receipt, name='print-factory-receipt'),
    path("products-export/<int:industry_id>/", views.industry_products_print),
    path("product-factories-export/<int:user_id>/", views.product_factories_export, name='product-factories-export'),
    path("product-factories-print/", views.ProductFactoriesPrintView.as_view(), name='product-factories-print')
]