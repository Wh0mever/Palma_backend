/* eslint-disable @typescript-eslint/no-explicit-any */
type IdType = {
  id?: number | any
}

type PagesType = {
  count?: number | any
  total_pages?: number | any
  next?: string | any
  previous?: string | any
}

export type CashiersData = IdType & {
  name?: string | any
  amount?: string | any
}

export type CategoriesData = IdType & {
  name?: string | any
  industry?: IndustriesData
  is_composite?: boolean | any
  is_for_sale?: boolean | any
}

export type ClientsData = IdType & {
  full_name?: string | any
  phone_number?: string | any
  debt?: string | any
  comment?: string | any
}

export type ClientsReportClientList = IdType & {
  full_name?: string | any
  phone_number?: string | any
  debt?: string | any
  orders_count?: string | any
  orders_sum?: string | any
  total_discount_sum?: string | any
}

export type ClientsReport = {
  total_debt?: string | any
  total_orders_count?: string | any
  total_orders_sum?: string | any
  clients?: ClientsReportClientList
}

export type ClientsReportOrderList = IdType & {
  name?: string | any
  debt?: string | any
  total_with_discount?: string | any
  created_at?: string | any
}

export type ClientsReportOrder = PagesType & {
  results?: ClientsReportOrderList
}

export type ClientsReportOrderData = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: ClientsReport
}

export type DepartmentsData = IdType & {
  name?: string | any
}

export type IncomesData = IdType & {
  provider?: ProvidersData
  total?: string | any
  total_sale_price?: string | any
  status?: string
  comment?: string | any
  created_at?: string
  provider_name?: string | any
}

export type IncomesDataPages = PagesType & {
  results?: IncomesData
}

export type IncomeItemsData = IdType & {
  product?: ProductsData
  count?: string | any
  price?: string | any
  sale_price?: string | any
  total?: string | any
}

export type IndustriesData = IdType & {
  name?: string | any
  industry?: string | any
  charge_percent?: string | any
  has_sale_compensation?: boolean | any
  sale_compensation_percent?: string | any
}

export type IndustryChartTable = {
  name?: string | any
  total_turnover_sum?: string | any
  share_percentage?: string | any
}

export type OutlaysChartTable = {
  total_payments_amount?: string | any
  outlays?: OutlaysData
}

export type TurnoverChartTable = {
  label?: string | any
  total_sum?: string | any
  percentage?: string | any
}

export type MaterialReportProductList = IdType & {
  name?: string | any
  total_income_in_range?: string | any
  total_outcome_in_range?: string | any
  total_income_after_range?: string | any
  total_outcome_after_range?: string | any
  total_income_before_range?: string | any
  total_outcome_before_range?: string | any
  current_count?: string | any
  before_count?: string | any
  after_count?: string | any
  product_in_orders_count?: string | any
  product_in_incomes_count?: string | any
  product_in_factories_count?: string | any
  product_write_offs_count?: string | any
  product_order_returns_count?: string | any
  product_factory_returns_count?: string | any
}

export type MaterialReportResults = {
  products?: MaterialReportProductList
}

export type MaterialReport = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportResults
}

export type MaterialReportFactoriesList = IdType & {
  name?: string | any
  product_count?: string | any
  florist?: UserProfileData
  created_at?: string | any
}

export type MaterialReportFactoriesReturnsList = IdType & {
  product_name?: string | any
  count?: string | any
  created_at?: string | any
}

export type MaterialReportIncomesList = IdType & {
  product_count?: string | any
  provider?: ProvidersData
  created_at?: string | any
}

export type MaterialReportOrdersList = IdType & {
  order_name?: string | any
  product_count?: string | any
  client?: ClientsData
  created_at?: string | any
}

export type MaterialReportProductReturnsList = IdType & {
  count?: string | any
  order_name?: string | any
  created_at?: string | any
}

export type MaterialReportWriteOffList = IdType & {
  count?: string | any
  created_at?: string | any
}

export type MaterialReportFactories = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportFactoriesList
}

