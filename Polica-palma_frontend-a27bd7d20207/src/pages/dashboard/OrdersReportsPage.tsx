import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import OrdersReportsSection from '@/components/sections/OrdersReportsSection.tsx'

const OrdersReportsPage = () => {
  return (
    <>
      <DashboardLayout>
        <OrdersReportsSection />
      </DashboardLayout>
    </>
  )
}

export default OrdersReportsPage