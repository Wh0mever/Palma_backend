import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {Input} from '@/components/ui/input.tsx'

interface OrdersFormFieldProps {
  control: any
  name: string
  label?: string
  type: string
  _value?: string | number | any
  _onChange?: (e: any) => void
}

const OrdersFormField = ({ control, name, label, type, _value, _onChange }: OrdersFormFieldProps) => {
  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className='w-full'>
          <FormLabel>{label}</FormLabel>
          <FormControl>
            <Input
              type={type}
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

export default OrdersFormField