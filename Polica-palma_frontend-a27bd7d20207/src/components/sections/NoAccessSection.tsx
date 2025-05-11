import CenterBlock from '@/components/blocks/CenterBlock.tsx'
import {Link} from 'react-router-dom'
import {Button} from '@/components/ui/button.tsx'
import {ArrowLeft} from 'lucide-react'

const NoAccessSection = () => {
  return (
    <>
      <CenterBlock>
        <div className='flex flex-col items-center gap-8'>
          <div className='flex flex-col items-center gap-4'>
            <h1 className='text-5xl font-bold text-neutral-900 dark:text-white'>У вас нет доступа к этой странице!</h1>
          </div>

          <Link to="/">
            <Button>
              <ArrowLeft className='w-4 h-4 mr-2'/> Вернуться на главную
            </Button>
          </Link>
        </div>
      </CenterBlock>
    </>
  )
}

export default NoAccessSection