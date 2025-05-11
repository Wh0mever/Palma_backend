import {FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form.tsx'
import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover.tsx'
import {Button} from '@/components/ui/button.tsx'
import {cn} from '@/lib/utils.ts'
import {format} from 'date-fns'
import {CalendarIcon} from 'lucide-react'
import {Calendar} from '@/components/ui/calendar.tsx'

interface CalendarFormFieldProps {
  form: any
  name: string
  label?: string
  text?: string
}

const CalendarFormField = ({ form, name, label, text }: CalendarFormFieldProps) => {
  return (
    <FormField
      control={form}
      name={name}
      render={({ field }) => (
        <FormItem className="flex flex-col">
          { label && <FormLabel>{label}</FormLabel> }
          <Popover>
            <PopoverTrigger asChild>
              <FormControl>
                <Button
                  variant={"outline"}
                  className={cn(
                    "w-[240px] pl-3 text-left font-normal",
                    !field.value && "text-muted-foreground"
                  )}
                >
                  {field.value ? (
                    format(field.value, "PPP")
                  ) : (
                    <span>{text}</span>
                  )}
                  <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                </Button>
              </FormControl>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={field.value}
                onSelect={field.onChange}
                initialFocus
              />
            </PopoverContent>
          </Popover>

          <FormMessage />
        </FormItem>
      )}
    />
  )
}

export default CalendarFormField