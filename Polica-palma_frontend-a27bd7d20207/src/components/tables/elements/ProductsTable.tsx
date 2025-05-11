import TableItem from '@/components/tables/TableItem.tsx'
import {TablesProps} from '@/typing/interfaces.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'
import {productsTHData} from '@/data/tablesHeaderData.ts'
import translatedData from '@/data/translatedData.ts'
import {Button} from '@/components/ui/button.tsx'
import {ScanLine} from 'lucide-react'
import getUrl from '@/config.ts'
import getUserData from '@/helpers/getUserData.ts'

const ProductsTable = ({ data }: TablesProps) => {
  const { userType } = getUserData()
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={productsTHData} notFoundText='Товары не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{formatter.format(item.price)} сум</TableCell>
          <TableCell>{translatedData(item.unit_type)}</TableCell>
          <TableCell>{item.category?.name}</TableCell>
          <TableCell>{item.code}</TableCell>
          <TableCell className='flex items-center gap-4'>
            <a href={`${getUrl()}/core/print-barcode/product/${item.id}/`} target='_blank' className={`${!item.is_barcode_printable ? 'pointer-events-none opacity-60' : ''}`}>
              <Button variant='outline' size='icon'>
                <ScanLine className='w-4 h-4'/>
              </Button>
            </a>
            <EditItem link={`/dashboard/product/products/edit/${item.id}`}/>
            { userType !== 'SALESMAN' && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && (
              <DeleteDialog
                item={item.name}
                id={item.id}
                url='api/products'
                invalidatesTags={["Products"]}
              />
            ) }
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default ProductsTable