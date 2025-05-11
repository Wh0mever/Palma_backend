import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import translateFunc from '@/data/translatedData.ts'
import formatDate from '@/helpers/formatDate.ts'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {Pencil} from 'lucide-react'
import PaymentDialog from '@/components/others/PaymentDialog.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import {outlaysTHData} from '@/data/tablesHeaderData.ts'
import getUserData from '@/helpers/getUserData.ts'

const OutlaysTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()

  return (
    <TableItem data={data} headerData={outlaysTHData} notFoundText='Причины расхода не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.title}</TableCell>
          <TableCell>{translateFunc(item.outlay_type)}</TableCell>
          <TableCell>{item.industry?.name || '-'}</TableCell>
          <TableCell>{item.comment || '-'}</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <Link to={`/dashboard/payment/outlays/edit/${item.id}`}>
              <Button size='icon' title='Редактировать'>
                <Pencil className='w-4 h-4'/>
              </Button>
            </Link>

            <PaymentDialog
              dialogTitle='Добавить платёж'
              dialogDescription='Заполните все поля чтобы добавить платёж'
              page='outlays'
              item={item.id}
              outlay_type={item.outlay_type}
              invalidatesTags={["Payments", "Outlays", "Cashiers"]}
            />

            { userType !== 'CASHIER' && (
              <DeleteDialog
                desc
                id={item.id}
                url='api/outlays'
                item={item.title}
                invalidatesTags={["Outlays"]}
              />
            ) }
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default OutlaysTable