from barcode import EAN13


def generate_product_code(product):
    return EAN13(str(100_000_000_000 + product.id)).get_fullcode()
