import {BrowserRouter as Router, Route, Routes} from 'react-router-dom'
import LoginPage from '@/pages/LoginPage.tsx'
import {ThemeProvider} from '@/components/theme-provider.tsx'
import NotFoundPage from '@/pages/NotFoundPage.tsx'
import DashboardPage from '@/pages/DashboardPage.tsx'
import ProductsPage from '@/pages/dashboard/ProductsPage.tsx'
import CategoriesPage from '@/pages/dashboard/CategoriesPage.tsx'
import IndustriesPage from '@/pages/dashboard/IndustriesPage.tsx'
import IndustriesEditPage from '@/pages/dashboard/edit/IndustriesEditPage.tsx'
import CategoriesEditPage from '@/pages/dashboard/edit/CategoriesEditPage.tsx'
import ProductsEditPage from '@/pages/dashboard/edit/ProductsEditPage.tsx'
import ProvidersPage from '@/pages/dashboard/ProvidersPage.tsx'
import ProvidersEditPage from '@/pages/dashboard/edit/ProvidersEditPage.tsx'
import IncomesPage from '@/pages/dashboard/IncomesPage.tsx'
import IncomesEditPage from '@/pages/dashboard/edit/IncomesEditPage.tsx'
import IncomeItemsEditPage from '@/pages/dashboard/edit/IncomeItemsEditPage.tsx'
import WarehousePage from '@/pages/dashboard/WarehousePage.tsx'
import ClientsPage from '@/pages/dashboard/ClientsPage.tsx'
import ClientsEditPage from '@/pages/dashboard/edit/ClientsEditPage.tsx'
import OrdersPage from '@/pages/dashboard/OrdersPage.tsx'
import OrdersEditPage from '@/pages/dashboard/edit/OrdersEditPage.tsx'
import PaymentsPage from '@/pages/dashboard/PaymentsPage.tsx'
import OutlaysPage from '@/pages/dashboard/OutlaysPage.tsx'
import OutlaysEditPage from '@/pages/dashboard/edit/OutlaysEditPage.tsx'
import WriteOffPage from '@/pages/dashboard/WriteOffPage.tsx'
import CashiersProvider from '@/providers/CashiersProvider.tsx'
import NoAccessPage from '@/pages/NoAccessPage.tsx'
import BouquetsPage from '@/pages/dashboard/BouquetsPage.tsx'
import FactoriesCategoriesPage from '@/pages/dashboard/FactoriesCategoriesPage.tsx'
import FactoriesCategoriesEditPage from '@/pages/dashboard/edit/FactoriesCategoriesEditPage.tsx'
import BouquetsEditPage from '@/pages/dashboard/edit/BouquetsEditPage.tsx'
import FinishedBouquetsPage from '@/pages/dashboard/FinishedBouquetsPage.tsx'
import WriteOffBouquetsPage from '@/pages/dashboard/WriteOffBouquetsPage.tsx'
import OrdersReportsPage from '@/pages/dashboard/OrdersReportsPage.tsx'
import ClientsReportsPage from '@/pages/dashboard/ClientsReportsPage.tsx'
import ClientsReportsEditPage from '@/pages/dashboard/edit/ClientsReportsEditPage.tsx'
import FloristsReportsPage from '@/pages/dashboard/FloristsReportsPage.tsx'
import WriteOffReportsPage from '@/pages/dashboard/WriteOffReportsPage.tsx'
import FloristsReportsEditPage from '@/pages/dashboard/edit/FloristsReportsEditPage.tsx'
import WriteOffReportsEditPage from '@/pages/dashboard/edit/WriteOffReportsEditPage.tsx'
import BouquetsReportsPage from '@/pages/dashboard/BouquetsReportsPage.tsx'
import ReturnsReportsPage from '@/pages/dashboard/ReturnsReportsPage.tsx'
import SalesmanReportsPage from '@/pages/dashboard/SalesmanReportsPage.tsx'
import SalesmanReportsEditPage from '@/pages/dashboard/edit/SalesmanReportsEditPage.tsx'
import MaterialReportsPage from '@/pages/dashboard/MaterialReportsPage.tsx'
import MaterialReportsEditPage from '@/pages/dashboard/edit/MaterialReportsEditPage.tsx'
import ShiftsPage from '@/pages/dashboard/ShiftsPage.tsx'
import OrderItemsReportsPage from '@/pages/dashboard/OrderItemsReportsPage.tsx'
import AnotherSalesmanReportsPage from "@/pages/dashboard/AnotherSalesmanReportsPage.tsx"
import AnotherSalesmanReportsEditPage from "@/pages/dashboard/edit/AnotherSalesmanReportsEditPage.tsx"
import AllWorkersReportsPage from "@/pages/dashboard/AllWorkersReportsPage.tsx"
import AllWorkersReportsEditPage from "@/pages/dashboard/edit/AllWorkersReportsEditPage.tsx"
import OverallReportsPage from "@/pages/dashboard/OverallReportsPage.tsx"
import BouquetsListPage from "@/pages/dashboard/BouquetsListPage.tsx"

