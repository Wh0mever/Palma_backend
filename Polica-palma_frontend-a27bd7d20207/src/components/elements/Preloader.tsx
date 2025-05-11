import Logo from '@/components/ui/Logo.tsx'

const Preloader = () => {
  return (
    <div className='z-50 fixed top-0 left-0 w-full h-screen flex flex-col items-center justify-center gap-6 bg-white dark:bg-neutral-950'>
      <Logo />
      <div className='w-32 h-32 bg-transparent border-4 border-neutral-800 border-dotted rounded-full loading-circle dark:border-white' />
    </div>
  )
}

export default Preloader