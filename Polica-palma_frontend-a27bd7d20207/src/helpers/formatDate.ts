const formatDate = (createdAt: string | any) => {
  const date = new Date(createdAt)

  return date.toLocaleDateString('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default formatDate