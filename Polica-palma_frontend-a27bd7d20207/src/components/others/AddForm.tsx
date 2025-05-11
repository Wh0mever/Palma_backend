import React from "react"
import {Form} from '@/components/ui/form.tsx'
import {Alert, AlertDescription, AlertTitle} from '@/components/ui/alert.tsx'
import {Check} from 'lucide-react'
import ErrorItem from '@/components/items/ErrorItem.tsx'

interface AddFormProps {
  children: React.ReactNode
  form: any
  onSubmit: (data: any) => void
  success: boolean
  successDesc: string
  error?: boolean
  errorDesc?: any
  notMT?: boolean
}

const AddForm = ({ children, form, onSubmit, success, successDesc, error, errorDesc, notMT }: AddFormProps) => {
  return (
    <Form {...form}>
      <form className={`flex flex-col gap-5 ${!notMT ? 'mt-5' : ''}`} onSubmit={form.handleSubmit(onSubmit)}>
        { success && (
          <Alert>
            <Check className='w-4 h-4' />
            <AlertTitle>Успешно</AlertTitle>
            <AlertDescription>{successDesc}</AlertDescription>
          </Alert>
        ) }

        { error && (
          <ErrorItem title='Ошибка' desc={errorDesc} />
        ) }

        {children}
      </form>
    </Form>
  )
}

export default AddForm