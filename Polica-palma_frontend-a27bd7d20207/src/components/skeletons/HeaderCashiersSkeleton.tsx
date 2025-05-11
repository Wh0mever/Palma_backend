import {Skeleton} from '@/components/ui/skeleton.tsx'

const HeaderCashiersSkeleton = () => {
  return (
    <div className='mr-28 flex items-center gap-12'>
      <Skeleton className='w-44 h-8' />
    </div>
  )
}

export default HeaderCashiersSkeleton