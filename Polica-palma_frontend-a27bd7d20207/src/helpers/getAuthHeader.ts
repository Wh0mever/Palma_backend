import {encode as base64_encode} from 'base-64'
import getUserData from '@/helpers/getUserData.ts'

const getAuthorizationHeader = () => {
  const { userLogin, userPassword } = getUserData()
  const authString = `${userLogin}:${userPassword}`
  const encodedAuthString = base64_encode(authString)
  localStorage.setItem('authToken', encodedAuthString)

  const storedAuthToken = localStorage.getItem('authToken')
  if (storedAuthToken) {
    return `Basic ${storedAuthToken}`
  } else {
    console.log('Auth token not found')
  }
}

export default getAuthorizationHeader