import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTrigger, DialogTitle} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Undo2} from 'lucide-react'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import {z} from 'zod'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import TextareaFormField from '@/components/others/TextareaFormField.tsx'
import useNumberValue from '@/hooks/useNumberValue.ts'

interface WriteOffDialogProps {
  warehouseProduct: string | number | undefined
}

const WriteOffDialog = ({ warehouseProduct }: WriteOffDialogProps) => {
  const { numberValue, handleNumberChange } = useNumberValue()
  const { success, form, onSubmit, pending } = useAxiosPost(
    {
      count: z.string({ required_error: "Пожалуйста, введите количество товара" }),
      comment: z.string({ required_error: "Пожалуйста, введите комментарий" }),
    },
    {
      "count": numberValue.replace(/\s/g, ''),
      "warehouse_product": warehouseProduct
    },
    `api/warehouse/write-offs/`,
    ["Warehouse", "WriteOffs"]
  )

  return (
    <>
      { !success ? (
        <Dialog>
          <DialogTrigger>
            <Button size='icon' variant='destructive'>
              <Undo2 className='w-4 h-4' />
            </Button>
          </DialogTrigger>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>Сделать списание</DialogTitle>
              <DialogDescription>Заполните нужные поля чтобы сделать списание товара со склада</DialogDescription>
            </DialogHeader>

            <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Товар успешно списан со склада'>
              <NumberFormField _value={numberValue} _onChange={handleNumberChange} control={form.control} name='count' label='Количество товара' />
              <TextareaFormField control={form.control} name='comment' label='Комментарий' />

              { pending ? (
                <Button className='mt-5' disabled>
                  Сделать списание
                </Button>
              ) : (
                <Button className='mt-5' type='submit'>
                  Сделать списание
                </Button>
              ) }
            </AddForm>
          </DialogContent>
        </Dialog>
      ) : null }
    </>
  )
}

export default WriteOffDialog