import {Button} from '@/components/ui/button.tsx'
import {Eye, Pencil} from 'lucide-react'
import {Link} from 'react-router-dom'

interface EditItemProps {
  link: string
  isEye?: boolean
}

const EditItem = ({ link, isEye }: EditItemProps) => {
  return (
    <Link to={link}>
      <Button size='icon' title='Редактировать'>
        { isEye ? (
          <Eye className='w-4 h-4'/>
          ) : (
          <Pencil className='w-4 h-4'/>
        ) }
      </Button>
    </Link>
  )
}

export default EditItem