export type MaterialReportFactoriesReturns = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportFactoriesReturnsList
}

export type MaterialReportIncomes = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportIncomesList
}

export type MaterialReportOrders = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportOrdersList
}

export type MaterialReportProductReturns = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportProductReturnsList
}

export type MaterialReportWriteOff = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: MaterialReportWriteOffList
}

export type OrdersClients = ClientsData & {
  total_orders_sum?: string | any
  total_orders_profit_sum?: string | any
  debt?: string | any
}

export type OrdersData = IdType & {
  client?: OrdersClients
  department?: DepartmentsData
  status?: string
  discount?: string | any
  total?: string | any
  created_at?: string
  debt?: string | any
  total_with_discount?: string | any
  client_name?: string | any
  amount_paid?: string | any
  amount_returned?: string | any
  order_items?: OrderItems
  product_returns?: OrderItemReturns
  order_item_factory_products?: FactoryOrderItems
  factory_product_returns?: FactoryOrderItemsReturns
  created_user?: UserProfileData
  comment?: string | any
  salesman?: UserProfileData
  payments?: OrdersPaymentsData[]
}

export type OrdersDataPages = PagesType & {
  results?: OrdersData
}

export type OrderItems = IdType & {
  product?: ProductsData
  price?: string | any
  count?: string | any
  total?: string | any
  returned_count?: string | any
  order?: OrdersData
}

export type OrderItemReturns = IdType & {
  order?: string | any
  order_item?: string | any
  product_name?: string | any
  count?: string | any
  total?: string | any
  created_at?: string | any
}

export type OrderListReport = IdType & {
  total?: string | any
  total_with_discount?: string | any
  amount_paid?: string | any
  total_discount?: string | any
  total_charge?: string | any
  total_self_price?: string | any
  total_profit?: string | any
  debt?: string | any
  client?: string | any
  industry?: IndustriesData
  status?: 'CREATED' | 'COMPLETED' | 'CANCELLED'
  created_at?: string | any
}

export type OrderReport = {
  total_sale_amount?: string | any
  total_sale_with_discount_amount?: string | any
  total_discount_amount?: string | any
  total_charge_amount?: string | any
  total_self_price_amount?: string | any
  total_profit_amount?: string | any
  total_debt_amount?: string | any
  orders: OrderListReport
}

export type OrdersReportsData = PagesType & {
  results: OrderReport
}

export type OrderItemsList = IdType & {
  order?: OrdersData
  product?: ProductsData
  client_name?: string | any
  price?: string | any
  count?: string | any
  discount?: string | any
  total?: string | any
  total_discount?: string | any
  total_self_price?: string | any
}

export type OrderItemsReportsSummary = {
  total_sum?: string | any
  total_count_sum?: string | any
  total_discount_sum?: string | any
  total_self_price_sum?: string | any
  total_profit_sum?: string | any
  total_returned_count_sum?: string | any
  total_charge_sum?: string | any
}

export type OrderItemsReportsPages = PagesType & {
  results?: OrderItemsList
}

export type OutlaysData = IdType & {
  title?: string | any
  industry?: IndustriesData
  outlay_type?: "INVESTMENT" | "SPENDING" | any
  created_at? : string | any
  comment?: string | any
  amount?: string | any
  payment_method?: string | any
  payments?: PaymentsData
}

export type OutlaysDataPages = PagesType & {
  results?: OutlaysData
}

export type OutlaysTypesData = {
  value?: string | any
  label?: string | any
}

export type OrdersPaymentsData = IdType & PaymentsData & {
  payment_method?: PaymentMethods
}

export type PaymentsDataResults = PagesType & {
  results?: PaymentsData
}

export type PaymentsData = IdType & {
  payment_method?: "CASH" | "CARD" | "TRANSFER" | "TRANSFER_TO_CARD"
  payment_type?: "INCOME" | "OUTCOME"
  payment_model_type?: "OUTLAY" | "ORDER" | "INCOME" | "PROVIDER"
  amount?: string | any
  created_at?: string | any
  comment?: string | any
  income?: IncomesData
  order?: OrdersData
  provider?: ProvidersData
  outlay?: OutlaysData
}

