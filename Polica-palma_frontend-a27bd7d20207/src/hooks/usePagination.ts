import {useState} from 'react'

const usePagination = (initalFilterState: any = undefined) => {
  const [currentPage, setCurrentPage] = useState<number>(initalFilterState?.currentPage ? initalFilterState.currentPage : 1)
  const [totalPages, setTotalPages] = useState<number>(1)

  return { currentPage, setCurrentPage, totalPages, setTotalPages }
}

export default usePagination