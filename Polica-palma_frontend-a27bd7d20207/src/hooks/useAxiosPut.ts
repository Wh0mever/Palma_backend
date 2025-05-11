import {z} from 'zod'
import {useForm} from 'react-hook-form'
import {zodResolver} from '@hookform/resolvers/zod'
import {api} from "@/services/api.ts"
import {useEffect, useState} from "react"
import {toast} from "@/components/ui/use-toast.tsx"

const useAxiosPut = (schemaObject = {}, axiosData = {}, url: string, id: string | undefined | any = undefined, invalidatesTags: string[] | undefined) => {
  const apiUrl: string = `${url}/${id}/`
  const [putData, { error, isLoading, isSuccess: mutationSuccess }] = api.usePutDataMutation<any>()
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
      await putData({ url: apiUrl, body: { ...data, ...axiosData }, invalidatesTags }).unwrap()

      if (isSuccess) {
        form.reset()
      }
    } catch (e: any) {
      console.error('POST error: ', e)
      toast({
        variant: "destructive",
        title: "Произошла ошибка",
        description: e ? JSON.stringify(e?.data?.detail || e?.data) : 'Ошибка'
      })
    }
  }

  return { success: isSuccess, onSubmit, form, pending: isLoading, error, errorText: error ? JSON.stringify(error.data.detail) || JSON.stringify(error.data) || error : null }
}

export default useAxiosPut