function App() {
  return (
    <>
      <ThemeProvider storageKey='vite-ui-theme'>
        <CashiersProvider>
          <Router>
            <Routes>
              <Route path='*' element={<NotFoundPage />} />
              <Route path='/noaccess/' element={<NoAccessPage />} />
              <Route path='/auth/login/' element={<LoginPage />} />
              <Route path='/' element={<DashboardPage />} />

              <Route path='/dashboard/product/products/' element={<ProductsPage />} />
              <Route path='/dashboard/product/categories/' element={<CategoriesPage />} />
              <Route path='/dashboard/product/industries/' element={<IndustriesPage />} />
              <Route path='/dashboard/income/providers/' element={<ProvidersPage />} />
              <Route path='/dashboard/income/incomes/' element={<IncomesPage />} />
              <Route path='/dashboard/warehouse/products/' element={<WarehousePage />} />
              <Route path='/dashboard/warehouse/write-off/' element={<WriteOffPage />} />
              <Route path='/dashboard/order/clients/' element={<ClientsPage />} />
              <Route path='/dashboard/order/orders/' element={<OrdersPage />} />
              <Route path='/dashboard/payment/payments/' element={<PaymentsPage />} />
              <Route path='/dashboard/payment/outlays/' element={<OutlaysPage />} />
              <Route path='/dashboard/payment/shifts/' element={<ShiftsPage />} />

              <Route path='/dashboard/product/products/edit/:id/' element={<ProductsEditPage />} />
              <Route path='/dashboard/product/industries/edit/:id/' element={<IndustriesEditPage />} />
              <Route path='/dashboard/product/categories/edit/:id/' element={<CategoriesEditPage />} />
              <Route path='/dashboard/income/providers/edit/:id/' element={<ProvidersEditPage />} />
              <Route path='/dashboard/income/incomes/edit/:id/' element={<IncomesEditPage />} />
              <Route path='/dashboard/income/incomes/edit/:id/income-items/edit/:incomeId' element={<IncomeItemsEditPage />} />
              <Route path='/dashboard/order/clients/edit/:id/' element={<ClientsEditPage />} />
              <Route path='/dashboard/order/orders/edit/:id/' element={<OrdersEditPage />} />
              <Route path='/dashboard/payment/outlays/edit/:id/' element={<OutlaysEditPage />} />

              <Route path='/dashboard/factories/categories/' element={<FactoriesCategoriesPage />} />
              <Route path='/dashboard/factories/categories/edit/:id/' element={<FactoriesCategoriesEditPage />} />
              <Route path='/dashboard/factories/bouquets/' element={<BouquetsPage />} />
              <Route path='/dashboard/factories/bouquets/edit/:id/' element={<BouquetsEditPage />} />
              <Route path='/dashboard/factories/finished/' element={<FinishedBouquetsPage />} />
              <Route path='/dashboard/factories/written-off/' element={<WriteOffBouquetsPage />} />
              <Route path='/dashboard/factories/bouquets-list/' element={<BouquetsListPage />} />

              <Route path='/dashboard/reports/overall/' element={<OverallReportsPage />} />
              <Route path='/dashboard/reports/orders/' element={<OrdersReportsPage />} />
              <Route path='/dashboard/reports/order-items/' element={<OrderItemsReportsPage />} />
              <Route path='/dashboard/reports/clients/' element={<ClientsReportsPage />} />
              <Route path='/dashboard/reports/clients/:id/' element={<ClientsReportsEditPage />} />
              <Route path='/dashboard/reports/florists/' element={<FloristsReportsPage />} />
              <Route path='/dashboard/reports/all-workers/' element={<AllWorkersReportsPage />} />
              <Route path='/dashboard/reports/all-workers/:id/' element={<AllWorkersReportsEditPage />} />
              <Route path='/dashboard/reports/florists/:id/' element={<FloristsReportsEditPage />} />
              <Route path='/dashboard/reports/write-offs/' element={<WriteOffReportsPage />} />
              <Route path='/dashboard/reports/write-offs/:id/' element={<WriteOffReportsEditPage />} />
              <Route path='/dashboard/reports/bouquets/' element={<BouquetsReportsPage />} />
              <Route path='/dashboard/reports/returns/' element={<ReturnsReportsPage />} />
              <Route path='/dashboard/reports/salesman/' element={<SalesmanReportsPage />} />
              <Route path='/dashboard/reports/salesman/:id/' element={<SalesmanReportsEditPage />} />
              <Route path='/dashboard/reports/another-salesman/' element={<AnotherSalesmanReportsPage />} />
              <Route path='/dashboard/reports/another-salesman/:id/' element={<AnotherSalesmanReportsEditPage />} />
              <Route path='/dashboard/reports/materials/' element={<MaterialReportsPage />} />
              <Route path='/dashboard/reports/materials/:id/' element={<MaterialReportsEditPage />} />
            </Routes>
          </Router>
        </CashiersProvider>
      </ThemeProvider>
    </>
  )
}

export default App