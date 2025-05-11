import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translateFunc from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import EditItem from '@/components/items/EditItem.tsx'
import PaymentDialog from '@/components/others/PaymentDialog.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {incomesTHData} from '@/data/tablesHeaderData.ts'

const IncomesTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={incomesTHData} notFoundText='Закупы не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.provider?.full_name}</TableCell>
          <TableCell>{translateFunc(item.status)}</TableCell>
          <TableCell>{formatter.format(item.total)} сум</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/income/incomes/edit/${item.id}`} />
            <PaymentDialog
              dialogTitle='Добавить платёж'
              dialogDescription='Заполните все поля чтобы добавить платёж'
              page='incomes'
              item={item.id}
              isDisabled={item.status !== 'COMPLETED'}
              invalidatesTags={["Payments", "Outlays", "Cashiers"]}
            />
            <DeleteDialog
              id={item.id}
              url='api/incomes'
              item={item.comment}
              invalidatesTags={["Incomes"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default IncomesTable