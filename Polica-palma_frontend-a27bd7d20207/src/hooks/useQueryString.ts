const useQueryString = (queryParams: any) => {
  const formatQueryParams = (params: Record<string, any>) => {
    return Object.keys(params).map(key => {
      const value = params[key]

      if (Array.isArray(value)) {
        return value.map(v => `${encodeURIComponent(key)}=${encodeURIComponent(v)}`).join('&')
      }

      return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
    }).join('&')
  }

  for (const key of Object.keys(queryParams)) {
    if (queryParams[key] === '') {
      delete queryParams[key]
    }
  }

  const queryString = formatQueryParams(queryParams)

  return { queryString }
}

export default useQueryString