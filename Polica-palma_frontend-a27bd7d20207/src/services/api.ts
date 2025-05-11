import {createApi, fetchBaseQuery} from "@reduxjs/toolkit/query/react"
import getUrl from "@/config.js"
import getAuthorizationHeader from "@/helpers/getAuthHeader.ts"

export const api = createApi({
  reducerPath: "clientApi",
  baseQuery: fetchBaseQuery({baseUrl: getUrl()}),
  tagTypes: [
    "Shift",
    "Industries",
    "Providers",
    "Categories",
    "FactoriesCategories",
    "Clients",
    "Products",
    "Incomes",
    "Warehouse",
    "WriteOffs",
    "Orders",
    "Cashiers",
    "Factories",
    "Payments",
    "Outlays",
    "Bouquets",
    "Florists",
    "OrderReturns"
  ],

  endpoints: (builder) => ({

    // GET Requests
    getShiftReport: builder.query({
      query: (queryString) => ({
        url: `api/cashiers/shifts/with-summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Shift"]
    }),

    getShiftStatus: builder.query({
      query: () => ({
        url: `api/users/has-shift/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Shift"]
    }),

    getOrderReport: builder.query({
      query: (queryString) => ({
        url: `api/reports/orders-report/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Orders"]
    }),

    getOrderItemsReport: builder.query({
      query: ({ queryString, item }) => ({
        url: item ? `api/reports/order-items-report/${item}/?${queryString}` : `api/reports/order-items-report/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Orders", "Products"]
    }),

    getIndustries: builder.query({
      query: (id) => ({
        url: id ? `api/industries/${id}/` : `api/industries/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
      providesTags: ["Industries"]
    }),

    getProviders: builder.query({
      query: ({ id, queryString }) => ({
        url: id ? `api/providers/${id}/?${queryString}` : `api/providers/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
      providesTags: ["Providers"]
    }),

    getCategories: builder.query({
      query: (id) => ({
        url: id ? `api/categories/${id}/` : `api/categories/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 500,
      providesTags: ["Categories"]
    }),

    getFactoriesCategories: builder.query({
      query: (id) => ({
        url: id ? `api/product-factory-categories/product-factory-categories/${id}/` : `api/product-factory-categories/product-factory-categories/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 500,
      providesTags: ["FactoriesCategories"]
    }),

    getFactoriesReturns: builder.query({
      query: ({ id, factoryItemID }) => ({
        url: `api/factories/product-factories/${id}/items/${factoryItemID}/returns/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["OrderReturns"]
    }),

    getFinishedFactories: builder.query({
      query: (queryString) => ({
        url: `api/factories/product-factories/finished/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Factories"]
    }),

    getWrittenOffFactories: builder.query({
      query: (queryString) => ({
        url: `api/factories/product-factories/written-off/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Factories"]
    }),

    getWrittenOffFactoriesSummary: builder.query({
      query: (queryString) => ({
        url: `api/factories/product-factories/written-off/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Factories"]
    }),

    getFactoriesSalesTypes: builder.query({
      query: () => ({
        url: `api/factories/product-factories/sales-types/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Factories"]
    }),

    getCompositeCategories: builder.query({
      query: () => ({
        url: `api/categories/composite/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Categories"]
    }),

    getCompositeProducts: builder.query({
      query: () => ({
        url: `api/products/composites`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Products"]
    }),

    getClients: builder.query({
      query: ({ id, queryString }) => ({
        url: id ? `api/clients/${id}/?${queryString}` : `api/clients/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Clients"]
    }),

    getProducts: builder.query({
      query: ({ id, params }) => ({
        url: id ? `api/products/${id}/` : `api/products/`,
        method: "GET",
        params: params ? params : '',
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Products"]
    }),

    getProvidersProducts: builder.query({
      query: (id) => ({
        url: `api/providers/${id}/products/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Products"]
    }),

    getProductsOptions: builder.query({
      query: () => ({
        url: `api/products/options/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
    }),

    getIncomes: builder.query({
      query: ({ id, params }) => ({
        url: id ? `api/incomes/${id}/` : `api/incomes/`,
        method: "GET",
        params: params ? params : '',
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Incomes"]
    }),

    getIncomeItems: builder.query({
      query: (id) => ({
        url: `api/incomes/${id}/income-items/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Incomes"]
    }),

    getIncomesSummary: builder.query({
      query: (queryString) => ({
        url: `api/incomes/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Incomes"]
    }),

    getPaymentMethods: builder.query({
      query: () => ({
        url: `api/payments/payment-methods/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 1000,
      providesTags: ["Payments"]
    }),

    getPaymentCreateOptions: builder.query({
      query: () => ({
        url: `api/payments/create-options/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 1000,
      providesTags: ["Payments"]
    }),

    getPaymentFilterOptions: builder.query({
      query: () => ({
        url: `api/payments/filter-options/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 1000,
      providesTags: ["Payments"]
    }),

    getOutlaysTypes: builder.query({
      query: () => ({
        url: `api/outlays/types/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Outlays"]
    }),

    getFlorists: builder.query({
      query: () => ({
        url: `api/users/product-factory-creators/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getHaveOrdersUsers: builder.query({
      query: () => ({
        url: `api/users/have-orders-created/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
    }),

    getOutlays: builder.query({
      query: ({ queryString, id }) => ({
        url: queryString ? `api/outlays/?${queryString}` : id ? `api/outlays/${id}/` : `api/outlays/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Outlays"]
    }),

    getOutlaysPayments: builder.query({
      query: ({ queryString, id }) => ({
        url: `api/outlays/${id}/payments/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Outlays"]
    }),

    getSalesman: builder.query({
      query: () => ({
        url: `api/users/salesmen-list/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getWorkers: builder.query({
      query: () => ({
        url: `api/users/workers/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getWorkerIncomeTypes: builder.query({
      query: () => ({
        url: `api/users/worker-income/types/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getWarehouse: builder.query({
      query: (queryString) => ({
        url: `api/warehouse/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Warehouse"]
    }),

    getWarehouseSummary: builder.query({
      query: (queryString) => ({
        url: `api/warehouse/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Warehouse"]
    }),

    getIncomeHistory: builder.query({
      query: (id) => ({
        url: `api/products/${id}/income-history/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getWriteOffs: builder.query({
      query: (queryString) => ({
        url: `api/warehouse/write-offs/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["WriteOffs"]
    }),

    getOrders: builder.query({
      query: ({id, queryString}) => ({
        url: id ? `api/orders/${id}/` : `api/orders/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Orders"]
    }),

    getOrdersSummary: builder.query({
      query: (queryString) => ({
        url: `api/orders/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Orders"]
    }),

    getDepartments: builder.query({
      query: () => ({
        url: `api/departments/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
    }),

    getSalesmanList: builder.query({
      query: () => ({
        url: `api/users/salesmen-list/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getPaymentMethodCategories: builder.query({
      query: () => ({
        url: `api/payments/payment-method-categories/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      providesTags: ["Payments"]
    }),

    getCashiers: builder.query({
      query: () => ({
        url: `api/cashiers/display/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Cashiers"]
    }),

    getCategoriesForSale: builder.query({
      query: () => ({
        url: `api/categories/for-sale/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Categories"]
    }),

    getProductsForSale: builder.query({
      query: () => ({
        url: `api/products/for-sale-list/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Products"]
    }),

    getFactoriesForSale: builder.query({
      query: () => ({
        url: `api/factories/product-factories/for-sale/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Factories"]
    }),

    getOrderItemsReturns: builder.query({
      query: ({ id, orderItemID }) => ({
        url: `api/orders/${id}/order-items/${orderItemID}/returns/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["OrderReturns"]
    }),

    getFactoryOrderItemsReturns: builder.query({
      query: ({ id, factoryOrderID }) => ({
        url: `api/orders/${id}/factory-product-order_items/${factoryOrderID}/returns/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["OrderReturns"]
    }),

    getPaymentsWithSummary: builder.query({
      query: (queryString) => ({
        url: `api/payments/with-summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["Payments"]
    }),

    getBouquets: builder.query({
      query: ({ id, queryString }) => ({
        url: queryString ? `api/factories/product-factories/?${queryString}` : `api/factories/product-factories/${id}/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Bouquets"]
    }),

    getBouquetsSummary: builder.query({
      query: (queryString) => ({
        url: `api/factories/product-factories/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
      providesTags: ["Bouquets"]
    }),

    getAnalytics: builder.query({
      query: ({ queryString, item }) => ({
        url: `api/analytics/${item}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 60,
    }),

    getClientsReports: builder.query({
      query: ({ id, queryString }) => ({
        url: id ? `api/reports/clients-report/${id}/?${queryString}` : `api/reports/clients-report/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Clients"]
    }),

    getClientsReportsOrders: builder.query({
      query: ({ id, queryString }) => ({
        url: `api/reports/clients-report/${id}/orders/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Clients", "Orders"]
    }),

    getFloristsReports: builder.query({
      query: ({ id, queryString, item }) => ({
        url: item && !id ? `api/reports/florists-report/${item}/?${queryString}` : item && id ? `api/reports/florists-report/${id}/${item}/?${queryString}` : `api/reports/florists-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 500,
      providesTags: ["Florists"]
    }),

    getWriteOffsReports: builder.query({
      query: ({ id, queryString, item }) => ({
        url: item && !id ? `api/reports/write-offs-report/${item}/?${queryString}` : item && id ? `api/reports/write-offs-report/${id}/${item}/?${queryString}` : `api/reports/write-offs-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
      providesTags: ["WriteOffs"]
    }),

    getBouquetsReports: builder.query({
      query: ({ item, queryString }) => ({
        url: `api/reports/product-factories-report/${item}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
      providesTags: ["Bouquets"]
    }),

    getReturnsReports: builder.query({
      query: ({ item, queryString }) => ({
        url: `api/reports/product-returns-report/${item}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getSalesmanReports: builder.query({
      query: ({ id, queryString, item }) => ({
        url: item && !id ? `api/reports/salesmen-report/${item}/?${queryString}` : item && id ? `api/reports/salesmen-report/${id}/${item}/?${queryString}` : `api/reports/salesmen-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getAnotherWorkersReports: builder.query({
      query: ({ id, queryString, item }) => ({
        url: item && !id ? `api/reports/workers-report/${item}/?${queryString}` : item && id ? `api/reports/workers-report/${id}/${item}/?${queryString}` : `api/reports/workers-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getMaterialReportsId: builder.query({
      query: ({ id, queryString }) => ({
        url: `api/reports/material-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getMaterialReports: builder.query({
      query: ({ id, queryString, item }) => ({
        url: id && item ? `api/reports/material-report/${id}/${item}/?${queryString}` : id && queryString ? `api/reports/material-report/${id}/?${queryString}` : `api/reports/material-report/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getIncomesIncomeItems: builder.query({
      query: ({ id, incomeId }) => ({
        url: `api/incomes/${id}/income-items/${incomeId}/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 120,
    }),

    getIncomeReasons: builder.query({
      query: () => ({
        url: `api/users/worker-income/reasons/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getUsersForPayments: builder.query({
      query: () => ({
        url: `api/users/workers/?type=ADMIN&type=CASHIER`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getIndicator: builder.query({
      query: (url) => ({
        url: url,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getStatuses: builder.query({
      query: (url) => ({
        url: url,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getCreated: builder.query({
      query: (url) => ({
        url: url,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 3600,
    }),

    getAllWorkersReportSummary: builder.query({
      query: (queryString) => ({
        url: `api/reports/all-workers-report/summary/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getAllWorkersReportId: builder.query({
      query: ({ id, queryString }) => ({
        url: `api/reports/all-workers-report/${id}/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getAllWorkersReportWorkers: builder.query({
      query: (queryString) => ({
        url: `api/reports/all-workers-report/workers/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getAllWorkersReportTypeOptions: builder.query({
      query: () => ({
        url: `api/reports/all-workers-report/worker-type-options/`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),

    getOverallReport: builder.query({
      query: (queryString) => ({
        url: `api/reports/overall-report/?${queryString}`,
        method: "GET",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      keepUnusedDataFor: 300,
    }),


    // POST Requests
    createShift: builder.mutation({
      query: ({...data}) => ({
        url: "api/cashiers/shifts/create/",
        method: "POST",
        body: data,
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: ["Shift"]
    }),

    closeShift: builder.mutation({
      query: ({...data}) => ({
        url: "api/cashiers/shifts/close/",
        method: "POST",
        body: data,
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: ["Shift"]
    }),

    postData: builder.mutation({
      query: ({ url, body }) => ({
        url: url,
        method: "POST",
        body: body,
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: (_result, _error, { invalidatesTags }) => invalidatesTags
    }),

    updateStatus: builder.mutation({
      query: ({ url, body }) => ({
        url: url,
        method: "POST",
        body: body,
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: (_result, _error, { invalidatesTags }) => invalidatesTags
    }),


    // PUT Requests
    putData: builder.mutation({
      query: ({ url, body }) => ({
        url: url,
        method: "PUT",
        body: body,
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: (_result, _error, { invalidatesTags }) => invalidatesTags
    }),


    // DELETE Requests
    deleteData: builder.mutation({
      query: ({url}) => ({
        url: url,
        method: "DELETE",
        headers: {
          Authorization: getAuthorizationHeader(),
        },
      }),
      invalidatesTags: (_result, _error, { invalidatesTags }) => invalidatesTags
    }),
  })
})