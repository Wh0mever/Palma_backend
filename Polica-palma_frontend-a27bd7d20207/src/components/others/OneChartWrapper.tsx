import React from "react"

interface OneChartWrapperProps {
  title: string
  children: React.ReactNode
}

const OneChartWrapper = ({ title, children }: OneChartWrapperProps) => {
  return (
    <div className='w-full flex flex-col gap-5'>
      <h3 className='text-3xl font-bold'>{title}</h3>
      { children }
    </div>
  )
}

export default OneChartWrapper