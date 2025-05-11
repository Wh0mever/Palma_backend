import {Skeleton} from '@/components/ui/skeleton.tsx'

const CategoriesSkeleton = () => {
  return (
    <div className='flex items-center gap-5'>
      <Skeleton className='w-40 h-10' />
      <Skeleton className='w-40 h-10' />
      <Skeleton className='w-40 h-10' />
      <Skeleton className='w-40 h-10' />
    </div>
  )
}

export default CategoriesSkeleton