import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import PaymentsSection from '@/components/sections/PaymentsSection.tsx'

const PaymentsPage = () => {
  return (
    <>
      <DashboardLayout>
        <PaymentsSection />
      </DashboardLayout>
    </>
  )
}

export default PaymentsPage