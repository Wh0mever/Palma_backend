import axios from 'axios'
import { useEffect, useRef, useState } from 'react'
import getAuthorizationHeader from '@/helpers/getAuthHeader.ts'
import getUrl from '@/config.ts'

type AxiosGetData<T> = {
  data: T
  isLoading: boolean
  refetchData?: () => void
}

const useAxiosGet = <T>(url: string, params: any = {}): AxiosGetData<T> => {
  const [data, setData] = useState<T>({} as T)
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const apiUrl: string = `${getUrl()}/${url}`

  const abortControllerRef = useRef<AbortController | null>(null)

  const fetchData = async () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }

    const controller = new AbortController()
    abortControllerRef.current = controller

    try {
      const response = await axios.get<T>(apiUrl, {
        headers: {
          Authorization: getAuthorizationHeader(),
        },
        params: params,
        signal: controller.signal
      })
      setData(response.data)
      setIsLoading(false)
      localStorage.setItem(url, JSON.stringify(response.data))
    } catch (e) {
      console.log('Response error: ', e)
    }
  }

  useEffect(() => {
    fetchData()
    const cachedData = localStorage.getItem(url)

    if (cachedData) {
      setData(JSON.parse(cachedData))
      setIsLoading(false)
    } else {
      fetchData()
    }

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort()
      }
    }
  }, [apiUrl])

  return { data, isLoading, refetchData: fetchData }
}

export default useAxiosGet