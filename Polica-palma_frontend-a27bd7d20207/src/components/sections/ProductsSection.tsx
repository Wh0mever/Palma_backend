/* eslint-disable @typescript-eslint/no-explicit-any */
import {Button} from '@/components/ui/button.tsx'
import {useEffect, useState} from 'react'
import SectionsTop from '@/components/others/SectionsTop.tsx'
import {z} from 'zod'
import AddDialog from '@/components/others/AddDialog.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import convertToBase64 from '@/helpers/convertToBase64.ts'
import ProductsTable from '@/components/tables/elements/ProductsTable.tsx'
import ProductsFormFields from '@/components/forms/ProductsFormFields.tsx'
import useNumberValue from '@/hooks/useNumberValue'
import SectionTableSkeleton from '@/components/skeletons/SectionTableSkeleton.tsx'
import CategoriesSkeleton from '@/components/skeletons/CategoriesSkeleton.tsx'
import usePagination from '@/hooks/usePagination.ts'
import PaginationComponent from '@/components/others/PaginationComponent.tsx'
import getUserData from '@/helpers/getUserData.ts'
import {api} from "@/services/api.ts"
import useQueryString from "@/hooks/useQueryString.ts"

interface PostImage {
  myFile: string | any
}

const ProductsSection = () => {
  const { userType } = getUserData()
  const { currentPage, setCurrentPage, totalPages, setTotalPages } = usePagination()
  const [selectedCategory, setSelectedCategory] = useState(null)
  const [searchValue, setSearchValue] = useState<string>('')
  const [postImage, setPostImage] = useState<PostImage>({ myFile: "" })
  const { numberValue, handleNumberChange } = useNumberValue()

  const queryParams = {
    'page': currentPage,
    'search': searchValue,
    'category': selectedCategory !== null ? selectedCategory : '',
  }

  const { queryString: queryStringCollection } = useQueryString(queryParams)
  const [queryString, setQueryString] = useState('')
  const { data: categoriesData, isLoading: categoriesLoading } = api.useGetCategoriesQuery('')
  const { data: productsData, isLoading: productsLoading, isFetching: productsFetching, isError: productsError } = api.useGetProductsQuery({ params: queryString })

  const { success, form, onSubmit, pending } = useAxiosPost(
    {
      name: z.string({ required_error: "Пожалуйста, введите название товара" }),
      unit_type: z.string().optional(),
      price: z.string({ required_error: "Пожалуйста, введите цену товара" }),
      category: z.string({ required_error: "Пожалуйста, выберите категорию" }),
      image: z.string().optional(),
    },
    postImage.myFile !== '' && postImage.myFile !== undefined && postImage.myFile !== null ? {
      "price": numberValue.replace(/\s/g, ''),
      "image": postImage.myFile
    } : {
      "price": numberValue.replace(/\s/g, ''),
    },
    'api/products/',
    ["Products"]
  )

  useEffect(() => {
    if (success) {
      setPostImage({
        ...postImage,
        myFile: ''
      })
    }
  }, [success, postImage])

  const handleSearch = (e: any) => {
    setSearchValue(e.target.value)
  }

  const applySearch = () => {
    if (searchValue.trim() === '') {
      setQueryString(queryStringCollection)
    } else {
      setQueryString(queryStringCollection)
    }
  }

  useEffect(() => {
    if (searchValue.trim() === '') {
      setQueryString(queryStringCollection)
    }
  }, [searchValue, queryStringCollection])

  useEffect(() => {
    window.addEventListener('keypress', (e: any) => {
      if (e.key === 'Enter') {
        setQueryString(queryStringCollection)
      }
    })
  }, [searchValue])

  const handleFileUpload = async (e: any) => {
    const file = e.target.files[0]
    const base64 = await convertToBase64(file)
    setPostImage({ ...postImage, myFile: base64 })
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const filteredProducts = productsData && productsData?.results && Array.isArray(productsData?.results) && productsData?.results.filter((item: any) => {
    return selectedCategory ? item.category?.id === selectedCategory : true
  })

  return (
    <>
      { productsLoading ? (
        <SectionTableSkeleton />
      ) : (
        <section className='w-full h-screen flex flex-col gap-8'>
          <SectionsTop
            title='Товары'
            placeholder='Поиск товара'
            inputValue={searchValue}
            onChange={handleSearch}
            onClick={applySearch}
          />

          <div className="w-full h-full relative flex flex-col gap-5">
            <div className='z-40 sticky -top-6 pt-4 pb-4 flex flex-col sm:flex-row items-center justify-between gap-5 bg-white dark:bg-neutral-950'>
              <div className='w-full pb-2 max-w-[900px] flex items-center gap-1 overflow-x-auto'>
                { categoriesLoading ? (
                  <CategoriesSkeleton />
                ) : (
                  <>
                    <Button
                      onClick={() => setSelectedCategory(null)}
                      className={selectedCategory === null ? 'bg-neutral-600 dark:bg-neutral-300' : ''}
                    >Все товары</Button>

                    {categoriesData && Array.isArray(categoriesData) && categoriesData.map(item => (
                      <Button
                        key={item.id}
                        onClick={() => setSelectedCategory(item.id)}
                        className={selectedCategory === item.id ? 'bg-neutral-600 dark:bg-neutral-300' : ''}
                      >{item.name}</Button>)
                    )}
                  </>
                ) }
              </div>

              {!success && userType !== 'FLORIST' && userType !== 'FLORIST_PERCENT' && userType !== 'SALESMAN' ? (
                <AddDialog btnText='Добавить товар' dialogTitle='Добавить товар' dialogDesc='Заполните все поля чтобы добавить товар'>
                  <AddForm
                    form={form}
                    onSubmit={onSubmit}
                    success={success}
                    successDesc='Новый товар успешно добавлен'
                  >
                    <ProductsFormFields
                      inputValue={postImage.myFile}
                      onChange={(e: any) => handleFileUpload(e)}
                      form={form}
                      numberValue={numberValue}
                      numberChange={handleNumberChange}
                    />

                    <Button className='mt-5' disabled={pending}>Добавить товар</Button>
                  </AddForm>
                </AddDialog>
              ) : null}
            </div>

            <div className='w-full h-full relative flex flex-col gap-3'>
              { !productsFetching ? (
                <ProductsTable data={filteredProducts} />
              ) : (
                <SectionTableSkeleton />
              )  }

              <PaginationComponent
                data={!productsError && productsData}
                currentPage={currentPage}
                totalPages={totalPages}
                setCurrentPage={setCurrentPage}
                setTotalPages={setTotalPages}
                refetchData={() => setQueryString(queryStringCollection)}
              />
            </div>
          </div>
        </section>
      )}
    </>
  )
}

export default ProductsSection