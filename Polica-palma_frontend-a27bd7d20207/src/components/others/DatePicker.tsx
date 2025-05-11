import {Popover, PopoverContent, PopoverTrigger} from '@/components/ui/popover.tsx'
import {Button} from '@/components/ui/button.tsx'
import {cn} from '@/lib/utils.ts'
import {format} from 'date-fns'
import {CalendarIcon} from 'lucide-react'
import {Calendar} from '@/components/ui/calendar.tsx'
import {FormField, FormItem, FormLabel} from "@/components/ui/form.tsx"

interface DatePickerProps {
  date?: any
  setDate?: any
  text: string
  isForm?: boolean
  control?: any
  name?: any
  label?: string | undefined
}

const DatePicker = ({ date, setDate, text, isForm, control, name, label }: DatePickerProps) => {
  return (
    <>
      { !isForm ? (
        <Popover>
          <PopoverTrigger asChild>
            <Button
              variant={"outline"}
              className={cn(
                "w-full pl-3 text-left font-normal",
                !date && "text-muted-foreground"
              )}
            >
              {date ? (
                format(date, "dd.MM.yyyy")
              ) : (
                <span>{text}</span>
              )}
              <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-auto p-0" align="start">
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              initialFocus
            />
          </PopoverContent>
        </Popover>
      ) : (
        <FormField
          control={control}
          name={name}
          render={({ field }) => (
            <FormItem className="w-full flex flex-col">
              { label && <FormLabel>{label}</FormLabel> }
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant={"outline"}
                    className={cn(
                      "w-full pl-3 text-left font-normal",
                      !field.value && "text-muted-foreground"
                    )}
                  >
                    {field.value ? (
                      format(field.value, "dd.MM.yyyy")
                    ) : (
                      <span>{text}</span>
                    )}
                    <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={field.value}
                    onSelect={field.onChange}
                    disabled={(date) => date > new Date()}
                    initialFocus
                  />
                </PopoverContent>
              </Popover>
            </FormItem>
          )}
        />
      ) }
    </>
  )
}

export default DatePicker