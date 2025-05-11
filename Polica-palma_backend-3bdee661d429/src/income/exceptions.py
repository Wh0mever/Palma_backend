
class IncompleteIncomeItemError(Exception):
    def __init__(self, message="Существуют незаполненные элементы прихода."):
        self.message = message
        super().__init__(self.message)