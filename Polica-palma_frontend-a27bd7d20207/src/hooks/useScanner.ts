import { useEffect, useState } from 'react'

const useScanner = () => {
  const [keyList, setKeyList] = useState<number[]>([])
  const [tempEnter, setTempEnter] = useState<boolean>(false)

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return
      }

      if (e.code === 'Enter' && tempEnter) {
        setTempEnter(false)
      }

      if (e.code.includes('Digit')) {
        setKeyList((prevKeyList) => [...prevKeyList, e.code.split('').pop() as any])
        setTempEnter(true)
      }
      setTimeout(() => setKeyList([]), 100)
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [tempEnter])

  return { keyList }
}

export default useScanner