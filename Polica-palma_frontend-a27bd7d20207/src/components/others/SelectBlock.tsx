import {Select, SelectContent, SelectGroup, SelectTrigger, SelectValue} from '@/components/ui/select.tsx'
import {Search} from 'lucide-react'
import {ScrollArea} from '@/components/ui/scroll-area.tsx'
import React, {useState} from 'react'

interface SelectBlockProps {
  placeholder: string
  children: React.ReactNode
  onValueChange: (e: any) => void
  defaultValue?: any
}

const SelectBlock = ({ placeholder, children, onValueChange, defaultValue }: SelectBlockProps) => {
  const [searchValue, setSearchValue] = useState<string>('')

  const filteredChildren = React.Children.toArray(children).filter((child) => {
    if (React.isValidElement(child)) {
      const childText = String(child.props.children)
      return childText.toLowerCase().includes(searchValue.toLowerCase())
    }

    return false
  })

  return (
    <>
      <Select onValueChange={onValueChange} defaultValue={defaultValue}>
        <SelectTrigger>
          <SelectValue placeholder={placeholder}/>
        </SelectTrigger>

        <SelectContent>
          <div className='w-full p-2 mb-2 flex items-center gap-2 bg-neutral-200 rounded-lg dark:bg-neutral-900'>
            <Search className='w-4 h-4'/>
            <input
              type="text"
              className='w-full p-1 outline-0 bg-transparent text-sm'
              placeholder='Поиск'
              onChange={(e: any) => setSearchValue(e.target.value)}
            />
          </div>

          <SelectGroup>
            {filteredChildren.length > 0 ? (
              <ScrollArea className='w-full max-h-[150px] overflow-y-auto'>
                {filteredChildren}
              </ScrollArea>
            ) : (
              <p className='text-sm text-neutral-500 dark:text-neutral-400'>Ничего не найдено</p>
            )}
          </SelectGroup>
        </SelectContent>
      </Select>
    </>
  )
}

export default SelectBlock