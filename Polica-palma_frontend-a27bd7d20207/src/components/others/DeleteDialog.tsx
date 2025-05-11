import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Trash2} from 'lucide-react'
import {api} from "@/services/api.ts"

interface DeleteDialogProps {
  id: string | number
  url: string
  item: string
  desc?: boolean
  hasCheck?: boolean
  invalidatesTags: string[]
}

const DeleteDialog = ({ item, desc, id, url, invalidatesTags }: DeleteDialogProps) => {
  const apiUrl: string = `/${url}/${id}/`
  const [deleteData, { isLoading }] = api.useDeleteDataMutation()

  const deleteItem = async () => {
    try {
      await deleteData({ url: apiUrl, invalidatesTags }).unwrap()
    } catch (e) {
      console.log('Delete error: ', e)
    }
  }

  return (
    <>
      <Dialog>
        <DialogTrigger>
          <Button size='icon' variant='destructive' title='Удалить'>
            <Trash2 className='w-4 h-4'/>
          </Button>
        </DialogTrigger>

        <DialogContent>
          <DialogHeader>
            <DialogTitle>Вы точно хотите удалить "{item}"?</DialogTitle>
            {desc && <DialogDescription>Все связанные элементы с "{item}" будут удалены!</DialogDescription>}
          </DialogHeader>

          <div className='mt-4 flex items-center gap-3'>
            <Button variant='destructive' disabled={isLoading} onClick={() => deleteItem()}>Удалить</Button>
            <DialogTrigger>
              <Button>Отмена</Button>
            </DialogTrigger>
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default DeleteDialog