interface NumberMaskProps {
  value?: any
  onChange?: any
  placeholder?: string
  disabled?: boolean
  name?: any
}

const NumberMask = ({ value, onChange, placeholder, disabled, name }: NumberMaskProps) => {
  const formatNumber = (num: any) => {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ")
  }

  const removeFormatting = (str: any) => {
    return str.replace(/ /g, '')
  }

  const handleChange = (e: any) => {
    const inputValue = e.target.value
    const numericValue = removeFormatting(inputValue.replace(/[^\d.]/g, ''))
    onChange(formatNumber(numericValue))
  }

  return (
    <input
      className='flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-80'
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      disabled={disabled}
      name={name}
    />
  )
}

export default NumberMask