export type PaymentsDataSummary = {
  total_income?: string | any
  total_outcome?: string | any
  total_profit?: string | any
  total_count?: string | any
  payments?: PaymentsData
}

export type PaymentsDataPages = PagesType & {
  results?: PaymentsDataSummary
}

export type ShiftList = IdType & {
  start_date?: string | any
  end_date?: string | any
  started_user?: UserProfileData
  completed_user?: UserProfileData
  total_income?: string | any
  total_outcome?: string | any
  total_profit?: string | any
}

export type ShiftSummary = {
  total_income_sum?: string | any
  total_outcome_sum?: string | any
  total_profit_sum?: string | any
  shifts?: ShiftList
}

export type ShiftSummaryPage = PagesType & {
  results?: ShiftSummary
}

export type HistoryIncomeItems = IdType & {
  count?: string | any
  price?: string | any
  sale_price?: string | any
  total?: string | any
  created_at?: string | any
}

export type HistoryData = IdType & {
  name?: string | any
  income_items?: HistoryIncomeItems
}

export type FactoriesCategoriesData = IdType & {
  name?: string | any
}

export type FactoriesSalesTypesData = {
  value: string
  label: string
}

export type FactoryOrderItems = IdType & {
  order?: number | any
  product_factory?: ProductFactoriesData
  price?: string | any
  total?: string | any
  count?: string | any
  is_returned?: boolean | any
}

export type FactoryOrderItemsReturns = IdType & {
  product_name?: string | any
  total?: string | any
  count?: string | any
  created_at?: string | any
}

export type FloristsReportFloristList = IdType & {
  name?: string | any
  type?: "ADMIN" | "SALESMAN" | "FLORIST" | "FLORIST_PERCENT" | "MANAGER" | "WAREHOUSE_MASTER"
  finished_product_count?: string | any
  sold_product_count?: string | any
  written_off_product_count?: string | any
  total_product_count?: string | any
  income_sum?: string | any
  payment_sum?: string | any
  balance?: string | any
}

export type FloristsReport = PagesType & {
  results?: FloristsReportFloristList
}

export type FloristsReportFactoriesList = IdType & {
  name?: string | any
  product_code?: string | any
  category?: CategoriesData
  sales_type?:  "STORE" | "SHOWCASE" | "CONGRATULATION"
  price?: string | any
  self_price?: string | any
}

export type FloristsReportFactories = PagesType & {
  results?: FloristsReportFactoriesList
}

export type FloristsReportIncomes = PagesType & {
  results?: WorkerIncome
}

export type FloristsReportPayments = PagesType & {
  results?: WorkerPayment
}

export type FloristsReportSummary = {
  total_sold_product_count?: string | any
  total_finished_product_count?: string | any
  total_written_off_product_count?: string | any
  total_income_sum?: string | any
  total_payment_sum?: string | any
}

export type FactoriesReturnsList = IdType & {
  order?: number | any
  order_name?: string | any
  product_factory?: ProductFactoriesData
  price?: string | any
  count?: string | any
  total?: string | any
  total_self_price?: string | any
  returned_at?: string | any
}

export type FactoriesReturnsReports = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: FactoriesReturnsList
}

export type StatusesData = {
  value?: string | any
  label?: string | any
}

export type ProductsData = IdType & {
  name?: string | any
  unit_type?: string | any
  code?: string
  price?: string | any
  category?: CategoriesData
  in_stock?: string | any
  image?: string | any
  is_product_factory?: boolean | any
  is_barcode_printable?: boolean | any
  related_providers?: ProvidersData
}

export type ProductsDataPages = PagesType & {
  results?: ProductsData
}

export type ProductsCompositeData = IdType & ProductsData & {
  warehouse_products?: WarehouseData
}

export type ProductFactoryItemReturn = IdType & {
  count?: string | any
  total_self_price?: string | any
  total_price?: string | any
  created_at?: string | any
}

