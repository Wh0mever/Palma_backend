import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import formatDate from '@/helpers/formatDate.ts'
import translateFunc from '@/data/translatedData.ts'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {paymentsTHData} from '@/data/tablesHeaderData.ts'
import getUserData from '@/helpers/getUserData.ts'
import {Link} from "react-router-dom"
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from "@/components/ui/dialog.tsx"
import {Button} from "@/components/ui/button.tsx"
import {Pencil} from "lucide-react"
import useAxiosPut from "@/hooks/useAxiosPut.ts"
import {z} from "zod"
import {useState} from "react"
import AddForm from "@/components/others/AddForm.tsx"
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"
import translatedData from "@/data/translatedData.ts"
import NumberFormField from "@/components/others/NumberFormField.tsx"
import TextareaFormField from "@/components/others/TextareaFormField.tsx"
import DatePicker from "@/components/others/DatePicker.tsx"
import {format} from 'date-fns'

interface InputValues {
  amount: string
  comment: string
}

const PaymentsTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()
  const [paymentId, setPaymentId] = useState<string>('')
  const [paymentItem, setPaymentItem] = useState<string>('')
  const { data: paymentMethodsData, isLoading: paymentMethodsLoading } = api.useGetPaymentMethodsQuery('')
  const { data: optionsData, isLoading: optionsLoading } = api.useGetPaymentCreateOptionsQuery('')
  const { data: createdUsersData, isLoading: createdUsersLoading } = api.useGetUsersForPaymentsQuery('')
  const [inputValues, setInputValues] = useState<InputValues>({
    amount: '',
    comment: ''
  })

  const handleInputChange = (key: keyof InputValues, value: string) => {
    setInputValues({
      ...inputValues,
      [key]: value
    })
  }

  const { success, form, onSubmit, pending, error, errorText } = useAxiosPut(
    {
      payment_method: z.string().optional(),
      payment_type: z.string().optional(),
      created_user: z.string().optional(),
      amount: z.string().optional(),
      comment: z.string().optional(),
      created_at: z.date().optional()
    },
    {
      "amount": inputValues.amount !== '' ? String(inputValues.amount).replace(/\s/g, '') : '',
      "comment": inputValues.comment !== '' ? inputValues.comment : '',
    },
    `api/payments/${paymentItem}`,
    paymentId,
    ["Payments", "Cashiers"]
  )

  return (
    <TableItem data={data} headerData={paymentsTHData} notFoundText='Платежи не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>
            {
              item.payment_model_type === 'OUTLAY'
                ? `Причина расхода: ${item.outlay?.title}`
                : item.payment_model_type === 'ORDER'
                  ? <Link to={`/dashboard/order/orders/edit/${item.order?.id}`} className='hover:underline'>Продажа #{item.order?.id}</Link>
                  : item.payment_model_type === 'PROVIDER'
                    ? `Поставщик: ${item.provider?.full_name}`
                    : item.payment_model_type === 'INCOME'
                      ? <Link to={`/dashboard/income/incomes/edit/${item.income?.id}`} className='hover:underline'>Закуп #{item.income?.id}</Link>
                      : '-'
            }
          </TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell>{formatter.format(item.amount)} сум</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell>{translateFunc(item.payment_method?.name)}</TableCell>
          <TableCell>{translateFunc(item.payment_type)}</TableCell>
          <TableCell>{item.created_user?.first_name || item.created_user?.username || '-'}</TableCell>
          <TableCell>{item.worker?.first_name || item.worker?.username || '-'}</TableCell>
          {!success && userType === 'ADMIN' ? (
            <TableCell className='flex items-center gap-3'>
              <Dialog>
                <DialogTrigger>
                  <Button size='icon' onClick={() => {
                    setPaymentId(item.id)
                    setInputValues({ amount: item.amount, comment: item.comment })

                    if (item.payment_model_type === 'OUTLAY') {
                      setPaymentItem('outlays')
                    }

                    if (item.payment_model_type === 'ORDER') {
                      setPaymentItem('orders')
                    }

                    if (item.payment_model_type === 'PROVIDER') {
                      setPaymentItem('providers')
                    }

                    if (item.payment_model_type === 'INCOME') {
                      setPaymentItem('incomes')
                    }
                  }}>
                    <Pencil className='w-4 h-4' />
                  </Button>
                </DialogTrigger>

                <DialogContent>
                  <DialogHeader>
                    <DialogTitle>Изменить данные</DialogTitle>
                  </DialogHeader>

                  <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Данные успешно изменены' error={error} errorDesc={errorText}>
                    <ReactSelectFormField
                      idData={paymentMethodsData}
                      control={form.control}
                      isLoading={paymentMethodsLoading}
                      name="payment_method"
                      placeholder={item.payment_method?.name}
                      label="Метод оплаты"
                    />
                    <ReactSelectFormField
                      isValue
                      valueData={optionsData?.payment_types}
                      control={form.control}
                      isLoading={optionsLoading}
                      name="payment_type"
                      placeholder={translatedData(item.payment_type)}
                      label="Тип оплаты"
                    />
                    <ReactSelectFormField
                      idData={createdUsersData}
                      control={form.control}
                      isLoading={createdUsersLoading}
                      name="created_user"
                      placeholder={item.created_user?.first_name || item.created_user?.username || '-'}
                      label="Создатель"
                    />
                    <NumberFormField
                      control={form.control}
                      name='amount'
                      label='Сумма'
                      _value={inputValues.amount}
                      _onChange={(e: any) => handleInputChange('amount', e)}
                    />
                    <DatePicker
                      isForm
                      name='created_at'
                      text={format(item.created_at, 'dd.MM.yyyy')}
                      label='Дата создания'
                      control={form.control}
                    />
                    <TextareaFormField
                      control={form.control}
                      name='comment'
                      label='Комментарий'
                      _value={inputValues.comment}
                      _onChange={(e: any) => handleInputChange('comment', e.target.value)}
                    />

                    <Button type='submit' disabled={pending}>Изменить данные</Button>
                  </AddForm>
                </DialogContent>
              </Dialog>

              <DeleteDialog
                desc
                id={item.id}
                url='api/payments'
                item={item.comment || item.id}
                invalidatesTags={["Payments", "Cashiers"]}
              />
            </TableCell>
          ) : null }
        </TableRow>
      ))}
    </TableItem>
  )
}

export default PaymentsTable