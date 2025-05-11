import {FormControl, FormField, FormItem, FormLabel} from '@/components/ui/form.tsx'
import {Checkbox} from '@/components/ui/checkbox.tsx'

interface CheckboxFormFieldProps {
  form: any
  name: string
  label: string
  _checked?: any
  _onCheckedChange?: (e: any) => void
}

const CheckboxFormField = ({ form, name, label, _checked, _onCheckedChange }: CheckboxFormFieldProps) => {
  return (
    <FormField
      control={form}
      name={name}
      render={({ field }) => (
        <>
          <FormItem className='flex items-center gap-2'>
            <FormControl>
              <Checkbox
                {...field}
                checked={_checked}
                onCheckedChange={(e: any) => {
                  if (_onCheckedChange) {
                    _onCheckedChange(e)
                  }
                  field.onChange(e)
                }}
              />
            </FormControl>

            <FormLabel style={{ marginTop: 0 }}>{label}</FormLabel>
          </FormItem>
        </>
      )}
    />
  )
}

export default CheckboxFormField