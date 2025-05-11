import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {Input} from '@/components/ui/input.tsx'
import {HTMLInputAutoCompleteAttribute} from 'react'

interface InputFormFieldProps {
  control: any
  type: string
  name: string
  label?: string
  placeholder?: string
  _value?: string | number | any
  _onChange?: (e: any) => void
  autocomplete?: HTMLInputAutoCompleteAttribute | undefined
}

const InputFormField = ({ control, type, name, label, placeholder, _value, _onChange, autocomplete }: InputFormFieldProps) => {
  return (
    <FormField
      control={control}
      name={name}
      render={({field}) => (
        <FormItem className='w-full'>
          { label && <FormLabel>{label}</FormLabel> }
          <FormControl>
            <Input
              type={type}
              {...field}
              placeholder={placeholder}
              value={_value}
              onChange={(e: any) => {
                field.onChange(e)
                if (_onChange) {
                  _onChange(e)
                }
              }}
              autoComplete={autocomplete}
            />
          </FormControl>

          <FormMessage />
        </FormItem>
      )}
    />
  )
}

export default InputFormField