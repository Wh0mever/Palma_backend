import {z} from 'zod'
import {useForm} from 'react-hook-form'
import {zodResolver} from '@hookform/resolvers/zod'
import {api} from "@/services/api.ts"
import {useEffect, useState} from "react"

type AxiosPostData<T> = {
  success: boolean
  onSubmit: (data: object) => Promise<void>
  form: any
  pending?: boolean
  error?: boolean
  errorText?: any
  data?: T
  invalidatesTags?: any
}

const useAxiosPost = <T>(schemaObject = {}, axiosData = {}, url: string, invalidatesTags: string[] | undefined): AxiosPostData<T> => {
  const [postData, { error, isLoading, isSuccess: mutationSuccess }] = api.usePostDataMutation<any>()
  const [isSuccess, setIsSuccess] = useState<boolean>(false)

  useEffect(() => {
    if (mutationSuccess) {
      setIsSuccess(true)

      const timeoutId = setTimeout(() => {
        setIsSuccess(false)
      }, 500)

      return () => clearTimeout(timeoutId)
    }
  }, [mutationSuccess])

  const FormSchema = z.object(schemaObject)

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  })

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    try {
      await postData({ url: url, body: { ...data, ...axiosData }, invalidatesTags }).unwrap()

      if (isSuccess) {
        form.reset()
      }
    } catch (e) {
      console.error('POST error: ', e)
    }
  }

  return {
    form,
    onSubmit,
    success: isSuccess,
    pending: isLoading,
    error: !!error,
    errorText: error ? JSON.stringify(error.data) : null,
  }
}

export default useAxiosPost