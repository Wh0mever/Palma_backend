import {Table, TableBody, TableHeader} from '@/components/ui/table.tsx'
import React from 'react'
import TableRowItem from '@/components/tables/TableRowItem.tsx'

interface TableItemProps {
  data: any
  headerData: { title: string }[]
  children: React.ReactNode
  notFoundText: string
  bodyId?: string
}

const TableItem = ({ data, headerData, children, notFoundText, bodyId }: TableItemProps) => {
  return (
    <Table className='w-full'>
      <TableHeader className='z-30 w-full sticky top-0 bg-white dark:bg-neutral-950'>
        <TableRowItem data={headerData} />
      </TableHeader>

      <TableBody id={bodyId}>
        {children}
      </TableBody>

      {data && Array.isArray(data) && data.length === 0 && <p className='mt-4 text-xl font-bold text-neutral-600 dark:text-neutral-400'>{notFoundText}</p>}
    </Table>
  )
}

export default TableItem