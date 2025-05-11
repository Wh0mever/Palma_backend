import {useEffect, useState} from 'react'

const useValues = (stateData: any, setStateData = {}, isLoading: boolean, data: any) => {
  const [inputValues, setInputValues] = useState(stateData)

  useEffect(() => {
    if (!isLoading && data) {
      setInputValues(setStateData)
    }
  }, [data, isLoading])

  const handleInputChange = (key: any, value: any) => {
    setInputValues({
      ...inputValues,
      [key]: value
    })
  }

  return { inputValues, handleInputChange }
}

export default useValues