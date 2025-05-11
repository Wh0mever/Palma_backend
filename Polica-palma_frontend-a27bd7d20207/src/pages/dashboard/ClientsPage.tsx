import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import ClientsSection from '@/components/sections/ClientsSection.tsx'

const ClientsPage = () => {
  return (
    <>
      <DashboardLayout>
        <ClientsSection />
      </DashboardLayout>
    </>
  )
}

export default ClientsPage