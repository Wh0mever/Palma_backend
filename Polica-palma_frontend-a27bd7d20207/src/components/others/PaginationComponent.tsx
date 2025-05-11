/* eslint-disable @typescript-eslint/no-explicit-any */
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination.tsx'
import { useEffect } from 'react'
import { Button } from '@/components/ui/button.tsx'
import { ChevronsLeft, ChevronsRight } from 'lucide-react'

interface PaginationComponentProps {
  currentPage: number
  totalPages: number
  setCurrentPage: any
  setTotalPages: any
  data: any
  refetchData?: any
}

const PaginationComponent = ({ totalPages, currentPage, setCurrentPage, setTotalPages, data, refetchData }: PaginationComponentProps) => {
  useEffect(() => {
    setCurrentPage(currentPage)

    if (refetchData) {
      refetchData()
    }
  }, [currentPage])

  useEffect(() => {
    setTotalPages(data && data?.total_pages)
  }, [currentPage, data])

  useEffect(() => {
    if (!data) {
      setCurrentPage(1)
      refetchData()
    }
  }, [data])

  const handleFirstClick = () => setCurrentPage(1)
  const handleLastClick = () => setCurrentPage(totalPages)
  const handlePreviousClick = () => setCurrentPage((prevPage: any) => Math.max(prevPage - 1, 1))
  const handleNextClick = () => setCurrentPage((prevPage: any) => Math.min(prevPage + 1, totalPages))

  const renderPaginationItems = () => {
    const pages = []

    if (totalPages <= 5) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(
          <PaginationItem key={i}>
            <PaginationLink
              className="cursor-pointer"
              isActive={currentPage === i}
              onClick={() => setCurrentPage(i)}
            >{i}</PaginationLink>
          </PaginationItem>
        )
      }
    } else {
      let startPage = 1
      let endPage = 5

      if (currentPage > 3) {
        startPage = currentPage - 2
        endPage = currentPage + 2
      }

      if (endPage > totalPages) {
        startPage = totalPages - 4
        endPage = totalPages
      }

      for (let i = startPage; i <= endPage; i++) {
        pages.push(
          <PaginationItem key={i}>
            <PaginationLink
              className="cursor-pointer"
              isActive={currentPage === i}
              onClick={() => setCurrentPage(i)}
            >
              {i}
            </PaginationLink>
          </PaginationItem>
        )
      }

      if (endPage < totalPages) {
        pages.push(
          <PaginationItem key="ellipsis" className="disabled">
            <PaginationEllipsis />
          </PaginationItem>
        )

        pages.push(
          <PaginationItem key={totalPages}>
            <PaginationLink
              className="cursor-pointer"
              isActive={currentPage === totalPages}
              onClick={() => setCurrentPage(totalPages)}
            >
              {totalPages}
            </PaginationLink>
          </PaginationItem>
        );
      }
    }
    return pages
  }

  return (
    <>
      <Pagination className="mt-2 mb-4">
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious className="cursor-pointer" onClick={handlePreviousClick} />
          </PaginationItem>

          <PaginationItem>
            <Button size="icon" variant="outline" onClick={handleFirstClick}>
              <ChevronsLeft className="w-4 h-4" />
            </Button>
          </PaginationItem>

          {renderPaginationItems()}

          <PaginationItem>
            <Button size="icon" variant="outline" onClick={handleLastClick}>
              <ChevronsRight className="w-4 h-4" />
            </Button>
          </PaginationItem>

          <PaginationItem>
            <PaginationNext className="cursor-pointer" onClick={handleNextClick} />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </>
  )
}

export default PaginationComponent