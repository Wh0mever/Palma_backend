import {Input} from "@/components/ui/input.tsx"
import {Button} from "@/components/ui/button.tsx"
import {Search} from "lucide-react"

interface SearchItemProps {
  placeholder?: string
  value: string
  onChange: (e: any) => void
  onClick?: (e: any) => void
  hasntBtn?: boolean
}

const SearchItem = ({ placeholder, onChange, onClick, hasntBtn }: SearchItemProps) => {
  return (
    <div className='w-full flex items-center gap-3'>
      <Input
        className={`w-full`}
        placeholder={placeholder}
        onChange={onChange}
      />

      { hasntBtn ? null : (
        <Button onClick={onClick}>
          <Search className='w-4 h-4 mr-2' /> Поиск
        </Button>
      ) }
    </div>
  )
}

export default SearchItem