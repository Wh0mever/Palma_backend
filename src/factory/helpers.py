from barcode import EAN13


def generate_product_code(product_factory):
    return EAN13(str(200_000_000_000 + product_factory.id)).get_fullcode()