export type ProductFactoriesItems = IdType & {
  warehouse_product?: WarehouseData
  count?: string | any
  total_price?: string | any
  total_self_price?: string | any
  returns?: ProductFactoryItemReturn
  returned_count?: string | any
}

export type ProductFactoriesData = IdType & {
  name?: string | any
  product_code?: string | any
  category?: FactoriesCategoriesData
  image?: string | any
  price?: string | any
  self_price?: string | any
  status?: "CREATED" | "FINISHED" | "SOLD" | "WRITTEN_OFF"
  sales_type?: "STORE" | "SHOWCASE" | "CONGRATULATION" | any
  florist?: UserProfileData
  created_at?: string | any
  finished_at?: string | any
  is_product_factory?: boolean | any
  items?: ProductFactoriesItems
  returns?: ProductFactoryItemReturn
  sold_user?: UserProfileData
  order?: OrdersData
}

export type ProductFactoriesDataPages = PagesType & {
  results?: ProductFactoriesData
}

export type ProvidersData = IdType & {
  full_name?: string | any
  phone_number?: string | any
  org_name?: string
  balance?: string | any
  comment?: string
}

export type ProductsOptionsData = IdType & {
  value?: string | any
  label?: string | any
}

export type ProductFactoriesReport = PagesType & {
  results?: ProductFactoriesData
}

export type ProductFactoriesReportSummary = {
  total_finished_self_price?: string | any
  total_finished_price?: string | any
  total_finished_count?: string | any
  total_sold_self_price?: string | any
  total_sold_price?: string | any
  total_sold_count?: string | any
  total_written_off_self_price?: string | any
  total_written_off_count?: string | any
  total_product_count?: string | any
}

export type ProductReturnsList = IdType & {
  order?: number | any
  order_name?: string | any
  product?: ProductsData
  price?: string | any
  count?: string | any
  total?: string | any
  total_self_price?: string | any
  created_at?: string | any
}

export type ProductReturnsReports = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: ProductReturnsList
}

export type ProductFactorySellsTable = {
  name?: string | any
  self_price?: { amount?: string | any, percentage?: string | any }
  worker_income?: { amount?: string | any, percentage?: string | any }
  profit?: { amount?: string | any, percentage?: string | any }
}

export type ReturnsReportSummary = {
  total_product_returns?: string | any
  total_product_returns_price?: string | any
  total_product_returns_self_price?: string | any
  total_product_factory_returns?: string | any
  total_product_factory_returns_price?: string | any
  total_product_factory_returns_self_price?: string | any
  total_returns?: string | any
  total_price?: string | any
  total_self_price?: string | any
}

export type SalesmanReportWorkerList = IdType & {
  name?: string | any
  industry?: IndustriesData
  balance?: string | any
  orders_count?: string | any
  order_total_sum?: string | any
  income_sum?: string | any
  payment_sum?: string | any
}

export type SalesmanReport = PagesType & {
  results?: SalesmanReportWorkerList
}

export type SalesmanReportSummary = {
  total_orders_count?: string | any
  total_orders_sum?: string | any
  total_income_sum?: string | any
  total_payments_sum?: string | any
}

export type AnotherSalesmanReportList = IdType & {
  name?: string | any
  balance?: string | any
  payment_sum?: string | any
}

export type AnotherSalesmanReportSummary = {
  total_payments_sum?: string | any
}

export type AnotherSalesmanReport = PagesType & {
  results?: AnotherSalesmanReportList
}

export type AnotherSalesmanReportPaymentsList = IdType & {
  payment_name?: string | any
  amount?: string | any
  payment_type?: "INCOME" | "OUTCOME"
  payment_model_type?: "OUTLAY" | "ORDER" | "INCOME" | "PROVIDER"
  created_at?: string | any
  comment?: string | any
}

export type AnotherSalesmanReportPayments = PagesType & {
  results?: AnotherSalesmanReportPaymentsList
}

