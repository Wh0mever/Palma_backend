import {UserTypes} from '@/typing/types.ts'

const getUserData = () => {
  const userId = localStorage.getItem('user_id')
  const userLogin = localStorage.getItem('user_login')
  const userPassword = localStorage.getItem('user_password')
  const userType: UserTypes = localStorage.getItem('user_type')
  const firstName = localStorage.getItem('first_name')

  return { userId, userLogin, userPassword, userType, firstName }
}

export default getUserData