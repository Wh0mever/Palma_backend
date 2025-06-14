class NotEnoughProductsInOrderItemError(Exception):
    def __init__(self, message="Недостаточно товаров в элементе заказа."):
        self.message = message
        super().__init__(self.message)


class OrderHasReturnError(Exception):
    def __init__(self, message="Нельзя восстановить заказ с возвратами."):
        self.message = message
        super().__init__(self.message)


class RestoreTimeExceedError(Exception):
    def __init__(self, message="Восстановление заказа невозможно спустя сутки после его создания."):
        self.message = message
        super().__init__(self.message)
