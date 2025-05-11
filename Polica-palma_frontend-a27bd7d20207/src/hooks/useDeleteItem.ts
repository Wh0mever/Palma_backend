import {api} from "@/services/api.ts"

const useDeleteItem = () => {
  const [updateStatus, { isLoading, error }] = api.useDeleteDataMutation<any>()

  const deleteItem = async (url: string, id: any = undefined, invalidatesTags: string[] | undefined) => {

    try {
      let deleteUrl = `${url}/`
      if (id !== undefined) {
        deleteUrl += `${id}/`
      }

      await updateStatus({ url: deleteUrl, invalidatesTags: invalidatesTags })
    } catch (e: any) {
      console.log('Delete Error: ', e)
    }
  }

  return { deleteItem, isDeleting: isLoading, error, errorText: error && JSON.stringify(error.data) }
}

export default useDeleteItem