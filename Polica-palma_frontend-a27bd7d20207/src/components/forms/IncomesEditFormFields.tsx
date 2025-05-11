import NewAddDialog from '@/components/others/NewAddDialog.tsx'
import ProductsFormFields from '@/components/forms/ProductsFormFields.tsx'
import {useState} from 'react'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import convertToBase64 from '@/helpers/convertToBase64.ts'
import {FormFieldsProps} from '@/typing/interfaces.ts'
import useNumberValue from '@/hooks/useNumberValue.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface PostImage {
  myFile: string | any
}

interface IncomesEditFormFieldsProps extends FormFieldsProps {
  providerID: string
}

const IncomesEditFormFields = ({ form, providerID }: IncomesEditFormFieldsProps) => {
  const { numberValue, handleNumberChange } = useNumberValue()
  const { data: productsData, isLoading: productsLoading } = api.useGetProvidersProductsQuery(providerID)
  const [postImage, setPostImage] = useState<PostImage>({
    myFile: ""
  })

  const { success: productsSuccess, form: productsForm, onSubmit: productsSubmit, pending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название товара" }),
      unit_type: z.string().optional(),
      price: z.string({ required_error: "Пожалуйста, введите цену товара" }),
      category: z.string({ required_error: "Пожалуйста, выберите категорию" }),
      image: z.string().optional(),
    },
    postImage.myFile !== '' && postImage.myFile !== undefined && postImage.myFile !== null ? {
      "image": postImage.myFile,
      "provider": providerID,
      "price": numberValue.replace(/\s/g, '')
    } : {
      "provider": providerID,
      "price": numberValue.replace(/\s/g, '')
    },
    'api/products/',
    ["Products"]
  )

  const handleFileUpload = async (e: any) => {
    const file = e.target.files[0]
    const base64 = await convertToBase64(file)
    setPostImage({ ...postImage, myFile: base64 })
  }

  return (
    <>
      <div className='flex items-end gap-2'>
        <ReactSelectFormField
          idData={productsData}
          isLoading={productsLoading}
          control={form.control}
          name="product"
          label="Выберите товар"
          placeholder="Выберите товар"
        />

        { !productsSuccess ? (
          <NewAddDialog
            pending={pending}
            form={productsForm}
            submit={productsSubmit}
            success={productsSuccess}
            successDesc='Новый товар успешно добавлен'
            btnText='Добавить новый товар'
            dialogTitle='Добавить новый товар'
            dialogDesc='Заполните все поля чтобы добавить новый товар'
          >
            <ProductsFormFields
              numberValue={numberValue}
              numberChange={handleNumberChange}
              inputValue={postImage.myFile}
              onChange={(e: any) => handleFileUpload(e)} form={productsForm}
            />
          </NewAddDialog>
        ) : null }
      </div>
    </>
  )
}

export default IncomesEditFormFields