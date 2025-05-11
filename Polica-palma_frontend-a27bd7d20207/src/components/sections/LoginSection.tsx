import {ModeToggle} from '@/components/mode-toggle.tsx'
import Logo from '@/components/ui/Logo.tsx'
import CenterBlock from '@/components/blocks/CenterBlock.tsx'
import AddForm from '@/components/others/AddForm.tsx'
import InputFormField from '@/components/others/InputFormField.tsx'
import {Button} from '@/components/ui/button.tsx'
import {z} from 'zod'
import {useNavigate} from 'react-router-dom'
import {useEffect, useState} from 'react'
import {useForm} from 'react-hook-form'
import {zodResolver} from '@hookform/resolvers/zod'
import axios from 'axios'
import {UserProfileData} from '@/typing/types.ts'
import getUrl from '@/config.ts'

interface InputValues {
  username: string
  password: string
}

const LoginSection = () => {
  const navigate = useNavigate()
  const apiUrl: string = `${getUrl()}/api/users/login/`
  const [success, setSuccess] = useState<boolean>(false)
  const [pending, setPending] = useState<boolean>(false)
  const [error, setError] = useState<boolean>(false)
  const [regexLoginError, setRegexLoginError] = useState<boolean>(false)
  const [regexPassError, setRegexPassError] = useState<boolean>(false)
  const [loginData, setLoginData] = useState<UserProfileData>({})
  const [inputValues, setInputValues] = useState<InputValues>({
    username: '',
    password: ''
  })

  const loginRegex = /^[a-zA-Z0-9_-]+$/
  const passwordRegex = /^[a-zA-Z0-9!@#$%^&*()_+{}[\]:;<>,.?/~`]+$/

  const FormSchema = z.object({
    username: z.string({ required_error: "Пожалуйста, введите имя пользователя" }),
    password: z.string({ required_error: "Пожалуйста, введите пароль" }),
  })

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  })

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    setPending(true)

    if (!loginRegex.test(data.username)) {
      setRegexLoginError(true)
      setTimeout(() => setRegexLoginError(false), 2500)
      setPending(false)
      return
    }

    if (!passwordRegex.test(data.password)) {
      setRegexPassError(true)
      setTimeout(() => setRegexPassError(false), 2500)
      setPending(false)
      return
    }

    try {
      const response = await axios.post(apiUrl, {
        "username": data.username,
        "password": data.password,
      })

      if (response.status === 201 || response.status === 200) {
        setSuccess(true)
        setTimeout(() => setSuccess(false), 500)
        setLoginData(response.data)
        form.reset()
      }
    } catch (e) {
      console.log('POST error: ', e)
      setError(true)
      setTimeout(() => setError(false), 1500)
    } finally {
      setPending(false)
    }
  }

  function setData(key: string, value: string) {
    localStorage.setItem(key, value)
  }

  useEffect(() => {
    if (success) {
      setData('user_id', loginData.id)
      setData('user_login', inputValues.username)
      setData('user_password', inputValues.password)
      setData('user_type', loginData.type)
      setData('first_name', loginData.first_name)
      navigate('/')
      location.reload()
    }
  }, [success, inputValues, loginData, navigate])

  const handleInputChange = (key: keyof InputValues, value: string) => {
    setInputValues({
      ...inputValues,
      [key]: value
    })
  }

  return (
    <>
      <div className='absolute top-5 right-5'>
        <ModeToggle />
      </div>

      <section className='w-full max-w-[500px] mx-auto p-3'>
        <CenterBlock>
          <div className='flex flex-col gap-10'>
            <div className='flex flex-col items-center gap-5'>
              <Logo/>
              <h1 className='text-3xl font-bold text-neutral-900 dark:text-white text-center'>Добро пожаловать в систему!</h1>
            </div>

            <div className='w-full p-5 flex flex-col gap-4 border border-neutral-300 dark:border-neutral-800 rounded-xl shadow-2xl'>
              <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Успешно авторизовано' error={error} errorDesc='Неверное имя пользователя или пароль' notMT>
                <div className='flex flex-col gap-2'>
                  <InputFormField
                    control={form.control}
                    type='text'
                    name='username'
                    placeholder='Имя пользователя'
                    _value={inputValues.username}
                    _onChange={(e: any) => handleInputChange('username', e.target.value)}
                  />
                  {regexLoginError && <span className="text-sm font-semibold text-red-500">В логине используются недопустимые символы</span>}

                  <InputFormField
                    control={form.control}
                    type='password'
                    name='password'
                    placeholder='Пароль'
                    _value={inputValues.password}
                    _onChange={(e: any) => handleInputChange('password', e.target.value)}
                    autocomplete=''
                  />
                  {regexPassError && <span className="text-sm font-semibold text-red-500">В пароле используются недопустимые символы</span>}
                </div>

                <Button type='submit' disabled={pending}>Войти</Button>
              </AddForm>
            </div>
          </div>
        </CenterBlock>
      </section>
    </>
  )
}

export default LoginSection