import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import OrdersSection from '@/components/sections/OrdersSection.tsx'

const OrdersPage = () => {
  return (
    <>
      <DashboardLayout>
        <OrdersSection />
      </DashboardLayout>
    </>
  )
}

export default OrdersPage