import {AlertCircle} from 'lucide-react'
import {Alert, AlertDescription, AlertTitle} from '@/components/ui/alert.tsx'

interface ErrorItemProps {
  title: string
  desc: string | null | undefined
}

const ErrorItem = ({ title, desc }: ErrorItemProps) => {
  return (
    <Alert variant='destructive'>
      <AlertCircle className='w-4 h-4' />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{desc}</AlertDescription>
    </Alert>
  )
}

export default ErrorItem