import React from 'react'
import {Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Pencil} from 'lucide-react'
import AddForm from '@/components/others/AddForm.tsx'

interface EditDialogProps {
  dialogTitle: string
  form: any
  submit: any
  success: boolean
  successDesc: string
  onClick?: () => void
  children: React.ReactNode
  btnVariant?: 'link' | 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | null | undefined
  btnClassname?: string
  pending?: boolean
}

const EditDialog = ({ dialogTitle, form, submit, success, successDesc, onClick, children, btnVariant, btnClassname, pending }: EditDialogProps) => {
  return (
    <>
      { !success ? (
        <Dialog>
          <DialogTrigger>
            <Button size='icon' className={btnClassname} variant={btnVariant} title='Редактировать'>
              <Pencil className='w-4 h-4'/>
            </Button>
          </DialogTrigger>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>{dialogTitle}</DialogTitle>
            </DialogHeader>

            <AddForm form={form} onSubmit={submit} success={success} successDesc={successDesc}>
              {children}
              <Button type='submit' onClick={onClick} disabled={pending}>Изменить</Button>
            </AddForm>
          </DialogContent>
        </Dialog>
      ) : null }
    </>
  )
}

export default EditDialog