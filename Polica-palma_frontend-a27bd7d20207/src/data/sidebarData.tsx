import {Banknote, ClipboardList, Flower2, Package, PackagePlus, ShoppingCart, Warehouse} from 'lucide-react'
import getUserData from '@/helpers/getUserData.ts'

const getSidebarData = () => {
  const { userType } = getUserData()

  const sidebarData: any[] = [
    userType !== 'CRAFTER' && userType !== 'CASHIER' && {
      icon: <Package />,
      title: 'Продукты',
      subNavItems: [
        userType !== 'MANAGER' && userType !== 'WAREHOUSE_MASTER' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'INCOME_MANAGER' && { link: '/dashboard/product/industries', text: 'Магазины' },
        userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'INCOME_MANAGER' && { link: '/dashboard/product/categories', text: 'Категории' },
        { link: '/dashboard/product/products', text: 'Товары' },
      ]
    },
    userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'CRAFTER' && {
      icon: <PackagePlus />,
      title: 'Закуп',
      subNavItems: [
        { link: '/dashboard/income/providers', text: 'Поставщики' },
        { link: '/dashboard/income/incomes', text: 'Закуп' },
      ]
    },
    userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'CRAFTER' && userType !== 'INCOME_MANAGER' && {
      icon: <Warehouse />,
      title: 'Склад',
      subNavItems: [
        { link: '/dashboard/warehouse/products', text: 'Товары из склада' },
        { link: '/dashboard/warehouse/write-off', text: 'Списанные товары' },
      ]
    },
    userType !== 'WAREHOUSE_MASTER' && userType !== 'CRAFTER' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'INCOME_MANAGER' && {
      icon: <ShoppingCart />,
      title: 'Продажи',
      subNavItems: [
        { link: '/dashboard/order/orders', text: 'Продажи' },
        { link: '/dashboard/order/clients', text: 'Клиенты' },
      ]
    },
    userType !== 'MANAGER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'WAREHOUSE_MASTER' && userType !== 'CRAFTER' && userType !== 'INCOME_MANAGER' && {
      icon: <Banknote />,
      title: 'Оплата',
      subNavItems: [
        { link: '/dashboard/payment/payments', text: 'Платежи' },
        { link: '/dashboard/payment/outlays', text: 'Причины расхода' },
        // { link: '/dashboard/payment/shifts', text: 'Смена кассы' },
      ]
    },
    userType !== 'MANAGER' && userType !== 'INCOME_MANAGER' && {
      icon: <Flower2 />,
      title: 'Букеты',
      subNavItems: [
        userType !== 'CASHIER' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'CRAFTER' && { link: '/dashboard/factories/categories', text: 'Категории' },
        userType !== 'CASHIER' && { link: '/dashboard/factories/bouquets', text: 'Список букетов' },
        userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'CRAFTER' && { link: '/dashboard/factories/finished', text: 'Собранные букеты' },
        userType !== 'CASHIER' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'CRAFTER' && { link: '/dashboard/factories/written-off', text: 'Списанные букеты' },
        { link: '/dashboard/factories/bouquets-list', text: 'Букеты' }
      ]
    },
    userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'CRAFTER' && userType !== 'INCOME_MANAGER' && {
      icon: <ClipboardList />,
      title: 'Отчеты',
      subNavItems: [
        userType === 'ADMIN' && { link: '/dashboard/reports/overall', text: 'Общий отчет' },
        userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'WAREHOUSE_MASTER' && { link: '/dashboard/reports/orders', text: 'Отчеты по продажам' },
        userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'WAREHOUSE_MASTER' && { link: '/dashboard/reports/order-items', text: 'Отчеты по товарам' },
        userType !== 'CASHIER' && userType === 'ADMIN' && { link: '/dashboard/reports/clients', text: 'Отчеты по клиентам' },
        userType === 'ADMIN' || userType === 'CASHIER' || userType === 'WAREHOUSE_MASTER' ? { link: '/dashboard/reports/all-workers', text: 'Отчеты по сотрудникам' } : '',
        userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'MANAGER' && { link: '/dashboard/reports/florists', text: 'Отчеты по флористам' },
        userType !== 'CASHIER' && userType === 'ADMIN' && { link: '/dashboard/reports/write-offs', text: 'Отчеты по списаниям' },
        userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'MANAGER' && { link: '/dashboard/reports/bouquets', text: 'Отчеты по букетам' },
        userType !== 'CASHIER' && userType === 'ADMIN' && { link: '/dashboard/reports/returns', text: 'Отчеты по возвратам' },
        userType === 'ADMIN' || userType === 'CASHIER' ? { link: '/dashboard/reports/salesman', text: 'Отчеты по продавцам' } : '',
        userType === 'ADMIN' || userType === 'CASHIER' ? { link: '/dashboard/reports/another-salesman', text: 'Отчеты по прочим работникам' } : '',
        userType !== 'CASHIER' && userType !== 'SALESMAN' && userType !== 'NO_BONUS_SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'WAREHOUSE_MASTER' && { link: '/dashboard/reports/materials', text: 'Материальный отчет' },
      ]
    }
  ]

  return { sidebarData }
}

export default getSidebarData