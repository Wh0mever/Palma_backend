import {Skeleton} from '@/components/ui/skeleton.tsx'

const ProductsSkeleton = () => {
  return (
    <>
      <Skeleton className='w-full h-[240px]' />
      <Skeleton className='w-full h-[240px]' />
      <Skeleton className='w-full h-[240px]' />
    </>
  )
}

export default ProductsSkeleton