/* eslint-disable @typescript-eslint/no-explicit-any */
import React from 'react'
import {Button} from '@/components/ui/button.tsx'
import {ChevronLeft} from 'lucide-react'
import AddForm from '@/components/others/AddForm.tsx'
import {useNavigate} from 'react-router-dom'

interface EditSectionProps {
  children: React.ReactNode
  form: any
  onSubmit: (data: any) => void
  success: boolean
}

const EditSection = ({ children, form, onSubmit, success }: EditSectionProps) => {
  const navigate = useNavigate()
  const returnPage = () => navigate(-1)

  return (
    <>
      <section className='w-full flex flex-col gap-8'>
        <Button className='w-48 mb-4' onClick={returnPage} variant='outline'>
          <ChevronLeft className='w-4 h-4 mr-2'/> Вернуться назад
        </Button>

        <h1 className="text-3xl font-bold">Редактировать</h1>

        <div className="pb-6">
          <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Успешно изменено'>
            {children}

            <Button type='submit'>
              Изменить данные
            </Button>
          </AddForm>
        </div>
      </section>
    </>
  )
}

export default EditSection