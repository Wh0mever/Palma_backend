import React from 'react'
import {Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger} from '../ui/dialog'
import { Button } from '../ui/button'
import { Plus } from 'lucide-react'
import AddForm from './AddForm'

interface NewAddDialogProps {
  form: any
  submit: (data: {}) => Promise<void>
  success: boolean
  successDesc: string
  children: React.ReactNode
  btnText: string
  dialogTitle: string
  dialogDesc: string
  pending?: boolean
}

const NewAddDialog = ({ form, submit, children, success, successDesc, btnText, dialogTitle, dialogDesc, pending }: NewAddDialogProps) => {
  return (
    <Dialog>
      <DialogTrigger>
        <Button size='icon' type='button' className='h-full'>
          <Plus className='w-4 h-4' />
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>{dialogDesc}</DialogDescription>
        </DialogHeader>

        <AddForm form={form} onSubmit={submit} success={success} successDesc={successDesc}>
          {children}

          <Button className='mt-5 h-full' disabled={pending}>
            {btnText}
          </Button>
        </AddForm>
      </DialogContent>
    </Dialog>
  )
}

export default NewAddDialog