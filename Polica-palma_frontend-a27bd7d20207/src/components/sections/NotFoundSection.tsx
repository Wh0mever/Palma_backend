import {Button} from '@/components/ui/button.tsx'
import {ArrowLeft} from 'lucide-react'
import {Link} from 'react-router-dom'
import CenterBlock from '@/components/blocks/CenterBlock.tsx'

const NotFoundSection = () => {
  return (
    <>
      <CenterBlock>
        <div className='flex flex-col items-center gap-8'>
          <div className='flex flex-col items-center gap-4'>
            <h1 className='text-9xl font-semibold text-neutral-900 dark:text-white'>404</h1>
            <p className='text-2xl font-medium text-neutral-700 dark:text-neutral-300'>Страница не найдена!</p>
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

export default NotFoundSection