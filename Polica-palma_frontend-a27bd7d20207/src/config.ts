const getUrl = () => {
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  const isDev: boolean = import.meta.env.DEV

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  const MAIN_API_URL: string = import.meta.env.VITE_API_URL

  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-expect-error
  const DEV_API_URL: string = import.meta.env.VITE_DEV_API_URL

  if (!isDev) {
    return MAIN_API_URL
  } else {
    return DEV_API_URL
  }
}

export default getUrl