import {IChildren} from '@/typing/interfaces.ts'

const CenterBlock = ({ children }: IChildren) => {
  return (
    <div className='w-full h-screen flex items-center justify-center'>
      {children}
    </div>
  )
}

export default CenterBlock