import {TablesProps} from '@/typing/interfaces.ts'
import {factoriesCategoriesTHData} from '@/data/tablesHeaderData.ts'
import {TableCell, TableRow} from '@/components/ui/table.tsx'
import EditItem from '@/components/items/EditItem.tsx'
import DeleteDialog from '@/components/others/DeleteDialog.tsx'
import TableItem from '@/components/tables/TableItem.tsx'
import useNumberFormatter from '@/hooks/useNumberFormatter.ts'

const FactoriesCategoriesTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <TableItem data={data} headerData={factoriesCategoriesTHData} notFoundText='Категории не найдены!'>
      {data && Array.isArray(data) && data.map((item, index) => (
        <TableRow key={item.id}>
          <TableCell>{++index}</TableCell>
          <TableCell>{item.name}</TableCell>
          <TableCell>{item.industry?.name || '-'}</TableCell>
          <TableCell>{formatter.format(item.charge_percent) || '-'}%</TableCell>
          <TableCell className='flex items-center gap-4'>
            <EditItem link={`/dashboard/factories/categories/edit/${item.id}`} />
            <DeleteDialog
              desc
              id={item.id}
              url='api/product-factory-categories/product-factory-categories'
              item={item.name}
              invalidatesTags={["FactoriesCategories"]}
            />
          </TableCell>
        </TableRow>
      ))}
    </TableItem>
  )
}

export default FactoriesCategoriesTable