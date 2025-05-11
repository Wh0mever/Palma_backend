import {FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form.tsx"
import Select from "react-select"
import useNumberFormatter from "@/hooks/useNumberFormatter.ts"

interface ReactSelectFormFieldProps {
  isValue?: boolean
  valueData?: any[]
  idData?: any[]
  control: any
  name: string
  label?: string
  placeholder?: string
  isLoading?: boolean
  disabled?: boolean
  isClient?: boolean
}

const ReactSelectFormField = ({ isValue, valueData, idData, isLoading, control, name, label, placeholder, disabled, isClient }: ReactSelectFormFieldProps) => {
  const { formatter } = useNumberFormatter()

  return (
    <FormField
      control={control}
      name={name}
      render={({ field }) => (
        <FormItem className='w-full'>
          { label && <FormLabel>{label}</FormLabel> }
          <Select
            className='text-sm'
            defaultValue={field.value}
            isLoading={isLoading}
            isSearchable
            isClearable
            isDisabled={disabled}
            options={isValue ? valueData : idData}
            placeholder={placeholder}
            onChange={(option: any) => field.onChange(isValue ? option?.value : option?.id?.toString())}
            getOptionValue={!isValue ? (option: any) => option.id.toString() : (option: any) => option.value}
            getOptionLabel={!isValue ? (option: any) => option.name || option.first_name || `${option.full_name || option.username} | ${option.phone_number || '-'} ${isClient ? `| ${formatter.format(option.discount_percent)}%` : ''}` || option.username || option.title : (option: any) => option.label}
          />

          <FormMessage />
        </FormItem>
      )}
    />
  )
}

export default ReactSelectFormField