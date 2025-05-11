import NumberMask from "../number-mask"
import { FormControl, FormField, FormItem, FormLabel, FormMessage } from "../ui/form"

interface InputFormFieldProps {
  control: any
  name: string
  label?: string
  placeholder?: string
  disabled?: boolean
  _value?: string | number | any
  _onChange?: (e: any) => void
}

const NumberFormField = ({ control, name, label, placeholder, _value, _onChange, disabled }: InputFormFieldProps) => {
  return (
    <FormField
      control={control}
      name={name}
      render={({field}) => (
        <FormItem className='w-full'>
          { label && <FormLabel>{label}</FormLabel> }
          <FormControl>
            <NumberMask
              {...field}
              name={name}
              placeholder={placeholder}
              value={_value}
              disabled={disabled}
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

export default NumberFormField