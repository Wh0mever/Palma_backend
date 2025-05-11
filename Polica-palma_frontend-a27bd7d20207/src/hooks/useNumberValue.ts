import {useEffect, useState} from 'react'

const useNumberValue = (isSuccess?: boolean | undefined | null) => {
  const [numberValue, setNumberValue] = useState<string>('')
  const handleNumberChange = (newValue: any) => setNumberValue(newValue)

  useEffect(() => {
    if (isSuccess) {
      setNumberValue('')
    }
  }, [isSuccess])

  return { numberValue, handleNumberChange, setNumberValue }
}

export default useNumberValue