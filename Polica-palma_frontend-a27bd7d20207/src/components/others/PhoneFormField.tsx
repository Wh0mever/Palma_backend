import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {PhoneInput} from '@/components/phone-input.tsx'

interface PhoneFormFieldProps {
  control: any
  name: string
  label: string
  _value?: string | number | any
  _onChange?: (e: any) => void
}

const PhoneFormField = ({ control, name, label, _value, _onChange }: PhoneFormFieldProps) => {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className="flex flex-col items-start">
          <FormLabel className="text-left">{label}</FormLabel>
          <FormControl className="w-full">
            <PhoneInput
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

export default PhoneFormField