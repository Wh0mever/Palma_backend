import {Button} from '@/components/ui/button.tsx'
import {CircleDollarSign} from 'lucide-react'
import NumberFormField from '@/components/others/NumberFormField.tsx'
import React from 'react'

interface OrderCompleteItemProps {
  form: any
  name: string
  label?: string
  value?: string | number
  onChange?: (e: any) => void
  onClick?: () => void
}

const OrderCompleteItem = ({ form, name, label, value, onChange, onClick }: OrderCompleteItemProps) => {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (onChange) {
      onChange(e)
    }
  }

  return (
    <div className="w-full flex items-end gap-2">
      <NumberFormField
        control={form.control}
        name={name}
        label={label}
        _value={value}
        _onChange={handleChange}
      />
      <Button size="icon" type='button' onClick={onClick}>
        <CircleDollarSign className="w-4 h-4"/>
      </Button>
    </div>
  )
}

export default OrderCompleteItem