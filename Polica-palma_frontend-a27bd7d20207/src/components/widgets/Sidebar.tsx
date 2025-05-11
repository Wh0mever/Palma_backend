import Logo from '@/components/ui/Logo.tsx'
import {Link, To, useLocation} from 'react-router-dom'
import getSidebarData from '@/data/sidebarData.tsx'
import {ChevronDown, ChevronUp, X} from 'lucide-react'
import {Button} from '@/components/ui/button.tsx'
import {JSXElementConstructor, Key, ReactElement, ReactNode, ReactPortal, useEffect, useState} from 'react'

interface SidebarProps {
  onClick: () => void
}

const Sidebar = ({onClick}: SidebarProps) => {
  const location = useLocation()
  const [openIndex, setOpenIndex] = useState(-1)
  const {sidebarData} = getSidebarData()

  useEffect(() => {
    const storedIndex = localStorage.getItem('sidebarOpenIndex')
    if (storedIndex !== null) {
      setOpenIndex(parseInt(storedIndex))
    }
  }, [])

  const handleItemClick = (index: any) => {
    setOpenIndex((prevIndex: any) => (prevIndex === index ? -1 : index))
    localStorage.setItem('sidebarOpenIndex', index.toString())
  }

  return (
    <aside className="max-[1620px]:fixed top-0 left-0 z-50 relative w-72 h-screen p-4 flex flex-col gap-6 bg-white border-r border-r-neutral-300 overflow-auto dark:bg-neutral-950 dark:border-r-neutral-800">
      <div className="w-full pt-2 pb-6 flex justify-center border-b border-b-neutral-300 dark:border-b-neutral-800">
        <div className="flex items-center gap-8">
          <Link to="/">
            <Logo/>
          </Link>

          <Button size="icon" onClick={onClick} className="max-[1620px]:flex hidden">
            <X className="w-4 h-4"/>
          </Button>
        </div>
      </div>

      <div className="flex flex-col gap-5">
        <h3 className="text-xl font-semibold text-neutral-900 dark:text-white">Главная</h3>

        <nav className="flex flex-col gap-3">
          {sidebarData.map((item, index) => (
            <>
              { item.icon === undefined || item.title === undefined ? null : (
                <div key={index}>
                  <div
                    className="w-full p-4 flex items-center justify-between gap-5 bg-neutral-200 rounded-lg select-none cursor-pointer dark:bg-neutral-900"
                    onClick={() => handleItemClick(index)}
                  >
                    <div className="flex items-center gap-3">
                      <div>{item.icon}</div>
                      <p className="text-sm font-semibold">{item.title}</p>
                    </div>
                    {openIndex !== index ? <ChevronDown className="w-4 h-4"/> : <ChevronUp className="w-4 h-4"/>}
                  </div>
                  {openIndex === index && (
                    <div className="mt-3 p-2 flex flex-col gap-2 bg-neutral-200 rounded-lg dark:bg-neutral-900">
                      {openIndex === index && item.subNavItems?.map((item: {
                        link: To;
                        text: string | number | boolean | ReactElement<any, string | JSXElementConstructor<any>> | Iterable<ReactNode> | ReactPortal | null | undefined
                      }, index: Key | null | undefined) => (
                        <>
                          {item.link === undefined || item.text === undefined ? null : (
                            <Link key={index} to={item.link}>
                              <p
                                className={`px-4 py-2 rounded-md text-sm font-medium transition duration-300 hover:bg-neutral-800 hover:text-white ${
                                  location.pathname === item.link ? 'bg-neutral-800 text-white' : ''
                                }`}
                              >
                                {item.text}
                              </p>
                            </Link>
                          )}
                        </>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          ))}
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar