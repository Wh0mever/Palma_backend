/* eslint-disable @typescript-eslint/no-explicit-any */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import noImage from '@/assets/no-image.png'
import DashboardLayout from '@/components/elements/DashboardLayout.tsx'
import {useParams} from 'react-router-dom'
import InputFormField from '@/components/others/InputFormField.tsx'
import EditSection from '@/components/sections/EditSection.tsx'
import {z} from 'zod'
import {useState} from 'react'
import useAxiosPut from '@/hooks/useAxiosPut.ts'
import ImageFormField from '@/components/others/ImageFormField.tsx'
import useValues from '@/hooks/useValues.ts'
import convertToBase64 from '@/helpers/convertToBase64.ts'
import NumberFormField from '@/components/others/NumberFormField'
import EditSectionSkeleton from '@/components/skeletons/EditSectionSkeleton.tsx'
import translatedData from '@/data/translatedData.ts'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Plus, Trash2} from 'lucide-react'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import AddForm from '@/components/others/AddForm.tsx'
import axios from 'axios'
import getUrl from '@/config.ts'
import getAuthorizationHeader from '@/helpers/getAuthHeader.ts'
import getUserData from '@/helpers/getUserData.ts'
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx"
import {api} from "@/services/api.ts"

interface PostImage {
  myFile: string | any
}

const ProductsEditPage = () => {
  const { id } = useParams()
  const { userType } = getUserData()
  const { data, isLoading, refetch } = api.useGetProductsQuery({ id: id })
  const { data: providersData, isLoading: providersLoading } = api.useGetProvidersQuery('')
  const { data: optionsData, isLoading: optionsLoading } = api.useGetProductsOptionsQuery('')
  const { data: categoriesData, isLoading: categoriesLoading } = api.useGetCategoriesQuery('')
  const [postImage, setPostImage] = useState<PostImage>({
    myFile: ""
  })

  const { inputValues, handleInputChange } = useValues(
    {
      name: '',
      price: '',
    },
    {
      name: data && data?.name || '',
      price: data && data?.price || '',
    },
    isLoading,
    data
  )

  const { success, form, onSubmit } = useAxiosPut(
    {
      name: z.string().optional(),
      unit_type: z.string().optional(),
      price: z.string().optional(),
      category: z.string().optional(),
      image: z.string().optional(),
    },
    postImage.myFile !== '' && postImage.myFile !== undefined && postImage.myFile !== null ? {
      "price": inputValues.price !== '' ? String(inputValues.price).replace(/\s/g, '') : '',
      "image": postImage.myFile
    } : {
      "price": inputValues.price !== '' ? String(inputValues.price).replace(/\s/g, '') : '',
    },
    'api/products',
    id,
    ["Products"]
  )

  const { form: addProviderForm, onSubmit: addProviderSubmit, success: addProviderSuccess, pending: addProviderPending } = useAxiosPost(
    {
      provider: z.string({ required_error: 'Пожалуйста, выберите поставщика' }),
    },
    {},
    `api/products/${id}/add-provider/`,
    ["Products"]
  )

  const removeProvider = async (providerID: string) => {
    try {
      const response = await axios.post(`${getUrl()}/api/products/${id}/remove-provider/`, {
        "provider": providerID
      }, {
        headers: {
          Authorization: getAuthorizationHeader()
        }
      })

      if (response.status === 200 || response.status === 201 || response.status === 204) {
        if (refetch) {
          refetch()
        }
      }
    } catch (e) {
      console.log('Remove error: ', e)
    }
  }

  async function handleFileUpload(e: any) {
    const file = e.target.files[0]
    const base64 = await convertToBase64(file)
    setPostImage({ ...postImage, myFile: base64 })
  }

  return (
    <>
      <DashboardLayout>
        { !isLoading && data ? (
          <EditSection form={form} onSubmit={onSubmit} success={success}>
            { userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' && (
              <>
                <InputFormField
                  control={form.control}
                  type='text'
                  name='name'
                  label='Введите новое название товара'
                  _value={inputValues.name}
                  _onChange={(e: any) => handleInputChange('name', e.target.value)}
                />
                <ReactSelectFormField
                  isValue
                  valueData={optionsData}
                  isLoading={optionsLoading}
                  control={form.control}
                  name='unit_type'
                  label='Единица измерения'
                  placeholder={translatedData(data?.unit_type)}
                />
                <NumberFormField
                  control={form.control}
                  name='price'
                  label='Введите новую цену продажи'
                  _value={inputValues.price}
                  _onChange={(e: any) => handleInputChange('price', e)}
                />
                <ReactSelectFormField
                  idData={categoriesData}
                  isLoading={categoriesLoading}
                  control={form.control}
                  name='category'
                  label='Категория'
                  placeholder={data?.category?.name}
                />

                <div className='w-full flex items-center justify-between'>
                  <div className='flex items-center gap-2 text-xl'>
                    <h3 className='font-medium'>Поставщики:</h3>
                    <div className='flex items-center gap-2'>
                      { data && data?.related_providers && Array.isArray(data?.related_providers) && data?.related_providers.map((item: any) => (
                        <div key={item.id} className='px-4 py-2 flex items-center gap-2 text-base font-semibold bg-neutral-100 rounded-lg'>
                          <p>{item.full_name}</p>
                          <Button size='icon' variant='outline' onClick={() => removeProvider(item.id)}>
                            <Trash2 className='w-4 h-4' />
                          </Button>
                        </div>
                      ))}

                      { data && data?.related_providers && Array.isArray(data?.related_providers) && data?.related_providers.length === 0 &&
                        <p className="text-lg font-semibold">- Поставщиков нет -</p> }
                    </div>
                  </div>

                  <Dialog>
                    <DialogTrigger>
                      <Button>
                        <Plus className='mr-2 w-4 h-4' /> Добавить поставщика
                      </Button>
                    </DialogTrigger>

                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Добавить поставщика</DialogTitle>
                      </DialogHeader>

                      <AddForm form={addProviderForm} onSubmit={addProviderSubmit} success={addProviderSuccess} successDesc='Поставщик успешно добавлен'>
                        <ReactSelectFormField
                          idData={providersData}
                          isLoading={providersLoading}
                          control={addProviderForm.control}
                          name='provider'
                          placeholder='Выберите поставщика'
                          label='Поставщик'
                        />

                        <Button type='submit' disabled={addProviderPending}>Добавить поставщика</Button>
                      </AddForm>
                    </DialogContent>
                  </Dialog>
                </div>
              </>
            ) }

            <ImageFormField
              form={form.control}
              name='image'
              label='Изображение'
              _value={postImage.myFile}
              _onChange={(e: any) => handleFileUpload(e)}
            />

            <div
              style={{
                width: 150,
                height: 150,
                borderRadius: 10,
                cursor: 'pointer',
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                backgroundRepeat: 'no-repeat',
                backgroundImage: `url(${data && data?.image || noImage})`
              }}
            />
          </EditSection>
        ) : (
          <EditSectionSkeleton />
        )}
      </DashboardLayout>
    </>
  )
}

export default ProductsEditPage