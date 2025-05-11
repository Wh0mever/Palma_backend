import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Undo2} from 'lucide-react'
import AddForm from '@/components/others/AddForm.tsx'
import useAxiosPost from '@/hooks/useAxiosPost.ts'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import useNumberValue from '@/hooks/useNumberValue.ts'
import {useEffect} from 'react'
import ErrorItem from '@/components/items/ErrorItem.tsx'

interface ReturnDialogProps {
  dialogTitle: string
  dialogDesc?: string
  schemaObject?: any
  url?: any
  isButtons?: boolean
  onClick?: () => void
  invalidatesTags: string[] | undefined
}

const ReturnDialog = ({ dialogTitle, dialogDesc, schemaObject = {}, url, isButtons, onClick, invalidatesTags }: ReturnDialogProps) => {
  const { numberValue, handleNumberChange, setNumberValue } = useNumberValue()
  const { form, onSubmit, success, pending, errorText, error } = useAxiosPost(
    schemaObject,
    {
      count: numberValue.replace(/\s/g, '')
    },
    url,
    invalidatesTags
  )

  useEffect(() => {
    if (success) {
      setNumberValue('')
    }
  }, [success, setNumberValue])

  return (
    <>
      { !isButtons ? (
        <Dialog>
          <DialogTrigger>
            <Button size='icon' variant='destructive'>
              <Undo2 className='w-4 h-4' />
            </Button>
          </DialogTrigger>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>{dialogTitle}</DialogTitle>
              <DialogDescription>{dialogDesc}</DialogDescription>
            </DialogHeader>

            { error && (
              <ErrorItem title='Ошибка' desc={errorText} />
            ) }

            <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Возврат сделан успешно'>
              <NumberFormField
                control={form.control}
                name='count'
                label='Введите количество'
                _value={numberValue}
                _onChange={handleNumberChange}
              />

              <Button type='submit' disabled={pending}>
                Сделать возврат
              </Button>
            </AddForm>
          </DialogContent>
        </Dialog>
      ) : null }

      { isButtons ? (
        <Dialog>
          <DialogTrigger>
            <Button size='icon' variant='destructive'>
              <Undo2 className='w-4 h-4' />
            </Button>
          </DialogTrigger>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>{dialogTitle}</DialogTitle>
              <DialogDescription>{dialogDesc}</DialogDescription>
            </DialogHeader>

            { error && (
              <ErrorItem title='Ошибка' desc={errorText} />
            ) }

            <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Возврат сделан успешно'>
              <div className='flex items-center gap-2'>
                <Button type='submit' variant='destructive' onClick={onClick} disabled={pending}>Да</Button>

                <DialogTrigger>
                  <Button type='button'>Нет</Button>
                </DialogTrigger>
              </div>
            </AddForm>
          </DialogContent>
        </Dialog>
      ) : null }
    </>
  )
}

export default ReturnDialog