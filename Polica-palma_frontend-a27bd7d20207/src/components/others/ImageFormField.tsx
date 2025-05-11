import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {Input} from '@/components/ui/input.tsx'

interface ImageFormFieldProps {
  form: any
  name: string
  label?: string
  placeholder?: string
  _value?: string | any
  _onChange?: (e: any) => void
}

const ImageFormField = ({ form, name, label, placeholder, _value, _onChange }: ImageFormFieldProps) => {
  return (
    <FormField
      control={form}
      name={name}
      render={({ field: { value, onChange } }) => (
        <FormItem className='w-full'>
          { label && <FormLabel>{label}</FormLabel> }
          <FormControl>
            <Input
              type='file'
              value={value}
              placeholder={placeholder}
              defaultValue={_value}
              onChange={(e: any) => {
              onChange(e)
              if (_onChange) {
                _onChange(e)
              }
            }}/>
          </FormControl>

          <FormMessage />
        </FormItem>
      )}
    />
  )
}

export default ImageFormField