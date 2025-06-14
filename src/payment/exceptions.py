
class PaymentModelTypeInstanceDoesntExists(Exception):
    pass


class PaymentOrderDoesntExists(PaymentModelTypeInstanceDoesntExists):
    def __str__(self):
        return f"Платеж не привязан к заказу"


class PaymentIncomeDoesntExists(PaymentModelTypeInstanceDoesntExists):
    def __str__(self):
        return f"Платеж не привязан к приходу"


class PaymentProviderDoesntExists(PaymentModelTypeInstanceDoesntExists):
    def __str__(self):
        return f"Платеж не привязан к поставщику"


class PaymentOutlayDoesntExists(PaymentModelTypeInstanceDoesntExists):
    def __str__(self):
        return f"Платеж не привязан к прочему расходу"


class DontHaveStartedShifts:
    def __str__(self):
        return f"У вас нет открытых смен"