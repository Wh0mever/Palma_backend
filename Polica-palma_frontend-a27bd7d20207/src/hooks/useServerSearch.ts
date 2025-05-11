import {useState, useCallback, useEffect} from "react"

const useServerSearch = (setCurrentPage: any = undefined) => {
  const [searchValue, setSearchValue] = useState<string>('')
  const [submittedSearch, setSubmittedSearch] = useState<string>('')

  const handleSearch = useCallback((e: any) => {
    setSearchValue(e.target.value)
  }, [])

  const submitSearch = useCallback(() => {
    setSubmittedSearch(searchValue)
    setCurrentPage && setCurrentPage(1)
  }, [searchValue, setCurrentPage])

  useEffect(() => {
    if (searchValue === '') {
      setSubmittedSearch('')
    }
  }, [searchValue])

  useEffect(() => {
    window.addEventListener('keypress', (e: any) => {
      if (e.key === 'Enter') {
        setSubmittedSearch(searchValue)
        setCurrentPage && setCurrentPage(1)
      }
    })
  }, [searchValue])

  return { searchValue, handleSearch, submitSearch, submittedSearch }
}

export default useServerSearch