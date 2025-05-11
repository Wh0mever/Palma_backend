import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import ProductsSection from '@/components/sections/ProductsSection.tsx'

const ProductsPage = () => {
  return (
    <>
      <DashboardLayout>
        <ProductsSection />
      </DashboardLayout>
    </>
  )
}

export default ProductsPage