/* eslint-disable @typescript-eslint/no-explicit-any */
import DashboardLayout from "@/components/elements/DashboardLayout.tsx"
import {useNavigate, useParams} from "react-router-dom"
import SearchItem from "@/components/items/SearchItem.tsx"
import {Button} from "@/components/ui/button.tsx"
import {useEffect, useState} from "react"
import ProductCard from "@/components/ui/ProductCard.tsx"
import {ScrollArea} from "@/components/ui/scroll-area.tsx"
import useAxiosPost from "@/hooks/useAxiosPost.ts"
import AddForm from "@/components/others/AddForm.tsx"
import {z} from "zod"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import useAxiosPut from "@/hooks/useAxiosPut.ts"
import EditDialog from "@/components/others/EditDialog.tsx"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from "@/components/ui/dialog.tsx"
import ErrorItem from "@/components/items/ErrorItem.tsx"
import PaymentDialog from "@/components/others/PaymentDialog.tsx"
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table"
import {ChevronLeft, Eye, ReceiptText, Trash2} from "lucide-react"
import ReturnDialog from "@/components/others/ReturnDialog"
import formatDate from "@/helpers/formatDate"
import NumberFormField from "@/components/others/NumberFormField.tsx"
import EditSectionSkeleton from "@/components/skeletons/EditSectionSkeleton.tsx"
import CategoriesSkeleton from "@/components/skeletons/CategoriesSkeleton.tsx"
import ProductsSkeleton from "@/components/skeletons/ProductsSkeleton.tsx"
import SectionTableSkeleton from "@/components/skeletons/SectionTableSkeleton.tsx"
import useDeleteItem from "@/hooks/useDeleteItem.ts"
import getUrl from "@/config.ts"
import useScanner from "@/hooks/useScanner.ts"
import InputFormField from "@/components/others/InputFormField.tsx"
import useValues from "@/hooks/useValues"
import OrderCompleteItem from "@/components/items/OrderCompleteItem.tsx"
import getUserData from "@/helpers/getUserData.ts"
import translatedData from "@/data/translatedData.ts"
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"
import DatePicker from "@/components/others/DatePicker.tsx"

interface InputValues {
  count: string
  price: string
  discount: string
  factoryPrice: string
}

