import SearchItem from '@/components/items/SearchItem.tsx'

interface SectionsTopProps {
  title: string
  placeholder?: string
  inputValue: string
  onChange: (e: any) => void
  onClick: () => void
}

const SectionsTop = ({ title, placeholder, inputValue, onChange, onClick }: SectionsTopProps) => {
  return (
    <div className='w-full pb-5 flex items-center justify-center sm:justify-between border-b border-b-neutral-300 dark:border-b-neutral-800'>
      <div className='w-full flex flex-col sm:flex-row items-center gap-5 sm:gap-6'>
        <h1 className='text-3xl font-bold'>{title}</h1>
        { placeholder && (
          <SearchItem
            placeholder={placeholder}
            value={inputValue}
            onChange={onChange}
            onClick={onClick}
          />
        ) }
      </div>
    </div>
  )
}

export default SectionsTop