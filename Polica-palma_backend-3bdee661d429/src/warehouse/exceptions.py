

class NotEnoughProductInWarehouseError(Exception):
    def __init__(self, message="Недостаточно товаров на складе."):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"Товара недостаточно на складе"
