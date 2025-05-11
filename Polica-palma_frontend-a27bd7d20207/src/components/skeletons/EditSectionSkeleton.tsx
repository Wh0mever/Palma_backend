import {Skeleton} from '@/components/ui/skeleton.tsx'

const EditSectionSkeleton = () => {
  return (
    <>
      <div className='w-full flex flex-col gap-8'>
        <Skeleton className='w-48 h-10 rounded-lg' />
        <Skeleton className='w-64 h-8 rounded-lg' />
        <div className='flex flex-col gap-3'>
          <Skeleton className='w-full h-10 rounded-lg' />
          <Skeleton className='w-full h-10 rounded-lg' />
        </div>
      </div>
    </>
  )
}

export default EditSectionSkeleton