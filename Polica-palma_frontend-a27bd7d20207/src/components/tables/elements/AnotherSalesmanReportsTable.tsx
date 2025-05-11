import {anotherSalesmanReportsTHData} from "@/data/tablesHeaderData.ts"
import {TableCell, TableRow} from "@/components/ui/table.tsx"
import {Link} from "react-router-dom"
import {Button} from "@/components/ui/button.tsx"
import {Eye} from "lucide-react"
import TableItem from "@/components/tables/TableItem.tsx"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"
import {TablesProps} from "@/typing/interfaces.ts"

const AnotherSalesmanReportsTable = ({ data }: TablesProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <>
      <TableItem data={data} headerData={anotherSalesmanReportsTHData} notFoundText='Работники не найдены!'>
        {data && Array.isArray(data) && data.map((item, index) => (
          <TableRow key={item.id}>
            <TableCell>{++index}</TableCell>
            <TableCell>{item.name}</TableCell>
            <TableCell>{formatter.format(item.balance)} сум</TableCell>
            <TableCell>{formatter.format(item.payment_sum)} сум</TableCell>
            <TableCell>
              <Link to={`/dashboard/reports/another-salesman/${item.id}/`}>
                <Button size='icon'>
                  <Eye className='w-4 h-4' />
                </Button>
              </Link>
            </TableCell>
          </TableRow>
        ))}
      </TableItem>
    </>
  )
}

export default AnotherSalesmanReportsTable