// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-expect-error
import logoDark from '@/assets/logo-dark.png'

const Logo = () => {
  return (
    <img src={logoDark} alt='Logo' className='w-52 h-10 main-logo'/>
  )
}

export default Logo