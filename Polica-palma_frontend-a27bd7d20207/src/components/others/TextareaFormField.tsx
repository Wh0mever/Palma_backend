import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {Textarea} from '@/components/ui/textarea.tsx'

interface TextareaFormFieldProps {
  control: any
  name: string
  label: string
  _value?: string | number | any
  _onChange?: (e: any) => void
}

const TextareaFormField = ({ control, name, label, _value, _onChange }: TextareaFormFieldProps) => {
  return (
    <FormField
      control={control}
      name={name}
      render={({field}) => (
        <FormItem>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Textarea
              {...field}
              value={_value}
              onChange={(e: any) => {
                field.onChange(e)
                if (_onChange) {
                  _onChange(e)
                }
              }}
            />
          </FormControl>

          <FormMessage />
        </FormItem>
      )}
    />
  )
}

export default TextareaFormField