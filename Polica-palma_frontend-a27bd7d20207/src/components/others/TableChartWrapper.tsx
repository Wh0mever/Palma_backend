import React from "react"

interface TableChartWrapperProps {
  children: React.ReactNode
}

const TableChartWrapper = ({ children }: TableChartWrapperProps) => {
  return (
    <div className='w-full flex flex-col 2xl:flex-row items-center gap-16'>
      { children }
    </div>
  )
}

export default TableChartWrapper