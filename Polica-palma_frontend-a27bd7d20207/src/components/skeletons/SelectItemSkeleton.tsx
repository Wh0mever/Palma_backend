import {Skeleton} from '@/components/ui/skeleton.tsx'

const SelectItemSkeleton = () => {
  return (
    <div className='flex flex-col gap-1'>
      <Skeleton className='w-full h-4' />
      <Skeleton className='w-full h-4' />
      <Skeleton className='w-full h-4' />
    </div>
  )
}

export default SelectItemSkeleton