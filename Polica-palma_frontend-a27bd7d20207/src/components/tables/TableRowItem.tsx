import {TableHead, TableRow} from '@/components/ui/table.tsx'

interface TableRowItemProps {
  data: { title: string }[]
}

const TableRowItem = ({ data }: TableRowItemProps) => {
  return (
    <TableRow>
      { data && Array.isArray(data) && data.map((item, index) => <TableHead key={index}>{item.title}</TableHead>) }
    </TableRow>
  )
}

export default TableRowItem