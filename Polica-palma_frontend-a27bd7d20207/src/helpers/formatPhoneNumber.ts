const formatPhoneNumber = (phoneNumber: string) => {
  let countryCode: string = ''
  if (phoneNumber.startsWith('+998')) {
    countryCode = '+998'
  } else {
    return phoneNumber
  }

  let formattedNumber: string = ''
  if (countryCode === '+998') {
    formattedNumber = `${countryCode} (${phoneNumber.slice(4, 6)}) ${phoneNumber.slice(6, 9)}-${phoneNumber.slice(9, 11)}-${phoneNumber.slice(11, 13)}`
  } else {
    return phoneNumber
  }

  return formattedNumber
}

export default formatPhoneNumber