import {useState} from 'react'
import formatDate from '@/helpers/formatDate.ts'

const useFilters = (initFilters: any) => {
  const [fromTime, setFromTime] = useState('fromTime' in initFilters ? initFilters['fromTime'] : '')
  const [toTime, setToTime] = useState('toTime' in initFilters ? initFilters['toTime'] : '')
  const [periodFrom, setPeriodFrom] = useState<Date>(initFilters['periodFrom'])
  const [periodFromTime, setPeriodFromTime] = useState<any>(initFilters['periodFromTime'])
  const [periodTo, setPeriodTo] = useState<Date>(initFilters['periodTo'])
  const [periodToTime, setPeriodToTime] = useState<any>(initFilters['periodToTime'])
  const [industry, setIndustry] = useState<string | null>('industry' in initFilters ? initFilters['industry']: null)
  const [productsCategory, setProductsCategory] = useState<string | null>('productsCategory' in initFilters ? initFilters['productsCategory']: null)
  const [factoriesCategory, setFactoriesCategory] = useState<string | null>('factoriesCategory' in initFilters ? initFilters['factoriesCategory']: null)
  const [client, setClient] = useState<string | null>('client' in initFilters ? initFilters['client']: null)
  const [status, setStatus] = useState<string | null>('status' in initFilters ? initFilters['status']: null)
  const [paymentType, setPaymentType] = useState<string | null>('paymentType' in initFilters ? initFilters['paymentType']: null)
  const [paymentModelType, setPaymentModelType] = useState<string | null>('paymentModelType' in initFilters ? initFilters['paymentModelType']: null)
  const [paymentMethod, setPaymentMethod] = useState<string | null>('paymentMethod' in initFilters ? initFilters['paymentMethod']: null)
  const [outlayType, setOutlayType] = useState<string | null>('outlayType' in initFilters ? initFilters['outlayType']: null)
  const [florist, setFlorist] = useState<string | null>('florist' in initFilters ? initFilters['florist']: null)
  const [createdUser, setCreatedUser] = useState<string | null>('createdUser' in initFilters ? initFilters['createdUser']: null)
  const [salesType, setSalesType] = useState<string | null>('salesType' in initFilters ? initFilters['salesType']: null)
  const [hasDebt, setHasDebt] = useState<string | null>('hasDebt' in initFilters ? initFilters['hasDebt']: null)
  const [outlay, setOutlay] = useState<string | null>('outlay' in initFilters ? initFilters['outlay']: null)
  const [indicator, setIndicator] = useState<string | null>('indicator' in initFilters ? initFilters['indicator']: null)
  const [salesman, setSalesman] = useState<string | null>('salesman' in initFilters ? initFilters['salesman']: null)
  const [created, setCreated] = useState<string | null>('created' in initFilters ? initFilters['created']: null)
  const [provider, setProvider] = useState<string | null>('provider' in initFilters ? initFilters['provider']: null)
  const [worker, setWorker] = useState<string | null>('worker' in initFilters ? initFilters['worker']: null)
  const [incomeType, setIncomeType] = useState<string | null>('incomeType' in initFilters ? initFilters['incomeType']: null)
  const [incomeReason, setIncomeReason] = useState<string | null>('incomeReason' in initFilters ? initFilters['incomeReason']: null)
  const [isDebt, setIsDebt] = useState<string | null>('isDebt' in initFilters ? initFilters['isDebt']: null)
  const [workerType, setWorkerType] = useState<string | null>('workerType' in initFilters ? initFilters['workerType']: null)
  const [orderField, setOrderField] = useState<string | null>('orderField' in initFilters ? initFilters['orderField']: null)

  const periodFromFormatted = periodFrom ? formatDate(periodFrom).split(',')[0] : ''
  const periodToFormatted = periodTo ? formatDate(periodTo).split(',')[0] : ''

  const periodFromTimeFormatted = periodFromTime ? `${formatDate(periodFromTime).split(',')[0]}${fromTime ? ` ${fromTime}` : ' 00:00'}` : ''
  const periodToTimeFormatted = periodToTime ? `${formatDate(periodToTime).split(',')[0]}${toTime ? ` ${toTime}` : ' 23:59'}` : ''

  return { periodFromTime, setPeriodFromTime, periodToTime, setPeriodToTime, periodFromTimeFormatted, periodToTimeFormatted, periodFrom, periodTo, setPeriodFrom, setPeriodTo, industry, setIndustry, productsCategory, setProductsCategory, factoriesCategory, setFactoriesCategory, periodFromFormatted, periodToFormatted, status, setStatus, client, setClient, paymentType, setPaymentType, paymentModelType, setPaymentModelType, paymentMethod, setPaymentMethod, outlayType, setOutlayType, florist, setFlorist, createdUser, setCreatedUser, salesType, setSalesType, hasDebt, setHasDebt, outlay, setOutlay, indicator, setIndicator, salesman, setSalesman, created, setCreated, provider, setProvider, worker, setWorker, fromTime, setFromTime, toTime, setToTime, incomeType, setIncomeType, incomeReason, setIncomeReason, isDebt, setIsDebt, workerType, setWorkerType, orderField, setOrderField }
}

export default useFilters