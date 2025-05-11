const translatedData: { [key: string]: string } = {
  CREATED: 'Создан',
  ACCEPTED: 'Принят',
  COMPLETED: 'Завершен',
  CANCELLED: 'Отменен',
  FINISHED: 'Завершен',
  SOLD: 'Продан',
  WRITTEN_OFF: 'Списан',
  PENDING: 'В ожидании',

  INVESTMENT: 'Инвестиция',
  SPENDING: 'Затраты',
  WORKERS: 'Сотрудники',

  INCOME: 'Приход',
  OUTCOME: 'Расход',

  CASH: 'Наличными',
  CARD: 'Картой',
  TRANSFER: 'Перечисление',
  TRANSFER_TO_CARD: 'Перевод на карту',

  OUTLAY: 'Расходы',
  ORDER: 'Заказ',
  PROVIDER: 'Поставщик',

  STORE: 'Магазин',
  SHOWCASE: 'Витрина',
  CONGRATULATION: 'Поздравление',

  PIECE: 'шт.',
  METER: 'м.',
  CENTIMETER: 'см.',
  BRANCH: 'ветка',

  ADMIN: 'Админ',
  SALESMAN: 'Продавец',
  FLORIST: 'Флорист',
  FLORIST_PERCENT: 'Флорист с процентной ставкой',
  MANAGER: 'Менеджер',
  WAREHOUSE_MASTER: 'Складовщик',
  CRAFTER: 'Сборщик',
  FLORIST_ASSISTANT: 'Помощник флориста',
  OTHER: 'Прочие сотрудники',
  NO_BONUS_SALESMAN: 'Продавец без бонусов',

  PRODUCT_SALE: 'Продажа товара',
  PRODUCT_FACTORY_SALE: 'Продажа букета',
  PRODUCT_FACTORY_CREATE: 'Создание букета',
  BONUS: 'Бонус',
  SALARY: 'Зарплата',
  FINE: 'Штраф',
}

const translateFunc = (type: string | any) => {
  return translatedData[type] || type
}

export default translateFunc