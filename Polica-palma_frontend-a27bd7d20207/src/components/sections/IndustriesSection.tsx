import SectionsTop from '@/components/others/SectionsTop.tsx'
import useSearch from '@/hooks/useSearch.ts'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import IndustriesTable from '@/components/tables/elements/IndustriesTable.tsx'
import IndustriesFormFields from '@/components/forms/IndustriesFormFields.tsx'
import {Button} from '@/components/ui/button.tsx'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import {useEffect, useState} from 'react'
import useNumberValue from '@/hooks/useNumberValue.ts'
import {api} from "@/services/api.ts"
import ErrorItem from "@/components/items/ErrorItem.tsx"

interface CheckboxValues {
  hasSaleCompensation: boolean
}

const IndustriesSection = () => {
  const { data, isLoading } = api.useGetIndustriesQuery('')
  const { filteredData, searchTerm, handleSearchChange, handleSearch } = useSearch(data, 'name')
  const [checkboxValues, setCheckboxValues] = useState<CheckboxValues>({
    hasSaleCompensation: false
  })

  const { numberValue, handleNumberChange, setNumberValue } = useNumberValue()

  const { success, form, onSubmit, pending, error, errorText } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название магазина" }),
      sale_compensation_percent: z.string().optional(),
      has_sale_compensation: z.boolean().optional()
    },
    {
      "sale_compensation_percent": numberValue.replace(/\s/g, '')
    },
    `api/industries/`,
    ["Industries"]
  )

  useEffect(() => {
    if (success) {
      setNumberValue('')
    }
  }, [success])

  const handleCheckboxChange = (key: keyof CheckboxValues, value: boolean) => {
    setCheckboxValues({
      ...checkboxValues,
      [key]: value
    })
  }

  return (
    <>
      { isLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full h-full relative flex flex-col gap-8'>
          <SectionsTop
            title='Магазины'
            placeholder='Поиск магазина'
            inputValue={searchTerm}
            onChange={handleSearchChange}
            onClick={handleSearch}
          />

          <div className='flex items-center justify-center sm:justify-end'>
            {!success ? (
              <AddDialog btnText='Добавить магазин' dialogTitle='Добавить магазин' dialogDesc='Заполните все поля чтобы добавить магазин'>
                <AddForm
                  form={form}
                  onSubmit={onSubmit}
                  success={success}
                  successDesc='Новый магазин успешно добавлен'
                >
                  { error && (
                    <ErrorItem title='Ошибка' desc={errorText} />
                  ) }

                  <IndustriesFormFields
                    form={form}
                    checked={checkboxValues.hasSaleCompensation}
                    onCheckedChange={(e: any) => handleCheckboxChange('hasSaleCompensation', e)}
                    numberValue={numberValue}
                    numberChange={handleNumberChange}
                  />
                  <Button className='mt-5' disabled={pending}>Добавить магазин</Button>
                </AddForm>
              </AddDialog>
            ) : null}
          </div>

          <IndustriesTable data={filteredData}/>
        </section>
      )}
    </>
  )
}

export default IndustriesSection