import Sidebar from '@/components/widgets/Sidebar.tsx'
import {IChildren} from '@/typing/interfaces.ts'
import Header from '@/components/widgets/Header.tsx'
import {useEffect, useState} from 'react'
import {useNavigate} from 'react-router-dom'
import getUserData from '@/helpers/getUserData.ts'
import {Toaster} from "@/components/ui/toaster.tsx"

const notPermitted = {
  'ADMIN': [],
  'CASHIER': [],
  'INCOME_MANAGER': [[/dashboard\/payment*/g, false]],
  'FLORIST': [[/dashboard\/payment*/g, false]],
  'FLORIST_PERCENT': [[/dashboard\/payment*/g, false]],
  'MANAGER': [[/dashboard\/payment*/g, false]],
  'SALESMAN': [[/dashboard\/payment*/g, false]],
  'NO_BONUS_SALESMAN': [[/dashboard\/payment*/g, false]],
  'WAREHOUSE_MASTER': [[/dashboard\/payment*/g, false]],
  'CRAFTER': [[/dashboard\/payment*/g, false]],
}

const DashboardLayout = ({ children }: IChildren) => {
  const navigate = useNavigate()
  const storedSidebarState = localStorage.getItem('isSidebarOpen')
  const initialSidebarState = storedSidebarState ? JSON.parse(storedSidebarState) : true
  const [isSidebarOpen, setIsSidebarOpen] = useState(initialSidebarState)
  const { userLogin, userPassword, userType } = getUserData()

  useEffect(() => {
    const isAuthPage = window.location.pathname.match(/auth\/*/g)
    const isHomePage = window.location.pathname === '/'

    if (isAuthPage || isHomePage) return

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    if (notPermitted[userType] === undefined || notPermitted[userType] === 'all') {
      navigate('/noaccess')
      return
    }

    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-expect-error
    const permissions = notPermitted[userType]

    if (Array.isArray(permissions)) {
      const isNotAllowed = permissions.some(([regPer, regType]) => {
        const isMatch = window.location.pathname.match(regPer)
        return regType ? !isMatch : isMatch
      })

      if (isNotAllowed) {
        navigate('/noaccess')
      }
    }
  }, [navigate, userType])

  useEffect(() => {
    if (userLogin === null && userPassword === null && userType === null && window.location.pathname !== '/auth/login') {
      localStorage.clear()
      navigate('/auth/login')
    }
  }, [userLogin, userPassword, userType, navigate])

  useEffect(() => {
    localStorage.setItem('isSidebarOpen', JSON.stringify(isSidebarOpen))
  }, [isSidebarOpen])

  const handleSidebar = () => setIsSidebarOpen((prevState: never) => !prevState)

  return (
    <>
      <div className='flex h-screen'>
        { isSidebarOpen && <Sidebar onClick={handleSidebar}/> }

        <div className='w-full flex flex-col'>
          <Header onClick={handleSidebar} />

          <div className='w-full flex flex-grow overflow-y-auto p-6'>
            {children}
          </div>
        </div>

        <Toaster />
      </div>
    </>
  )
}

export default DashboardLayout