const OrdersEditPage = () => {
  const {id} = useParams()
  const navigate = useNavigate()
  const {keyList: productsKeyList} = useScanner()
  const {keyList: bouquetsKeyList} = useScanner()
  const {userType, userId} = getUserData()
  const {formatter} = useNumberFormatter()
  const {deleteItem, isDeleting, error, errorText} = useDeleteItem()
  const initialSelectedCategory = localStorage.getItem("selectedCategory") || ""
  const initialFactorySelectedCategory = localStorage.getItem("selectedFactoryCategory") || ""
  const {data, isLoading, isFetching} = api.useGetOrdersQuery({ id: id })
  const {data: paymentMethods, isLoading: paymentMethodsLoading} = api.useGetPaymentMethodsQuery('')

  const [amountError, setAmountError] = useState<boolean>(false)
  const [calculatedValue, setCalculatedValue] = useState<string>("")
  const [completeOrderValues, setCompleteOrderValues] = useState<{ [key: string]: string | number }>({})
  const [selectedCategory, setSelectedCategory] = useState(initialSelectedCategory)
  const [selectedFactoryCategory, setSelectedFactoryCategory] = useState(initialFactorySelectedCategory)
  const [searchValue, setSearchValue] = useState<string>("")
  const [orderID, setOrderID] = useState<string>("")
  const [factoryOrderID, setFactoryOrderID] = useState<string>("")
  const [orderItemID, setOrderItemID] = useState<string>("")
  const [dataStatusError, setDataStatusError] = useState<boolean>(false)
  const [inputValues, setInputValues] = useState<InputValues>({
    count: "",
    price: "",
    discount: "",
    factoryPrice: ""
  })

  const {inputValues: editValues, handleInputChange: editValuesChange} = useValues(
    {
      comment: ""
    },
    {
      comment: data && data?.comment
    },
    isLoading,
    data
  )

  const {data: categoriesData, isLoading: categoriesLoading} = api.useGetCategoriesForSaleQuery('')
  const {data: factoryCategoriesData, isLoading: factoryCategoriesLoading} = api.useGetFactoriesCategoriesQuery('')
  const {data: productsData, isLoading: productsLoading, isFetching: productsFetching} = api.useGetProductsForSaleQuery('')
  const {data: factoryProductsData, isLoading: factoryProductsLoading, isFetching: factoryProductsFetching} = api.useGetFactoriesForSaleQuery('')
  const {data: clientsData, isLoading: clientsLoading} = api.useGetClientsQuery('')
  const {data: departmentsData, isLoading: departmentsLoading} = api.useGetDepartmentsQuery('')
  const {data: orderReturnsData} = api.useGetOrderItemsReturnsQuery({ id: id, orderItemID: orderItemID })
  const {data: factoryReturnsData} = api.useGetFactoryOrderItemsReturnsQuery({ id: id, factoryOrderID: factoryOrderID })
  const {data: salesmanData, isLoading: salesmanLoading} = api.useGetSalesmanListQuery('')

  const [completeOrderPost, { isLoading: completePending }] = api.usePostDataMutation()
  const [scannerAddProduct, { isLoading: scannerAddProductPending }] = api.usePostDataMutation()
  const [scannerAddBouquet, { isLoading: scannerAddBouquetPending }] = api.usePostDataMutation()
  const [addProduct, { isLoading: addProductPending }] = api.usePostDataMutation()
  const [addBouquet, { isLoading: addBouquetPending }] = api.usePostDataMutation()
  const [cancelOrderPost, { isLoading: cancelOrderPostPending }] = api.usePostDataMutation()
  const [restoreOrderPost, { isLoading: restorePending, error: restoreError }] = api.usePostDataMutation<any>()

  // const {data: hasShiftData, isLoading: hasShiftIsLoading} = api.useGetShiftStatusQuery("")
  // const [createShift, {isLoading: openPending}] = api.useCreateShiftMutation<any>()

  const {success, form, onSubmit} = useAxiosPost(
    {
      product: z.string({required_error: "Пожалуйста, выберите продукт"}),
      count: z.string({required_error: "Пожалуйста, введите количество продукта"}),
    },
    {},
    `api/orders/${id}/order-items/`,
    ["Orders"]
  )

  const {success: factorySuccess, form: factoryForm, onSubmit: factorySubmit} = useAxiosPost(
    {
      product_factory: z.string({required_error: "Пожалуйста, выберите продукт"}),
    },
    {},
    `api/orders/${id}/factory-product-order_items/`,
    ["Orders"]
  )

  const {success: completeOrderSuccess, form: completeOrderForm, onSubmit: completeOrderSubmit} = useAxiosPost(
    {
      id: z.string().optional(),
      amount: z.string().optional(),
    },
    {
      "payments": [{"id": 0, "amount": "0.00"}]
    },
    `api/orders/${id}/complete-order/`,
    ["Orders", "Payments"]
  )

  const {success: orderSuccess, form: orderForm, onSubmit: orderSubmit, pending: orderPending} = useAxiosPut(
    {
      client: z.string().optional(),
      department: z.string().optional(),
      salesman: z.string().optional(),
      comment: z.string().optional(),
      created_at: z.date().optional()
    },
    {},
    `api/orders`,
    id,
    ["Orders"]
  )

  // const { success: totalSuccess, form: totalForm, onSubmit: totalSubmit, pending: totalPending } = useAxiosPut(
  //   {
  //     discount: z.string({ required_error: "Пожалуйста, введите новую скидку" }),
  //   },
  //   {
  //     "discount": inputValues.discount.replace(/\s/g, '')
  //   },
  //   `api/orders`,
  //   `${id}/update-discount`,
  //   () => {
  //     if (refetchData) {
  //       refetchData()
  //     }
  //   }
  // )

  const {success: countSuccess, form: countForm, onSubmit: countSubmit, pending: countPending} = useAxiosPut(
    {
      count: z.string({required_error: "Пожалуйста, введите количество"}),
    },
    {
      "count": inputValues.count.replace(/\s/g, "")
    },
    `api/orders/${id}/order-items`,
    orderID,
    ["Orders", "Products", "Factories"]
  )

  const {success: priceSuccess, form: priceForm, onSubmit: priceSubmit, pending: pricePending} = useAxiosPut(
    {
      price: z.string({required_error: "Пожалуйста, введите цену"}),
    },
    {
      "price": inputValues.price.replace(/\s/g, "")
    },
    `api/orders/${id}/order-items`,
    orderID,
    ["Orders"]
  )

  const {form: factoryPriceForm, success: factoryPriceSuccess, onSubmit: factoryPriceSubmit, pending: factoryPricePending} = useAxiosPut(
    {
      price: z.string({required_error: "Пожалуйста, введите цену"}),
    },
    {
      "price": inputValues.factoryPrice.replace(/\s/g, "")
    },
    `api/orders/${id}/factory-product-order_items`,
    factoryOrderID,
    ["Orders"]
  )

  useEffect(() => {
    localStorage.setItem("selectedCategory", selectedCategory)
    localStorage.setItem("selectedFactoryCategory", selectedFactoryCategory)
  }, [selectedCategory, selectedFactoryCategory])

  useEffect(() => {
    if (countSuccess || priceSuccess || factoryPriceSuccess || completeOrderSuccess) {
      setInputValues({
        ...inputValues,
        count: "",
        price: "",
        discount: "",
        factoryPrice: ""
      })
    }
  }, [countSuccess, priceSuccess, factoryPriceSuccess, inputValues, completeOrderSuccess])

  const filteredProducts = productsData && Array.isArray(productsData) && productsData.filter((item) => {
    const categoryFilter = selectedCategory && selectedCategory ? String(item.category?.id) === selectedCategory : true
    const searchFilter = item.name?.toLowerCase().includes(searchValue.toLowerCase()) || item.code?.includes(searchValue.toLowerCase())
    return categoryFilter && searchFilter
  })

  const filteredFactoryProducts = factoryProductsData && Array.isArray(factoryProductsData) && factoryProductsData.filter((item) => {
    const factoryCategoryFilter = selectedFactoryCategory && selectedFactoryCategory ? String(item.category?.id) === selectedFactoryCategory : true
    const searchFilter = item.name?.toLowerCase().includes(searchValue.toLowerCase()) || item.product_code?.includes(searchValue.toLowerCase())
    return factoryCategoryFilter && searchFilter
  })

  const handleSearch = (e: any) => {
    const inputValue = e.target.value
    setSearchValue(inputValue)
  }

  const handleInputValuesChange = (key: keyof InputValues, value: string) => {
    setInputValues({
      ...inputValues,
      [key]: value
    })
  }

  const handleInputChange = (name: string, value: string) => {
    setCompleteOrderValues(prevState => ({
      ...prevState,
      [name]: value
    }))
  }

  const calculateTotal = () => {
    let total = Number(data?.debt)

    for (const key in completeOrderValues) {
      total -= Number(completeOrderValues[key].toString().replace(/\s/g, ""))
    }

    const inputValue = Object.values(completeOrderValues).reduce((acc, val) => Number(acc) + Number(val.toString().replace(/\s/g, "")), 0)
    const debtValue = Number(String(data?.debt).slice(0, -3))

    setAmountError(Number(inputValue) > Number(debtValue))

    return String(total)
  }

  const handleInsertTotal = (key: string) => {
    const updatedValues: { [key: string]: string | number } = {}

    for (const k in completeOrderValues) {
      if (k !== key) {
        updatedValues[k] = "0"
      }
    }

    updatedValues[key] = String(data.total_with_discount).slice(0, -3)

    setCompleteOrderValues(updatedValues)
  }

  useEffect(() => {
    setCalculatedValue(calculateTotal())
  }, [calculateTotal, completeOrderValues])


  const completeOrder = async () => {
    try {
      const payments = Object.entries(completeOrderValues).map(([id, amount]) => ({
        id: Number(id),
        amount: amount !== "" ? String(amount).replace(/\s/g, "") : "0"
      }))

      const body = { payments }

      await completeOrderPost({ url: `api/orders/${id}/complete-order/`, body: body, invalidatesTags: ["Orders", "Cashiers"] })
    } catch (error) {
      console.error("Ошибка при отправке данных:", error)
    }
  }

  const handleSubmit = async (event: any) => {
    event.preventDefault()
    await completeOrder()
  }

  const handleScannerAddProduct = async () => {
    try {
      await scannerAddProduct({ url: `api/orders/${id}/order-items/`, body: {
        "code": productsKeyList.join(""),
        "count": 1
      }, invalidatesTags: ["Orders", "Products"] })
    } catch (e) {
      console.log("Error:", e)
    }
  }

  const handleScannerAddBouquet = async () => {
    try {
      await scannerAddBouquet({ url: `api/orders/${id}/factory-product-order_items/`, body: {
        "code": bouquetsKeyList.join(""),
        "count": 1
      }, invalidatesTags: ["Orders", "Products", "Factories"] })
    } catch (e) {
      console.log("Error:", e)
    }
  }

  useEffect(() => {
    if (productsKeyList.length !== 0 && data.status === 'CREATED') {
      handleScannerAddProduct()
    }
  }, [productsKeyList])

  useEffect(() => {
    if (bouquetsKeyList.length !== 0 && data.status === 'CREATED') {
      handleScannerAddBouquet()
    }
  }, [bouquetsKeyList])

  const handleAddProduct = async (selectedProduct: any) => {
    try {
      await addProduct({ url: `api/orders/${id}/order-items/`, body: {
        "product": selectedProduct.id,
        "count": 1
      }, invalidatesTags: ["Orders", "Products"] })
    } catch (error) {
      console.error("Error updating item quantity:", error)
    }
  }

  const handleAddBouquet = async (selectedBouquet: any) => {
    try {
      await addBouquet({ url: `api/orders/${id}/factory-product-order_items/`, body: {
        "product_factory": selectedBouquet.id
      }, invalidatesTags: ["Orders", "Products", "Factories"] })
    } catch (e) {
      console.log("Error adding item:", e)
    }
  }

  const cancelOrder = async () => {
    try {
      await cancelOrderPost({ url: `api/orders/${id}/cancel-order/`, body: {}, invalidatesTags: ["Orders"] })
    } catch (e) {
      console.log("Response error: ", e)
    }
  }

  const restoreOrder = async () => {
    try {
      await restoreOrderPost({ url: `api/orders/${id}/restore-order/`, body: {}, invalidatesTags: ["Orders"] })
    } catch (e) {
      console.log("Response error: ", e)
    }
  }


  const isCompleteDisabled = data && data.order_items && Array.isArray(data.order_items) && data.order_items.length !== 0 || data && data.order_item_factory_products && Array.isArray(data.order_item_factory_products) && data.order_item_factory_products.length !== 0

  return (
    <>
      <DashboardLayout>
        {!isLoading && !paymentMethodsLoading && data ? (
          <>
            <div className="w-full flex flex-col xl:flex-row gap-16 xl:gap-6">
              <section className="xl:w-2/5 w-full">
                <div className="flex flex-col gap-6">
                  <div className="flex flex-col gap-4">
                    <Button variant="outline" className="w-44" onClick={() => navigate(-1)}>
                      <ChevronLeft className="mr-2 w-4 h-4"/> Вернуться назад
                    </Button>

                    <SearchItem
                      placeholder="Поиск товаров"
                      value={searchValue}
                      onChange={handleSearch}
                      hasntBtn
                    />

                    <div className="w-full pb-2 max-w-full min-w-[200px] sm:min-w-[500px] xl:max-w-[800px] flex items-center gap-1 overflow-x-auto">
                      {!categoriesLoading && !factoryCategoriesLoading ? (
                        <>
                          <Button
                            onClick={() => {
                              setSelectedCategory("")
                              setSelectedFactoryCategory("")
                            }}
                            className={(selectedCategory === "" && selectedFactoryCategory === "") ? "bg-neutral-600 dark:bg-neutral-300" : ""}
                          >
                            Все товары
                          </Button>

                          <div className="flex items-center gap-1">
                            {factoryCategoriesData && Array.isArray(factoryCategoriesData) && factoryCategoriesData.map(item => (
                              <Button
                                key={item.id}
                                onClick={() => {
                                  setSelectedCategory("")
                                  setSelectedFactoryCategory(String(item.id))
                                }}
                                className={selectedFactoryCategory === String(item.id) ? "bg-neutral-600 dark:bg-neutral-300" : ""}
                              >{item.name}</Button>)
                            )}

                            {categoriesData && Array.isArray(categoriesData) && categoriesData.map(item => (
                              <Button
                                key={item.id}
                                onClick={() => {
                                  setSelectedFactoryCategory("")
                                  setSelectedCategory(String(item.id))
                                }}
                                className={selectedCategory === String(item.id) ? "bg-neutral-600 dark:bg-neutral-300" : ""}
                              >{item.name}</Button>)
                            )}
                          </div>
                        </>
                      ) : (
                        <CategoriesSkeleton/>
                      )}
                    </div>

                    {dataStatusError && <ErrorItem title="Ошибка" desc="Вы не можете добавить товар если заказ завершен"/>}
                  </div>

                  <AddForm form={form} onSubmit={onSubmit} success={success} successDesc="Товар успешно добавлен">
                    <AddForm form={factoryForm} onSubmit={factorySubmit} success={factorySuccess} successDesc="Букет успешно добавлен">
                      <ScrollArea className="h-[620px]">
                        <div className={`w-full pr-4 pb-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 ${userType !== "ADMIN" && userType !== "CASHIER" && userType !== "MANAGER" && userType !== "SALESMAN" && userType !== "NO_BONUS_SALESMAN" && userType !== "FLORIST_PERCENT" ? "opacity-60 pointer-events-none" : ""}`}>
                          {!productsLoading && filteredProducts && Array.isArray(filteredProducts) ? filteredProducts.map(item => (
                            <>
                              {selectedFactoryCategory === "" ? (
                                <ProductCard
                                  key={item.id}
                                  image={item.image}
                                  title={item.name}
                                  price={item.price}
                                  isSending={addProductPending || scannerAddProductPending || productsFetching}
                                  inStock={formatter.format(item.in_stock)}
                                  onClick={data.status === "CREATED" && Number(item.in_stock) > 0 && !addProductPending && !scannerAddProductPending ? () => handleAddProduct(item) : () => {
                                    data.status !== "CREATED" ? setDataStatusError(true) : null
                                    data.status !== "CREATED" ? setTimeout(() => setDataStatusError(false), 2500) : null
                                  }}
                                />
                              ) : null}
                            </>
                          )) : (
                            <ProductsSkeleton/>
                          )}
                          {!factoryProductsLoading && filteredFactoryProducts && Array.isArray(filteredFactoryProducts) ? filteredFactoryProducts.map(item => (
                            <>
                              {selectedCategory === "" ? (
                                <ProductCard
                                  key={item.id}
                                  image={item.image}
                                  title={item.name}
                                  price={item.price}
                                  isSending={addBouquetPending || scannerAddBouquetPending || factoryProductsFetching}
                                  florist={item.florist?.first_name || item.florist?.username}
                                  onClick={data.status === "CREATED" && !addBouquetPending && !scannerAddBouquetPending ? () => handleAddBouquet(item) : () => {
                                    data.status !== "CREATED" ? setDataStatusError(true) : null
                                    data.status !== "CREATED" ? setTimeout(() => setDataStatusError(false), 2500) : null
                                  }}
                                />
                              ) : null}
                            </>
                          )) : (
                            <ProductsSkeleton/>
                          )}
                        </div>

                        {filteredProducts && filteredProducts.length === 0 && <p className="text-xl font-bold">Товары не найдены или их не осталось!</p>}
                        {filteredFactoryProducts && filteredFactoryProducts.length === 0 && <p className="text-xl font-bold">Букеты не найдены или их не осталось!</p>}
                      </ScrollArea>
                    </AddForm>
                  </AddForm>
                </div>
              </section>

              <section className="w-full flex flex-col justify-between gap-4">
                <div className="flex flex-col gap-5">
                  {data.status === "CREATED" ? (
                    <AddForm form={orderForm} onSubmit={orderSubmit} success={orderSuccess} successDesc="Успешно изменено" notMT>
                      <div className="w-full flex flex-col gap-3">
                        <div className='w-full mb-3 flex flex-col sm:flex-row justify-between gap-4'>
                          <div className="flex flex-col">
                            <p className="font-semibold">Создал: <span
                              className="font-bold">{data.created_user?.first_name || data.created_user?.username}</span>
                            </p>

                            <p className="font-semibold">Дата создания: <span
                              className="font-bold">{formatDate(data.created_at)}</span>
                            </p>
                          </div>

                          <div className="flex flex-col">
                            <p className="font-semibold">Общая сумма покупок: <span
                              className="font-bold">{formatter.format(data.client?.total_orders_sum)} сум</span>
                            </p>

                            <p className="font-semibold">Чистая прибыль: <span
                              className="font-bold">{formatter.format(data.client?.total_orders_profit_sum)} сум</span>
                            </p>

                            <p className="font-semibold">Долг клиента: <span
                              className="font-bold">{formatter.format(data.client?.debt)} сум</span>
                            </p>

                            <p className="font-semibold">Процент скидки: <span
                              className="font-bold">{formatter.format(data.client?.discount_percent)}%</span>
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <ReactSelectFormField
                            idData={clientsData} isLoading={clientsLoading}
                            control={orderForm.control}
                            name="client"
                            placeholder={data.client?.full_name}
                          />
                          <ReactSelectFormField
                            idData={departmentsData}
                            isLoading={departmentsLoading}
                            control={orderForm.control}
                            name="department"
                            placeholder={data.department?.name}
                          />
                          <ReactSelectFormField
                            idData={salesmanData}
                            isLoading={salesmanLoading}
                            control={orderForm.control}
                            name="salesman"
                            placeholder={data.salesman?.first_name || data.salesman?.username || "Продавец не выбран"}
                          />
                          <InputFormField
                            control={orderForm.control}
                            type="text"
                            name="comment"
                            placeholder="Комментарий"
                            _value={editValues.comment}
                            _onChange={(e: any) => editValuesChange("comment", e.target.value)}
                          />

                          <Button type="submit" disabled={orderPending}>Изменить</Button>
                        </div>
                      </div>
                    </AddForm>
                  ) : (
                    <div className="flex flex-col gap-1">
                      <div className="w-full mb-3 flex flex-col sm:flex-row justify-between gap-4">
                        <div className="flex flex-col">
                          <p className="font-semibold">Клиент: <span
                            className="font-bold">{data.client?.full_name}</span></p>
                          <p className="font-semibold">Продавец: <span
                            className="font-bold">{data.salesman?.first_name || data.salesman?.username || "-"}</span></p>
                          <p className="font-semibold">Создал: <span
                            className="font-bold">{data.created_user?.first_name || data.created_user?.username}</span></p>
                          <p className="font-semibold">Дата создания: <span
                            className="font-bold">{formatDate(data.created_at)}</span>
                          </p>
                        </div>

                        <div className="flex flex-col">
                          <p className="font-semibold">Общая сумма покупок: <span
                            className="font-bold">{formatter.format(data.client?.total_orders_sum)} сум</span>
                          </p>

                          <p className="font-semibold">Чистая прибыль: <span
                            className="font-bold">{formatter.format(data.client?.total_orders_profit_sum)} сум</span>
                          </p>

                          <p className="font-semibold">Долг клиента: <span
                            className="font-bold">{formatter.format(data.client?.debt)} сум</span>
                          </p>

                          <p className="font-semibold">Процент скидки: <span
                            className="font-bold">{formatter.format(data.client?.discount_percent)}%</span>
                          </p>
                        </div>
                      </div>

                      <AddForm form={orderForm} onSubmit={orderSubmit} success={orderSuccess} successDesc="Успешно изменено" notMT>
                        <div className="flex items-center gap-2">
                          <ReactSelectFormField
                            idData={departmentsData}
                            isLoading={departmentsLoading}
                            control={orderForm.control}
                            name="department"
                            placeholder={data.department?.name}
                          />
                          <InputFormField
                            control={orderForm.control}
                            type="text"
                            name="comment"
                            placeholder="Комментарий"
                            _value={editValues.comment}
                            _onChange={(e: any) => editValuesChange("comment", e.target.value)}
                          />
                          { userType === 'ADMIN' && (
                            <DatePicker
                              isForm
                              name="created_at"
                              text='Дата cоздания'
                              control={orderForm.control}
                            />
                          ) }

                          <Button type="submit" disabled={orderPending}>Изменить</Button>
                        </div>
                      </AddForm>
                    </div>
                  )}

                  <ScrollArea className="h-[590px]">
                    {
                      (data.order_items && data.order_item_factory_products && Array.isArray(data.order_items) && Array.isArray(data.order_item_factory_products)) &&
                      (data.order_items.length === 0 && data.order_item_factory_products.length === 0) &&
                      <p className="text-xl font-bold">Добавьте товар или букет</p>
                    }

                    {!isFetching && !isLoading && !addProductPending && !scannerAddProductPending ? (
                      <>
                        {data.order_items && Array.isArray(data.order_items) && data.order_items.length !== 0 ? (
                          <Table className="w-full">
                            <TableHeader>
                              <TableRow>
                                <TableHead>№</TableHead>
                                <TableHead>Товар</TableHead>
                                <TableHead>Цена</TableHead>
                                <TableHead>Количество</TableHead>
                                {data.status === "COMPLETED" || data.status === "CANCELLED" ? (
                                  <TableHead>Количество возврата</TableHead>
                                ) : null}
                                <TableHead>Итого</TableHead>
                              </TableRow>
                            </TableHeader>

                            <TableBody>
                              {data && data.order_items && Array.isArray(data.order_items) && data.order_items.map((item: any, index: any) => (
                                <TableRow key={item.id}>
                                  <TableCell>{++index}</TableCell>
                                  <TableCell>{item.product?.name}</TableCell>
                                  <TableCell>
                                    {formatter.format(item.price)} сум
                                    {data.status === "CREATED" ? (
                                      <EditDialog
                                        dialogTitle="Изменить цену товара"
                                        form={priceForm}
                                        submit={priceSubmit}
                                        success={priceSuccess}
                                        successDesc="Цена товара успешно изменена"
                                        btnClassname="ml-6"
                                        onClick={() => setOrderID(item.id)}
                                        pending={pricePending}
                                      >
                                        <NumberFormField
                                          _value={inputValues.price}
                                          _onChange={(e: any) => handleInputValuesChange("price", e)}
                                          control={priceForm.control}
                                          name="price"
                                          placeholder="Введите новую цену товара"
                                        />
                                      </EditDialog>
                                    ) : null}
                                  </TableCell>
                                  <TableCell>
                                    {formatter.format(item.count)}
                                    {data.status === "CREATED" ? (
                                      <EditDialog
                                        dialogTitle="Изменить количество товара"
                                        form={countForm}
                                        submit={countSubmit}
                                        success={countSuccess}
                                        successDesc="Количество товара успешно изменено"
                                        btnClassname="ml-6"
                                        onClick={() => setOrderID(item.id)}
                                        pending={countPending}
                                      >
                                        <NumberFormField
                                          _value={inputValues.count}
                                          _onChange={(e: any) => handleInputValuesChange("count", e)}
                                          control={countForm.control}
                                          name="count"
                                          placeholder="Введите новое количество товара"
                                        />

                                        {errorText && <p className="text-sm text-red-500">Недостаточно товаров!</p>}
                                      </EditDialog>
                                    ) : null}
                                  </TableCell>
                                  {data.status === "COMPLETED" || data.status === "CANCELLED" ? (
                                    <TableCell>{formatter.format(item.returned_count)}</TableCell>
                                  ) : null}
                                  <TableCell>{formatter.format(item.total)} сум</TableCell>
                                  {data.status === "CREATED" ? (
                                    <TableCell className="flex items-center gap-4">
                                      <Button variant="destructive" size="icon" disabled={isDeleting} onClick={
                                        () => deleteItem(
                                          `api/orders/${id}/order-items`,
                                          item.id,
                                          ["Orders", "Products"]
                                        )
                                      } title="Удалить">
                                        <Trash2 className="w-4 h-4"/>
                                      </Button>
                                    </TableCell>
                                  ) : null}

                                  <TableCell className="flex items-center gap-2">
                                    {data.status === "COMPLETED" && userType !== "CASHIER" && (
                                      <ReturnDialog
                                        dialogTitle="Сделать возврат"
                                        dialogDesc="Заполните нужные поля, чтобы сделать возврат"
                                        schemaObject={{count: z.string({required_error: "Введите количество товара"})}}
                                        url={`api/orders/${id}/order-items/${item.id}/returns/`}
                                        invalidatesTags={["OrderReturns"]}
                                      />
                                    )}

                                    {data.status !== "CREATED" && (
                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <Button size="icon" onClick={() => setOrderItemID(item.id)}>
                                            <Eye className="w-4 h-4"/>
                                          </Button>
                                        </DialogTrigger>

                                        <DialogContent className="w-full">
                                          <DialogHeader>
                                            <DialogTitle>Возвращенные товары</DialogTitle>
                                          </DialogHeader>

                                          {error && (
                                            <ErrorItem title="Ошибка" desc={errorText}/>
                                          )}

                                          <Table className="w-full">
                                            <TableHeader>
                                              <TableRow>
                                                <TableHead>№</TableHead>
                                                <TableHead>Название продукта</TableHead>
                                                <TableHead>Количество</TableHead>
                                                <TableHead>Итого</TableHead>
                                                <TableHead>Дата возврата</TableHead>
                                              </TableRow>
                                            </TableHeader>

                                            <TableBody>
                                              {orderReturnsData && Array.isArray(orderReturnsData) && orderReturnsData.map((item, index) => (
                                                <TableRow key={item.id}>
                                                  <TableCell>{++index}</TableCell>
                                                  <TableCell>{item.product_name}</TableCell>
                                                  <TableCell>{formatter.format(item.count)}</TableCell>
                                                  <TableCell>{formatter.format(item.total)} сум</TableCell>
                                                  <TableCell>{formatDate(item.created_at)}</TableCell>
                                                  {data.status === "COMPLETED" && (
                                                    <TableCell>
                                                      <Button variant="destructive" size="icon" disabled={isDeleting}
                                                              onClick={() => deleteItem(
                                                                `api/orders/${id}/order-items/${orderItemID}/returns`,
                                                                item.id,
                                                                ["Orders", "Products"]
                                                              )}>
                                                        <Trash2 className="w-4 h-4"/>
                                                      </Button>
                                                    </TableCell>
                                                  )}
                                                </TableRow>
                                              ))}
                                            </TableBody>

                                            {orderReturnsData && Array.isArray(orderReturnsData) && orderReturnsData.length === 0 &&
                                              <p className="w-full mt-2 p-2 text-lg font-medium">Возвращённых товаров
                                                нет</p>}
                                          </Table>
                                        </DialogContent>
                                      </Dialog>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>

                            {data && data.order_items && Array.isArray(data.order_items) && data.order_items.length === 0 &&
                              <p className="mt-4 text-xl font-bold">Добавьте товар</p>}
                          </Table>
                        ) : null}
                      </>
                    ) : (
                      <SectionTableSkeleton/>
                    )}

                    {!isFetching && !isLoading && !addBouquetPending && !scannerAddBouquetPending ? (
                      <>
                        {data.order_item_factory_products && Array.isArray(data.order_item_factory_products) && data.order_item_factory_products.length !== 0 ? (
                          <Table className="w-full mt-16">
                            <TableHeader>
                              <TableRow>
                                <TableHead>№</TableHead>
                                <TableHead>Букет</TableHead>
                                <TableHead>Флорист</TableHead>
                                <TableHead>Цена</TableHead>
                                <TableHead>Итого</TableHead>
                              </TableRow>
                            </TableHeader>

                            <TableBody>
                              {data && data.order_item_factory_products && Array.isArray(data.order_item_factory_products) && data.order_item_factory_products.map((item: any, index: any) => (
                                <TableRow key={item.id}>
                                  <TableCell>{++index}</TableCell>
                                  <TableCell>{item.product_factory?.name}</TableCell>
                                  <TableCell>{item.product_factory?.florist?.first_name || item.product_factory?.florist?.username}</TableCell>
                                  <TableCell>
                                    {formatter.format(item.price)} сум
                                    {data.status === "CREATED" ? (
                                      <EditDialog
                                        dialogTitle="Изменить цену"
                                        form={factoryPriceForm}
                                        submit={factoryPriceSubmit}
                                        success={factoryPriceSuccess}
                                        successDesc="Цена успешно изменена"
                                        onClick={() => setFactoryOrderID(item.id)}
                                        pending={factoryPricePending}
                                        btnClassname="ml-6"
                                      >
                                        <NumberFormField
                                          control={factoryPriceForm.control}
                                          name="price"
                                          placeholder="Введите новую цену букета"
                                          _value={inputValues.factoryPrice}
                                          _onChange={(e: any) => handleInputValuesChange("factoryPrice", e)}
                                        />
                                      </EditDialog>
                                    ) : null}
                                  </TableCell>
                                  <TableCell>{formatter.format(item.total)} сум</TableCell>
                                  {data.status === "CREATED" ? (
                                    <TableCell>
                                      <Button variant="destructive" size="icon" disabled={isDeleting}
                                              onClick={() => deleteItem(
                                                `api/orders/${id}/factory-product-order_items`,
                                                item.id,
                                                ["Orders", "Factories", "Products"]
                                              )}>
                                        <Trash2 className="w-4 h-4"/>
                                      </Button>
                                    </TableCell>
                                  ) : null}

                                  <TableCell className="flex items-center gap-2">
                                    {item.is_returned && <p className="font-medium">Возвращен</p>}

                                    {data.status === "COMPLETED" && !item.is_returned && userType !== "CASHIER" && (
                                      <ReturnDialog
                                        isButtons
                                        dialogTitle="Сделать возврат"
                                        dialogDesc="Вы действительно хотите сделать возврат?"
                                        url={`api/orders/${id}/factory-product-order_items/${item.id}/returns/`}
                                        invalidatesTags={["OrderReturns"]}
                                      />
                                    )}

                                    {data.status !== "CREATED" && (
                                      <Dialog>
                                        <DialogTrigger asChild>
                                          <Button size="icon" onClick={() => setFactoryOrderID(item.id)}>
                                            <Eye className="w-4 h-4"/>
                                          </Button>
                                        </DialogTrigger>

                                        <DialogContent className="w-full">
                                          <DialogHeader>
                                            <DialogTitle>Возвращенные букеты</DialogTitle>
                                          </DialogHeader>

                                          {error && (
                                            <ErrorItem title="Ошибка" desc={errorText}/>
                                          )}

                                          <Table className="w-full">
                                            <TableHeader>
                                              <TableRow>
                                                <TableHead>№</TableHead>
                                                <TableHead>Букет</TableHead>
                                                <TableHead>Итого</TableHead>
                                                <TableHead>Дата возврата</TableHead>
                                              </TableRow>
                                            </TableHeader>

                                            <TableBody>
                                              {factoryReturnsData && Array.isArray(factoryReturnsData) && factoryReturnsData.map((item, index) => (
                                                <TableRow key={item.id}>
                                                  <TableCell>{++index}</TableCell>
                                                  <TableCell>{item.product_name}</TableCell>
                                                  <TableCell>{formatter.format(item.total)} сум</TableCell>
                                                  <TableCell>{formatDate(item.created_at)}</TableCell>
                                                  {data.status === "COMPLETED" && (
                                                    <TableCell>
                                                      <Button variant="destructive" size="icon" disabled={isDeleting}
                                                              onClick={() => deleteItem(
                                                                `api/orders/${id}/factory-product-order_items/${factoryOrderID}/returns`,
                                                                undefined,
                                                                ["Orders", "Factories", "Products"]
                                                              )}>
                                                        <Trash2 className="w-4 h-4"/>
                                                      </Button>
                                                    </TableCell>
                                                  )}
                                                </TableRow>
                                              ))}
                                            </TableBody>

                                            {factoryReturnsData && Array.isArray(factoryReturnsData) && factoryReturnsData.length === 0 &&
                                              <p className="w-full mt-2 p-2 text-lg font-medium">Возвращённых букетов
                                                нет</p>}
                                          </Table>
                                        </DialogContent>
                                      </Dialog>
                                    )}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>

                            {data && data.order_item_factory_products && Array.isArray(data.order_item_factory_products) && data.order_item_factory_products.length === 0 &&
                              <p className="mt-4 text-xl font-bold">Добавьте букет</p>}
                          </Table>
                        ) : null}
                      </>
                    ) : (
                      <SectionTableSkeleton/>
                    )}
                  </ScrollArea>
                </div>

                { restoreError && (
                  <ErrorItem title='Ошибка' desc={JSON.stringify(restoreError.data)} />
                ) }

                <div className="w-full mt-4 pb-2 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-transparent">
                  <div className="flex flex-col sm:flex-row sm:gap-8">
                    <div>
                      <p>Общая сумма: <span className="font-semibold">{formatter.format(Number(data.total))} сум</span></p>
                      <p className="flex items-center gap-1">
                        Скидка: <span className="font-semibold">{formatter.format(data.discount)} сум</span>
                        {/* {data.status === 'CREATED' ? (
                          <EditDialog
                            dialogTitle="Добавить скидку"
                            form={totalForm.control}
                            submit={totalSubmit}
                            success={totalSuccess}
                            successDesc="Скидка успешно добавлена"
                            btnVariant="ghost"
                            pending={totalPending}
                          >
                            <NumberFormField
                              _value={inputValues.discount}
                              _onChange={(e: any) => handleInputValuesChange('discount', e)}
                              control={totalForm.control}
                              name="discount"
                              placeholder="Введите скидку"
                            />
                          </EditDialog>
                        ) : null} */}
                      </p>
                      {data.status !== "CREATED" && data.status !== "CANCELLED" && (
                        <p className="text-red-500">Долг: <span className="font-semibold">{formatter.format(data.debt)} сум</span></p>
                      )}
                    </div>

                    <div className="flex flex-col">
                      <p>К оплате: <span className="font-semibold">{formatter.format(data.total_with_discount)} сум</span></p>
                      <p>Оплачено: <span className="font-semibold">{formatter.format(data.amount_paid)} сум</span></p>
                      {data.status !== "CREATED" && (
                        <p>Сумма возврата: <span className="font-semibold">{formatter.format(data.amount_returned)} сум</span></p>
                      )}
                    </div>
                  </div>

                  {userType !== "FLORIST" && (
                    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-1 sm:gap-2">
                      {data.status !== "CREATED" ? (
                        <Dialog>
                          <DialogTrigger>
                            <Button size="icon" variant="outline">
                              <ReceiptText className="w-4 h-4"/>
                            </Button>
                          </DialogTrigger>

                          <DialogContent className="max-w-[1000px]">
                            <DialogHeader>
                              <DialogTitle>Совершенные платежи</DialogTitle>
                            </DialogHeader>

                            <Table>
                              <TableHeader>
                                <TableRow>
                                  <TableHead>№</TableHead>
                                  <TableHead>Номер платежа</TableHead>
                                  <TableHead>Комментарий</TableHead>
                                  <TableHead>Метод оплаты</TableHead>
                                  <TableHead>Доход / расход</TableHead>
                                  <TableHead>Сумма</TableHead>
                                  <TableHead>Дата создания</TableHead>
                                </TableRow>
                              </TableHeader>

                              <TableBody>
                                {data.payments && Array.isArray(data.payments) && data.payments.length !== 0 ? data.payments.map((item: any, index: any) => (
                                  <TableRow key={item.id}>
                                    <TableCell>{index + 1}</TableCell>
                                    <TableCell>Платеж #{item.id}</TableCell>
                                    <TableCell>{item.comment || "-"}</TableCell>
                                    <TableCell>{translatedData(item.payment_method?.name)}</TableCell>
                                    <TableCell>{translatedData(item.payment_type)}</TableCell>
                                    <TableCell>{formatter.format(item.amount)} сум</TableCell>
                                    <TableCell>{formatDate(item.created_at)}</TableCell>
                                  </TableRow>
                                )) : (
                                  <p className="mt-4 text-base font-medium">Платежи не найдены!</p>
                                )}
                              </TableBody>
                            </Table>
                          </DialogContent>
                        </Dialog>
                      ) : null}

                      {data.status !== "CREATED" && (userType === "ADMIN" || userId === '2') && (
                        <PaymentDialog
                          btnText="Оплата"
                          dialogTitle="Оплата"
                          dialogDescription="Заполните нужные поля чтобы сделать оплату"
                          page="orders"
                          item={data.id}
                          text
                          invalidatesTags={["Cashiers", "Orders"]}
                        />
                      )}

                      {data.status === "CREATED" && isCompleteDisabled ? (
                        <Dialog>
                          <DialogTrigger>
                            <Button>Завершить</Button>
                          </DialogTrigger>

                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Завершить продажу</DialogTitle>
                              <DialogDescription>Заполните нужные поля чтобы завершить продажу</DialogDescription>
                            </DialogHeader>

                            <AddForm form={completeOrderForm} onSubmit={completeOrderSubmit} success={completeOrderSuccess} successDesc="Заказ успешно завершен">
                              <h3 className="text-xl font-bold">Сумма: {formatter.format(Number(data.total_with_discount))} сум</h3>

                              {amountError && (
                                <ErrorItem title="Ошибка" desc="Вы не можете ввести число больше чем сумма"/>
                              )}

                              <div className="w-full max-h-[400px] p-2 flex flex-col gap-4 overflow-y-auto">
                                {paymentMethods && Array.isArray(paymentMethods) && paymentMethods.filter((item:any) => item?.is_active ? item : null).map((item, index) => (
                                  <OrderCompleteItem
                                    key={index}
                                    form={completeOrderForm}
                                    name="amount"
                                    label={item.name}
                                    value={completeOrderValues[item.id] || ""}
                                    onChange={(value: string) => handleInputChange(item.id, value)}
                                    onClick={() => handleInsertTotal(item.id)}
                                  />
                                ))}
                              </div>

                              <h3 className="mt-4 text-xl font-bold">Долг: {formatter.format(calculatedValue !== "" ? Number(calculatedValue) : data.debt)} сум</h3>

                              {!amountError && <Button type="submit" onClick={handleSubmit} disabled={completePending}>Завершить</Button>}
                            </AddForm>
                          </DialogContent>
                        </Dialog>
                      ) : null }

                      {/*{!completeOrderSuccess && data.status === "CREATED" && isCompleteDisabled ? (*/}
                      {/*  <Dialog>*/}
                      {/*    <DialogTrigger>*/}
                      {/*      <Button>Завершить</Button>*/}
                      {/*    </DialogTrigger>*/}

                      {/*    { !hasShiftIsLoading && hasShiftData.has_shift ? (*/}
                      {/*      <DialogContent>*/}
                      {/*        <DialogHeader>*/}
                      {/*          <DialogTitle>Завершить продажу</DialogTitle>*/}
                      {/*          <DialogDescription>Заполните нужные поля чтобы завершить продажу</DialogDescription>*/}
                      {/*        </DialogHeader>*/}

                      {/*        <AddForm form={completeOrderForm} onSubmit={completeOrderSubmit} success={completeOrderSuccess} successDesc="Заказ успешно завершен">*/}
                      {/*          <h3 className="text-xl font-bold">Сумма: {formatter.format(Number(data.total_with_discount))} сум</h3>*/}

                      {/*          {amountError && (*/}
                      {/*            <ErrorItem title="Ошибка" desc="Вы не можете ввести число больше чем сумма"/>*/}
                      {/*          )}*/}

                      {/*          <div className="w-full max-h-[400px] p-2 flex flex-col gap-4 overflow-y-auto">*/}
                      {/*            {paymentMethods && Array.isArray(paymentMethods) && paymentMethods.map((item, index) => (*/}
                      {/*              <OrderCompleteItem*/}
                      {/*                key={index}*/}
                      {/*                form={completeOrderForm}*/}
                      {/*                name="amount"*/}
                      {/*                label={item.name}*/}
                      {/*                value={completeOrderValues[item.id] || ""}*/}
                      {/*                onChange={(value: string) => handleInputChange(item.id, value)}*/}
                      {/*                onClick={() => handleInsertTotal(item.id)}*/}
                      {/*              />*/}
                      {/*            ))}*/}
                      {/*          </div>*/}

                      {/*          <h3 className="mt-4 text-xl font-bold">Долг: {formatter.format(calculatedValue !== "" ? Number(calculatedValue) : data.debt)} сум</h3>*/}

                      {/*          {!amountError && <Button type="submit" onClick={handleSubmit} disabled={completePending}>Завершить</Button>}*/}
                      {/*        </AddForm>*/}
                      {/*      </DialogContent>*/}
                      {/*    ) : (*/}
                      {/*      <DialogContent>*/}
                      {/*        <DialogHeader>*/}
                      {/*          <DialogTitle>Откройте смену чтобы добавить продажу</DialogTitle>*/}
                      {/*        </DialogHeader>*/}

                      {/*        <Button disabled={openPending} onClick={() => createShift({})}>*/}
                      {/*          <CalendarClock className="w-4 h-4 mr-2"/> Открыть смену*/}
                      {/*        </Button>*/}
                      {/*      </DialogContent>*/}
                      {/*    ) }*/}
                      {/*  </Dialog>*/}
                      {/*) : null}*/}

                      {data.status === "COMPLETED" ? (
                        <a href={`${getUrl()}/core/print-receipt/order/${id}/`} target="_blank">
                          <Button>
                            <ReceiptText className="w-4 h-4 mr-2"/> Распечатать чек
                          </Button>
                        </a>
                      ) : null}

                      {userType !== 'CASHIER' && data.status === "COMPLETED" ? (
                        <Dialog>
                          <DialogTrigger>
                            <Button variant="destructive" type="submit">
                              Отменить
                            </Button>
                          </DialogTrigger>

                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Вы действительно хотите отменить продажу?</DialogTitle>
                            </DialogHeader>

                            <div className="flex items-center gap-2">
                              <Button variant="destructive" disabled={cancelOrderPostPending} onClick={() => cancelOrder()}>Да</Button>
                              <DialogTrigger>
                                <Button>Нет</Button>
                              </DialogTrigger>
                            </div>
                          </DialogContent>
                        </Dialog>
                      ) : null}

                      {/*{data.status === "COMPLETED" ? (*/}
                      {/*  <Dialog>*/}
                      {/*    <DialogTrigger>*/}
                      {/*      <Button variant="destructive" type="submit">*/}
                      {/*        Отменить*/}
                      {/*      </Button>*/}
                      {/*    </DialogTrigger>*/}

                      {/*    { !hasShiftIsLoading && hasShiftData.has_shift ? (*/}
                      {/*      <DialogContent>*/}
                      {/*        <DialogHeader>*/}
                      {/*          <DialogTitle>Вы действительно хотите отменить продажу?</DialogTitle>*/}
                      {/*        </DialogHeader>*/}

                      {/*        <div className="flex items-center gap-2">*/}
                      {/*          <Button variant="destructive" onClick={() => cancelOrder()}>Да</Button>*/}
                      {/*          <DialogTrigger>*/}
                      {/*            <Button>Нет</Button>*/}
                      {/*          </DialogTrigger>*/}
                      {/*        </div>*/}
                      {/*      </DialogContent>*/}
                      {/*    ) : (*/}
                      {/*      <DialogContent>*/}
                      {/*        <DialogHeader>*/}
                      {/*          <DialogTitle>Откройте смену чтобы добавить продажу</DialogTitle>*/}
                      {/*        </DialogHeader>*/}

                      {/*        <Button disabled={openPending} onClick={() => createShift({})}>*/}
                      {/*          <CalendarClock className="w-4 h-4 mr-2"/> Открыть смену*/}
                      {/*        </Button>*/}
                      {/*      </DialogContent>*/}
                      {/*    ) }*/}
                      {/*  </Dialog>*/}
                      {/*) : null}*/}

                      {userType !== 'CASHIER' && data.status === 'CANCELLED' ? (
                        <Button variant='destructive' onClick={() => restoreOrder()} disabled={restorePending}>
                          Восстановить
                        </Button>
                      ) : null}
                    </div>
                  )}
                </div>
              </section>
            </div>
          </>
        ) : (
          <EditSectionSkeleton/>
        )}
      </DashboardLayout>
    </>
  )
}

export default OrdersEditPage