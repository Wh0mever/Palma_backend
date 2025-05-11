import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger
} from '@/components/ui/dialog.tsx'
import {Button} from '@/components/ui/button.tsx'
import {Plus} from 'lucide-react'
import React from 'react'

interface AddDialogProps {
  children: React.ReactNode
  btnText: string
  dialogTitle: string
  dialogDesc: string
}

const AddDialog = ({ children, btnText, dialogTitle, dialogDesc }: AddDialogProps) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>
          <Plus className='w-4 h-4 mr-2' /> {btnText}
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle>{dialogTitle}</DialogTitle>
          <DialogDescription>{dialogDesc}</DialogDescription>
        </DialogHeader>

        {children}
      </DialogContent>
    </Dialog>
  )
}

export default AddDialog