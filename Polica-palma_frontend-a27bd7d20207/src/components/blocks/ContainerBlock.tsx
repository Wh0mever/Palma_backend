import {IChildren} from '@/typing/interfaces.ts'

const ContainerBlock = ({ children }: IChildren) => {
  return (
    <div className='max-w-[1880px] container mx-auto p-3'>
      {children}
    </div>
  )
}

export default ContainerBlock