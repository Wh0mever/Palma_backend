import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover.tsx'
import { Button } from '@/components/ui/button.tsx'
import { cn } from '@/lib/utils.ts'
import { format } from 'date-fns'
import { CalendarIcon } from 'lucide-react'
import { Calendar } from '@/components/ui/calendar.tsx'
import { Input } from "@/components/ui/input.tsx"

interface TimeDatePickerProps {
  date: any
  setDate: any
  text: string
  time?: any
  handleTimeChange?: any
}

const TimeDatePicker = ({ date, setDate, text, time, handleTimeChange }: TimeDatePickerProps) => {
  return (
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
            <>
              {format(date, "dd.MM.yyyy")} {time}
            </>
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
          onSelect={(newDate: any) => {
            setDate(newDate)
            if (time) {
              newDate.setHours(...time.split(':').map(Number))
              setDate(newDate)
            }
          }}
          initialFocus
        />
        <div className="p-2">
          <Input
            type="time"
            value={time}
            disabled={!date}
            onChange={handleTimeChange}
            className="w-full border border-gray-300 rounded-md p-2"
          />
        </div>
      </PopoverContent>
    </Popover>
  )
}

export default TimeDatePicker