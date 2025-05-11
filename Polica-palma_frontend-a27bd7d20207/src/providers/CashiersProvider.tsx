import React, { createContext, useContext } from 'react'
import {api} from "@/services/api.ts"

interface CashiersProviderProps {
  children: React.ReactNode
}

const CashiersContext = createContext<any>(undefined)

// eslint-disable-next-line react-refresh/only-export-components
export const useCashiers = () => {
  const context = useContext(CashiersContext)
  if (!context) {
    throw new Error('useCashiers must be used within a CashiersProvider')
  }
  return context
}

const CashiersProvider = ({ children }: CashiersProviderProps) => {
  const { data, isLoading } = api.useGetCashiersQuery('')
  const contextValue = React.useMemo(() => ({ data, isLoading }), [data, isLoading])

  return <CashiersContext.Provider value={contextValue}>{children}</CashiersContext.Provider>
}

export default CashiersProvider