export type WorkerIncome = IdType & {
  income_name?: string | any
  order?: number | any
  total?: string | any
  income_type?: "INCOME" | "OUTCOME"
  reason?: "PRODUCT_SALE" | "PRODUCT_FACTORY_SALE" | "PRODUCT_FACTORY_CREATE" | "BONUS" | "SALARY" | "FINE"
  created_at?: string | any
}

export type WorkerOrders = IdType & {
  order_name?: string | any
  total_with_discount?: string | any
  created_at?: string | any
}

export type WorkerPayment = IdType & {
  payment_name?: string | any
  amount?: string | any
  payment_type?: "INCOME" | "OUTCOME"
  payment_model_type?: "OUTLAY" | "ORDER" | "INCOME" | "PROVIDER"
  created_at?: string | any
}

export type SalesmanReportIncomes = PagesType & {
  results?: WorkerIncome
}

export type SalesmanReportOrders = PagesType & {
  results?: WorkerOrders
}

export type SalesmanReportPayments = PagesType & {
  results?: WorkerPayment
}

export type UserProfileData = IdType & {
  username?: string | any
  first_name?: string | any
  last_name?: string | any
  avatar?: string | any
  birthday?: string | any
  type?: "ADMIN" | "SALESMAN" | "FLORIST" | "FLORIST_PERCENT" | "MANAGER" | "WAREHOUSE_MASTER" | any
  industry?: IndustriesData
}

export type WarehouseData = IdType & {
  product?: ProductsData
  count?: string | any
  self_price?: string | any
  sale_price?: string | any
  created_at?: string | any
  product_name?: string | any
}

export type WarehouseDataPages = PagesType & {
  results?: WarehouseData
}

export type WriteOffData = IdType & {
  warehouse_product?: WarehouseData
  product_name?: string | any
  count?: string | any
  comment?: string | any
  created_at?: string | any
}

export type WriteOffDataPages = PagesType & {
  results?: WriteOffData
}

export type WriteOffReportProductList = IdType & {
  name?: string | any
  code?: string | any
  category?: CategoriesData
  product_count?: string | any
  self_price_sum?: string | any
}

export type WriteOffSummary = {
  total_product_count?: string | any
  total_self_price_sum?: string | any
  total_product_factory_count?: string | any
  total_product_factory_self_price_sum?: string | any
  total_count?: string | any
  total_self_price?: string | any
}

export type WriteOffReport = {
  count?: number | any
  next?: string | any
  previous?: string | any
  results?: WriteOffReportProductList
}

export type WriteOffsReportProductWriteOff = IdType & {
  count?: string | any
  self_price?: string | any
  created_at?: string | any
  comment?: string | any
}

export type WriteOffEditReport = PagesType & {
  results?: WriteOffsReportProductWriteOff
}

export type WriteOffTablesMain = {
  title?: string | any
  self_price_sum?: string | any
  self_price_percentage?: string | any
}

export type WriteOffTablesCount = {
  title?: string | any
  write_off_count?: string | any
}

export type WriteOffTablesSum = {
  title?: string | any
  write_off_count?: string | any
}

export type WriteOffTables = {
  main_table?: WriteOffTablesMain[]
  count_table?: WriteOffTablesCount[]
  sum_table?: WriteOffTablesSum[]
}

export type IndicatorData = {
  value?: string | any
  label?: string | any
}

export type UserTypes = "ADMIN" | "SALESMAN" | "FLORIST" | "FLORIST_PERCENT" | "MANAGER" | "WAREHOUSE_MASTER" | "CRAFTER" | "NO_BONUS_SALESMAN" | "CASHIER" | null | string

type PaymentType = {
  value: string
  label: string
}

type PaymentMethod = {
  value: string
  label: string
}

type PaymentModelType = {
  value: string
  label: string
}

export type PaymentMethods = IdType & {
  name: string
}

export type PaymentMethodCategory = IdType & {
  name?: string | any
  payment_methods?: PaymentMethods
}

export type CreateOptionsData = {
  payment_types: PaymentType[]
  payment_methods: PaymentMethod[]
  payment_model_types: PaymentModelType[]
}