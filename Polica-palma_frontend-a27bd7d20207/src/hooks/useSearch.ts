import {ChangeEvent, useEffect, useState} from "react"

interface SearchHook<T> {
  filteredData: T[]
  searchTerm: string
  handleSearchChange: (e: ChangeEvent<HTMLInputElement>) => void
  handleSearch: () => void
}

const useSearch = <T extends Record<string, any>>(initialData: T[], searchKey: keyof T): SearchHook<T> => {
  const [filteredData, setFilteredData] = useState<T[]>(initialData)
  const [searchTerm, setSearchTerm] = useState<string>('')

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value)
  }

  const handleSearch = () => {
    if (!searchTerm) {
      setFilteredData(initialData)
      return
    }

    const filtered = initialData.filter(item =>
      String(item[searchKey]).toLowerCase().includes(searchTerm.toLowerCase())
    )

    setFilteredData(filtered)
  }

  useEffect(() => {
    if (searchTerm === '') {
      setFilteredData(initialData)
    }
  }, [searchTerm])

  useEffect(() => {
    window.addEventListener('keypress', (e: any) => {
      if (e.key === 'Enter') {
        handleSearch()
      }
    })
  }, [searchTerm])

  return { filteredData: Array.isArray(filteredData) ? filteredData : initialData, searchTerm, handleSearchChange, handleSearch }
}

export default useSearch