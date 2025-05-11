import {TablesProps} from '@/typing/interfaces.ts'
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'
import translatedData from '@/data/translatedData.ts'
import getUserData from '@/helpers/getUserData.ts'

const BouquetsTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()

  return (
    <Table className='w-full'>
      <TableHeader className='z-30 sticky top-0 bg-white dark:bg-neutral-950'>
        <TableRow>
          <TableHead>№</TableHead>
          <TableHead>Название</TableHead>
          <TableHead>Категория</TableHead>
          { userType !== 'WAREHOUSE_MASTER' && (
            <TableHead>Себестоимость</TableHead>
          ) }
          <TableHead>Цена продажи</TableHead>
          <TableHead>Статус</TableHead>
          <TableHead>Тип продажи</TableHead>
          <TableHead>Код товара</TableHead>
          <TableHead>Дата создания</TableHead>
          <TableHead>Дата окончания</TableHead>
          <TableHead></TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{item.category?.name}</TableCell>
            { userType !== 'WAREHOUSE_MASTER' && (
              <TableCell>{formatter.format(item.self_price)} сум</TableCell>
            ) }
            <TableCell>{formatter.format(item.price)} сум</TableCell>
            <TableCell>{translatedData(item.status)}</TableCell>
            <TableCell>{translatedData(item.sales_type)}</TableCell>
            <TableCell>{item.product_code}</TableCell>
            <TableCell>{formatDate(item.created_at) || '-'}</TableCell>
            <TableCell>{item.finished_at !== null ? formatDate(item.finished_at) : '-'}</TableCell>
            <TableCell className='flex items-center gap-4'>
              <EditItem link={`/dashboard/factories/bouquets/edit/${item.id}`} isEye />
              { userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && <DeleteDialog id={item.id} url='api/factories/product-factories' item={item.name} desc invalidatesTags={["Bouquets"]} /> }
            </TableCell>
          </TableRow>
        ))}
      </TableBody>

      {data && Array.isArray(data) && data.length === 0 && <p className='mt-4 text-xl font-bold text-neutral-600 dark:text-neutral-400'>Букеты не найдены!</p>}
    </Table>
  )
}

export default BouquetsTable