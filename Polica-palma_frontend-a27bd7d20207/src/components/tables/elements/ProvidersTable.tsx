import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import PaymentDialog from '@/components/others/PaymentDialog.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {providersTHData} from '@/data/tablesHeaderData.ts'
import formatPhoneNumber from '@/helpers/formatPhoneNumber.ts'

const ProvidersTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={providersTHData} notFoundText='Поставщики не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.full_name}</TableCell>
          <TableCell>{item.phone_number ? formatPhoneNumber(item.phone_number) : '-'}</TableCell>
          <TableCell>{item.org_name || '-'}</TableCell>
          <TableCell>{formatter.format(item.balance)} сум</TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/income/providers/edit/${item.id}`} />
            <PaymentDialog
              dialogTitle='Добавить платёж'
              dialogDescription='Заполните все поля чтобы добавить платёж'
              page='providers'
              item={item.id}
              invalidatesTags={["Payments", "Cashiers"]}
            />
            <DeleteDialog
              desc
              id={item.id}
              url='api/providers'
              item={item.full_name}
              invalidatesTags={["Providers"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default ProvidersTable