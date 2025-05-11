import TableItem from '@/components/tables/TableItem.tsx'
import {writeOffTHData} from '@/data/tablesHeaderData.ts'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import formatDate from '@/helpers/formatDate.ts'
import {Button} from '@/components/ui/button.tsx'
import {Trash2} from 'lucide-react'
import useDeleteItem from '@/hooks/useDeleteItem.ts'
import getUserData from "@/helpers/getUserData.ts"

const WriteOffTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()
  const { deleteItem, isDeleting } = useDeleteItem()

  return (
    <TableItem data={data} headerData={writeOffTHData} notFoundText='Списанные товары из склада не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.product_name}</TableCell>
          <TableCell>{formatter.format(item.count)}</TableCell>
          <TableCell>{item.comment}</TableCell>
          <TableCell>{formatDate(item.created_at)}</TableCell>
          <TableCell>
            { userType !== 'WAREHOUSE_MASTER' && (
              <Button
                size='icon'
                variant='destructive'
                disabled={isDeleting}
                onClick={() => deleteItem(`api/warehouse/write-offs`, item.id, ["Warehouse", "WriteOffs"])}
              >
                <Trash2 className='w-4 h-4' />
              </Button>
            ) }
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default WriteOffTable