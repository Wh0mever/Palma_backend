import TableItem from '@/components/tables/TableItem.tsx'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Check, ScanLine, Trash2} from 'lucide-react'
import {TablesProps} from '@/typing/interfaces.ts'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {incomesEditTHData} from '@/data/tablesHeaderData.ts'
import useDeleteItem from '@/hooks/useDeleteItem.ts'
import getUrl from '@/config.ts'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import {z} from 'zod'
import {useState} from 'react'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import translatedData from '@/data/translatedData.ts'

interface IncomesEditTableProps extends TablesProps {
  id: string | undefined
  statusData: any
  refetch: any
}

interface InputValues {
  countValue: null | string
  priceValue: null | string
  salePriceValue: null | string
}

const IncomesEditTable = ({ data, id, statusData, refetch }: IncomesEditTableProps) => {
  const { formatter } = useNumberFormatter()
  const [productID, setProductID] = useState<string>('')
  const { deleteItem, isDeleting } = useDeleteItem()
  const [inputValues, setInputValues] = useState<InputValues>({
    countValue: null,
    priceValue: null,
    salePriceValue: null
  })
  const { form, onSubmit, pending, success } = useAxiosPut(
    {
      count: z.string().optional(),
      price: z.string().optional(),
      sale_price: z.string().optional(),
    },
    {
      "count": inputValues.countValue?.replace(/\s/g, ''),
      "price": inputValues.priceValue?.replace(/\s/g, ''),
      "sale_price": inputValues.salePriceValue?.replace(/\s/g, ''),
    },
    `api/incomes/${id}/income-items`,
    productID,
    ["Incomes"]
  )

  const handleInputValuesChange = (key: keyof InputValues, value: string) => {
    setInputValues({
      ...inputValues,
      [key]: value
    })
  }

  return (
    <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Данные успешно изменены'>
      <TableItem data={data} headerData={incomesEditTHData} notFoundText='Добавьте продукт'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.product?.name}</TableCell>
            <TableCell className='flex items-center gap-2'>
              <NumberFormField
                control={form.control}
                name='count'
                placeholder='Количество товара'
                disabled={statusData.status !== 'CREATED'}
                _value={inputValues.countValue !== null ? inputValues.countValue : String(item.count).slice(0, -3)}
                _onChange={(e: any) => handleInputValuesChange('countValue', e)}
              />
              <p className='font-medium'>{translatedData(item.product?.unit_type)}</p>
            </TableCell>
            <TableCell>
              <NumberFormField
                control={form.control}
                name='price'
                placeholder='Цена закупа'
                disabled={statusData.status !== 'CREATED'}
                _value={inputValues.priceValue !== null ? inputValues.priceValue : String(item.price).slice(0, -3)}
                _onChange={(e: any) => handleInputValuesChange('priceValue', e)}
              />
            </TableCell>
            <TableCell className='flex items-center gap-2'>
              <NumberFormField
                control={form.control}
                name='sale_price'
                placeholder='Продажная цена'
                disabled={statusData.status !== 'CREATED'}
                _value={inputValues.salePriceValue !== null ? inputValues.salePriceValue : String(item.sale_price).slice(0, -3)}
                _onChange={(e: any) => handleInputValuesChange('salePriceValue', e)}
              />
            </TableCell>
            <TableCell>{formatter.format(item.total)} сум</TableCell>
            {statusData.status === 'COMPLETED' && (
              <TableCell>
                <a href={`${getUrl()}/core/print-barcode/product/${item.product?.id}/`} target="_blank">
                  <Button size="icon">
                    <ScanLine className="w-4 h-4"/>
                  </Button>
                </a>
              </TableCell>
            )}
            {statusData.status === 'CREATED' && (
              <TableCell className="flex items-center gap-3">
                <Button type='submit' size='icon' disabled={pending} onClick={() => setProductID(item.id)}>
                  <Check className='w-4 h-4' />
                </Button>
                <Button variant="destructive" size="icon" disabled={isDeleting} onClick={() => deleteItem(`api/incomes/${id}/income-items`, item.id, refetch)} title='Удалить'>
                  <Trash2 className="w-4 h-4"/>
                </Button>
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableItem>
    </AddForm>
  )
}

export default IncomesEditTable