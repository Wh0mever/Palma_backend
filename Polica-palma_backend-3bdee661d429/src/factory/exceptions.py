class NotEnoughProductInFactoryItemError(Exception):
    def __init__(self, message="Недостаточно товаров в элементе производства."):
        self.message = message
        super().__init__(self.message)


class CantToAddProductFactoryToOrder(Exception):
    def __init__(self, message="Невозможно добавить товар из производства к заказу."):
        self.message = message
        super().__init__(self.message)


class FloristDoesntHavePenaltyError(Exception):
    def __init__(self, message="Невозможно добавить штрафной букет к флористу. У Флориста нет штрафов."):
        self.message = message
        super().__init__(self.message)
