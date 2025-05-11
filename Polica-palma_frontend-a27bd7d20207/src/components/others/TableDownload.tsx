import {Button} from '@/components/ui/button.tsx'
import {Download} from 'lucide-react'
import getUrl from '@/config.ts'
import getUserData from "@/helpers/getUserData.ts"

interface TableDownloadProps {
  apiUrl: string
  params?: any
  text?: string
  haventUserID?: boolean
}

const TableDownload = ({ apiUrl, params, text, haventUserID }: TableDownloadProps) => {
  const { userId } = getUserData()

  const downloadTable = () => {
    const baseUrl = `${getUrl()}/${apiUrl}${!haventUserID ? `/${userId}` : ''}`
    const queryString = params ? new URLSearchParams(params).toString() : null
    return `${baseUrl}${params ? `/?${queryString}` : ''}`
  }

  return (
    <div className='w-full flex justify-end'>
      <a href={`${downloadTable()}`} download target='_blank'>
        <Button>
          <Download className='w-4 h-4 mr-2'/> { text ? text : 'Скачать отчет' }
        </Button>
      </a>
    </div>
  )
}

export default TableDownload