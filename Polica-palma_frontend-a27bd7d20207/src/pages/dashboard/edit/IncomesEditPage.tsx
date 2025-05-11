/* eslint-disable @typescript-eslint/no-explicit-any */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-nocheck
import {useParams} from 'react-router-dom'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import InputFormField from '@/components/others/InputFormField.tsx'
import {Button} from '@/components/ui/button.tsx'
import {AlertCircle, Check, ScanLine, Trash2} from 'lucide-react'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {useEffect, useState} from 'react'
import {Alert, AlertDescription, AlertTitle} from '@/components/ui/alert.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import translateFunc from '@/data/translatedData.ts'
import useValues from '@/hooks/useValues.ts'
import IncomesEditFormFields from '@/components/forms/IncomesEditFormFields.tsx'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import ErrorItem from '@/components/items/ErrorItem.tsx'
import getUrl from '@/config.ts'
import TableItem from '@/components/tables/TableItem.tsx'
import {incomesEditTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import translatedData from '@/data/translatedData.ts'
import useDeleteItem from '@/hooks/useDeleteItem.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface InputValues {
  countValue: null | string
  priceValue: null | string
  salePriceValue: null | string
}

const IncomesEditPage = () => {
  const { id } = useParams()
  const { formatter } = useNumberFormatter()
  const { deleteItem, isDeleting } = useDeleteItem()
  const { data, isLoading } = api.useGetIncomesQuery({ id: id })
  const { data: providersData, isLoading: providersLoading } = api.useGetProvidersQuery('')
  const { data: incomeItemsData, isLoading: incomeItemsLoading } = api.useGetIncomeItemsQuery(id)
  const [inputData, setInputData] = useState<any[]>([])
  const [isInputChanged, setIsInputChanged] = useState<boolean>(false)
  const [updateStatus, { isLoading: statusLoading, error: statusError, isSuccess: statusSuccess }] = api.useUpdateStatusMutation()

  useEffect(() => {
    const _incomeData = incomeItemsData && Array.isArray(incomeItemsData) && incomeItemsData.map(item => ({
      countValue: item.count.toString().slice(0, -3),
      priceValue: item.price.toString().slice(0, -3),
      salePriceValue: item.sale_price.toString().slice(0, -3)
    }))
    setInputData(
      _incomeData
    )
  }, [incomeItemsData])

  const { success: productEditSuccess, form: productEditForm, onSubmit: productEditSubmit, pending: productsEditPending, error, errorText } = useAxiosPut(
    {
      income_items: z.array(
        z.object({
          id: z.number(),
          count: z.string().optional(),
          price: z.string().optional(),
          sale_price: z.string().optional()
        }).optional()
      ).optional()
    },
    {
      income_items: inputData && Array.isArray(inputData) && inputData.map((item, index) => {
        const itemId = incomeItemsData[index]?.id
        const tRow = document.querySelector(`#income-item-${itemId}`)
        const count = item?.countValue !== undefined ? item.countValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="count"]')?.value.replace(/\s/g, '')
        const price = item?.priceValue !== undefined ? item.priceValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="price"]')?.value.replace(/\s/g, '')
        const sale_price = item?.salePriceValue !== undefined ? item.salePriceValue?.replace(/\s/g, '') :  tRow?.querySelector('input[name="sale_price"]')?.value.replace(/\s/g, '')

        return {
          "id": itemId,
          "count": count,
          "price": price,
          "sale_price": sale_price
        }
      })
    },
    `api/incomes/${id}/income-items`,
    'multiple_update',
    ["Incomes", "Products"]
  )

  useEffect(() => {
    if (productEditSuccess) {
      setIsInputChanged(false)
    }
  }, [productEditSuccess])

  const handleInputValuesChange = (index: number, key: keyof InputValues, value: string) => {
    const updatedInputValues = [...inputData]

    updatedInputValues[index] = {
      ...updatedInputValues[index],
      [key]: value
    }

    setIsInputChanged(true)
    setInputData(updatedInputValues)
  }

  const { success, form, onSubmit } = useAxiosPut(
    {
      comment: z.string().optional(),
      provider: z.string().optional(),
    },
    {},
    'api/incomes',
    id,
    ["Incomes"]
  )

  const { success: productAddSuccess, form: productAddForm, onSubmit: productAddSubmit, error: productsAddError, errorText: productsAddErrorText } = useAxiosPost(
    {
      product: z.string({ required_error: "Пожалуйста, выберите продукт" }),
    },
    {},
    `api/incomes/${id}/income-items/`,
    ["Incomes"]
  )

  const { inputValues, handleInputChange } = useValues(
    {
      comment: ''
    },
    {
      comment: data && data?.comment || ''
    },
    isLoading,
    data
  )

  const updStatus = async (status: string) => {
    try {
      await updateStatus({ url: `api/incomes/${id}/update-status/`, body: { "status": status }, invalidatesTags: ["Incomes", "Warehouse"] }).unwrap()
    } catch (e: any) {
      console.log('Status Error: ', e)
    }
  }

  return (
    <>
      <DashboardLayout>
        { !isLoading && data ? (
          <>
            <div className='w-full flex flex-col xl:flex-row gap-6'>
              <section className='w-full xl:w-1/2 flex flex-col gap-6'>
                <EditSection form={form} onSubmit={onSubmit} success={success}>
                  <InputFormField
                    control={form.control}
                    type='text'
                    name='comment'
                    label='Новый комментарий'
                    _value={inputValues.comment}
                    _onChange={(e: any) => handleInputChange('comment', e.target.value)}
                  />
                  { data.status !== 'CREATED' && (
                    <p className="text-lg font-semibold">Поставщик: <span className='font-bold'>{data.provider?.full_name}</span></p>
                  )}
                  {data.status !== 'COMPLETED' && data.status !== 'CANCELLED' && data.status !== 'ACCEPTED' && (
                    <ReactSelectFormField idData={providersData} isLoading={providersLoading} control={form.control} name='provider' label='Выберите поставщика' placeholder={data.provider?.full_name} />
                  ) }
                </EditSection>

                { incomeItemsData && Array.isArray(incomeItemsData) && incomeItemsData.length !== 0 ? (
                  <div className="w-full mt-8 flex flex-col gap-4">
                    { statusError && (
                      <ErrorItem title='Ошибка' desc={statusError} />
                    ) }

                    { isInputChanged && (
                      <Alert>
                        <AlertCircle className='w-4 h-4' />
                        <AlertTitle>Сохраните данные</AlertTitle>
                        <AlertDescription>Введите необходимые данные и сохраните их, чтобы принять закуп</AlertDescription>
                      </Alert>
                    ) }

                    <h3 className="text-2xl font-bold">Действия</h3>
                    <p className="text-lg font-semibold">
                      Статус: <span
                      className="font-bold text-neutral-700 dark:text-neutral-400">{translateFunc(data.status)}</span>
                    </p>

                    <div className="pb-4 flex flex-col gap-1">
                      {statusSuccess && (
                        <Alert>
                          <Check className="w-4 h-4"/>
                          <AlertTitle>Успешно</AlertTitle>
                          <AlertDescription>Статус успешно изменен</AlertDescription>
                        </Alert>
                      )}

                      {data.status === 'CREATED' && (
                        <Button disabled={isInputChanged} type="submit" onClick={() => {
                          const _temp = inputData.map((item, index) => {
                            const itemId = incomeItemsData[index]?.id
                            const tRow = document.querySelector(`#income-item-${itemId}`)
                            const count = item?.countValue !== undefined ? item.countValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="count"]')?.value.replace(/\s/g, '')
                            const price = item?.priceValue !== undefined ? item.priceValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="price"]')?.value.replace(/\s/g, '')
                            const sale_price = item?.salePriceValue !== undefined ? item.salePriceValue?.replace(/\s/g, '') :  tRow?.querySelector('input[name="sale_price"]')?.value.replace(/\s/g, '')
                            if (+count === 0 || +price === 0 || +sale_price === 0) return true;
                            return false
                          })

                          if (_temp.some((e) => e)) {
                            if (confirm('У вас есть поля с 0 или пустые поля, вы уверены что хотите принять?')) updStatus('ACCEPTED')
                            return
                          }

                          updStatus('ACCEPTED')
                        }}>
                          Принять
                        </Button>
                      )}

                      {data.status === 'ACCEPTED' && (
                        <Button disabled={statusLoading} type="submit" onClick={() => updStatus('COMPLETED')}>
                          Завершить
                        </Button>
                      )}

                      {data.status === 'CANCELLED' && (
                        <Button disabled={statusLoading} type="submit" onClick={() => updStatus('CREATED')}>
                          Восстановить
                        </Button>
                      )}

                      {data.status !== 'CANCELLED' && (
                        <Button disabled={statusLoading} variant="destructive" type="submit" onClick={() => updStatus('CANCELLED')}>
                          Отменить
                        </Button>
                      )}
                    </div>
                  </div>
                ) : null }
              </section>

              <section className="w-full mt-16 xl:mt-0 flex flex-col gap-6">
                {!productAddSuccess && data.status !== 'CANCELLED' && data.status !== 'COMPLETED' && data.status !== 'ACCEPTED' && (
                  <div className="flex items-center justify-center sm:justify-end">
                    <AddDialog btnText="Добавить продукт" dialogTitle="Добавить продукт" dialogDesc="Заполните все поля чтобы добавить продукт">
                      { productsAddError && (
                        <ErrorItem title='Ошибка' desc={productsAddErrorText} />
                      ) }

                      <AddForm form={productAddForm} onSubmit={productAddSubmit} success={productAddSuccess} successDesc="Новый продукт успешно добавлен">
                        <IncomesEditFormFields
                          providerID={data.provider?.id}
                          form={productAddForm}
                        />

                        <Button className="mt-5" type="submit">
                          Добавить товар
                        </Button>
                      </AddForm>
                    </AddDialog>
                  </div>
                )}

                <div className="w-full flex flex-col gap-3">
                  { error && (
                    <ErrorItem title='Ошибка' desc={errorText} />
                  ) }

                  {!incomeItemsLoading ? (
                    <AddForm form={productEditForm} onSubmit={(data) => {
                      const _temp = inputData.map((item, index) => {
                        const itemId = incomeItemsData[index]?.id
                        const tRow = document.querySelector(`#income-item-${itemId}`)
                        const count = item?.countValue !== undefined ? item.countValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="count"]')?.value.replace(/\s/g, '')
                        const price = item?.priceValue !== undefined ? item.priceValue?.replace(/\s/g, '') : tRow?.querySelector('input[name="price"]')?.value.replace(/\s/g, '')
                        const sale_price = item?.salePriceValue !== undefined ? item.salePriceValue?.replace(/\s/g, '') :  tRow?.querySelector('input[name="sale_price"]')?.value.replace(/\s/g, '')
                        if (+count === 0 || +price === 0 || +sale_price === 0) return true;
                        return false
                      })

                      if (_temp.some((e) => e)) {
                        if (confirm('У вас есть поля с 0 или пустые поля, вы уверены что хотите сохранить?')) productEditSubmit(data)
                        return
                      }

                      productEditSubmit(data)
                    }} success={productEditSuccess} successDesc='Данные успешно изменены'>
                      { data.status === 'CREATED' && incomeItemsData && Array.isArray(incomeItemsData) && incomeItemsData.length !== 0 ? (
                        <Button type='submit' variant='destructive' disabled={productsEditPending}>
                          <Check className='w-4 h-4 mr-2' /> Сохранить
                        </Button>
                      ) : null }

                      <TableItem bodyId='income-body' data={incomeItemsData} headerData={incomesEditTHData} notFoundText='Добавьте продукт'>
                        {incomeItemsData && Array.isArray(incomeItemsData) && incomeItemsData.map((item, index) => {
                          return (
                            <TableRow id={`income-item-${item.id}`} className='income-item' key={item.id}>
                              <TableCell>
                                <input type="hidden" name='income_item_id' value={item.id}/>
                                {index + 1}
                              </TableCell>
                              <TableCell>{item.product?.name}</TableCell>
                              <TableCell className='flex items-center gap-2'>
                                <NumberFormField
                                  control={productEditForm.control}
                                  name='count'
                                  placeholder='Количество товара'
                                  disabled={data.status !== 'CREATED'}
                                  _value={inputData && inputData[index]?.countValue !== undefined ? inputData[index]?.countValue : ''}
                                  _onChange={(e: any) => handleInputValuesChange(index, 'countValue', e)}
                                />
                                <p className='font-medium'>{translatedData(item.product?.unit_type)}</p>
                              </TableCell>
                              <TableCell>
                                <NumberFormField
                                  control={productEditForm.control}
                                  name='price'
                                  placeholder='Цена закупа'
                                  disabled={data.status !== 'CREATED'}
                                  _value={inputData && inputData[index]?.priceValue !== undefined ? inputData[index]?.priceValue : ''}
                                  _onChange={(e: any) => handleInputValuesChange(index, 'priceValue', e)}
                                />
                              </TableCell>
                              <TableCell className='flex items-center gap-2'>
                                <NumberFormField
                                  control={productEditForm.control}
                                  name='sale_price'
                                  placeholder='Продажная цена'
                                  disabled={data.status !== 'CREATED'}
                                  _value={inputData && inputData[index]?.salePriceValue !== undefined ? inputData[index]?.salePriceValue : ''}
                                  _onChange={(e: any) => handleInputValuesChange(index, 'salePriceValue', e)}
                                />
                              </TableCell>
                              <TableCell>{formatter.format(item.total)} сум</TableCell>
                              {data.status === 'COMPLETED' && (
                                <TableCell>
                                  <a href={`${getUrl()}/core/print-barcode/product/${item.product?.id}/`} target="_blank">
                                    <Button size="icon" type='button'>
                                      <ScanLine className="w-4 h-4"/>
                                    </Button>
                                  </a>
                                </TableCell>
                              )}
                              {data.status === 'CREATED' && (
                                <TableCell className="flex items-center gap-3">
                                  <Button variant="destructive" size="icon" disabled={isDeleting} onClick={() => deleteItem(`api/incomes/${id}/income-items`, item.id, ["Incomes"])} title='Удалить'>
                                    <Trash2 className="w-4 h-4"/>
                                  </Button>
                                </TableCell>
                              )}
                            </TableRow>
                          )
                        })}
                      </TableItem>
                    </AddForm>
                  ) : (
                    <SectionTableSkeleton/>
                  )}
                </div>

                <div className='z-30 mt-6 pb-6 flex flex-col gap-2 text-xl font-bold bg-white'>
                  <p className='flex justify-end'>Сумма закупа: {formatter.format(data.total)} сум</p>
                  <p className='flex justify-end'>Сумма продажной цены: {formatter.format(data.total_sale_price)} сум</p>
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

export default IncomesEditPage