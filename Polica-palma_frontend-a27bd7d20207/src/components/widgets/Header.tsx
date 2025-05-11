import {Button} from '@/components/ui/button.tsx'
import {ChevronDown, LogOut, Menu} from 'lucide-react'
import {ModeToggle} from '@/components/mode-toggle.tsx'
import {Avatar, AvatarFallback} from '@/components/ui/avatar.tsx'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu.tsx'
import HeaderCashItem from '../items/HeaderCashItem'
import useWindowWidth from '@/hooks/useWindowWidth.ts'
import {useCashiers} from '@/providers/CashiersProvider.tsx'
import getUserData from '@/helpers/getUserData.ts'
import HeaderCashiersSkeleton from '@/components/skeletons/HeaderCashiersSkeleton.tsx'
// import {api} from "@/services/api.ts"
// import {Skeleton} from "@/components/ui/skeleton.tsx"

interface HeaderProps {
  onClick?: () => void
}

const Header = ({ onClick }: HeaderProps) => {
  const { data, isLoading } = useCashiers()
  const { windowWidth } = useWindowWidth()
  const { userLogin, userType, firstName } = getUserData()
  // const {data: hasShiftData, isLoading: hasShiftIsLoading} = api.useGetShiftStatusQuery('')

  const handleLogout = () => {
    localStorage.clear()
    location.reload()
  }

  return (
    <>
      <header className='w-full p-4 flex items-center justify-between gap-5 border-b border-b-neutral-300 dark:border-b-neutral-800'>
        <Button size='icon' onClick={onClick}>
          <Menu className='w-4 h-4' />
        </Button>

        <div className='flex items-center gap-4'>
          { windowWidth >= 925 ? (
            <>
              { userType === 'ADMIN' ? (
                <>
                  { !isLoading ? (
                    <div className="mr-28 flex items-center gap-12">
                      {data && Array.isArray(data) && data.map(item => (
                        <HeaderCashItem key={item.id} type={item.name} amount={item.amount}/>
                      ))}
                    </div>
                  ) : (
                    <HeaderCashiersSkeleton />
                  ) }
                </>
              ) : null}
            </>
          ) : (
            <>
              {userType === 'ADMIN' ? (
                <DropdownMenu>
                  <DropdownMenuTrigger>
                    <Button variant="outline" size="icon">
                      <ChevronDown className="w-4 h-4"/>
                    </Button>
                  </DropdownMenuTrigger>

                  <DropdownMenuContent>
                    { isLoading ? (
                      <HeaderCashiersSkeleton />
                      ) : (
                      <div className="p-2 flex flex-col gap-2">
                        {data && Array.isArray(data) && data.map(item => (
                          <HeaderCashItem key={item.id} type={item.name} amount={item.amount}/>
                        ))}
                      </div>
                    ) }
                  </DropdownMenuContent>
                </DropdownMenu>
              ) : null }
            </>
          ) }

          {/*{ hasShiftIsLoading ? (*/}
          {/*  <Skeleton className='w-5 h-5 rounded-full' />*/}
          {/*) : (*/}
          {/*  <div*/}
          {/*    title={hasShiftData.has_shift ? 'Смена открыта' : 'Смена закрыта'}*/}
          {/*    className={`w-5 h-5 rounded-full cursor-pointer ${hasShiftData.has_shift ? 'bg-green-500' : 'bg-red-500'}`}*/}
          {/*  />*/}
          {/*) }*/}

          <ModeToggle/>

          <DropdownMenu>
            <DropdownMenuTrigger>
              <Avatar>
                <AvatarFallback>{userLogin?.charAt(0).toUpperCase()}</AvatarFallback>
              </Avatar>
            </DropdownMenuTrigger>

            <DropdownMenuContent>
              <DropdownMenuGroup>
                <DropdownMenuItem>
                  <p className='font-semibold'>Пользователь: <span className='font-bold'>{firstName || userLogin}</span></p>
                </DropdownMenuItem>

                <DropdownMenuItem className='cursor-pointer font-semibold text-red-500' onClick={handleLogout}>
                  <LogOut className='w-4 h-4 mr-2' /> Выйти
                </DropdownMenuItem>
              </DropdownMenuGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>
    </>
  )
}

export default Header