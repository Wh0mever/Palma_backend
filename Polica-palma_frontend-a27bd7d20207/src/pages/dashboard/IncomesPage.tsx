import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import IncomesSection from '@/components/sections/IncomesSection.tsx'

const IncomesPage = () => {
  return (
    <>
      <DashboardLayout>
        <IncomesSection />
      </DashboardLayout>
    </>
  )
}

export default IncomesPage