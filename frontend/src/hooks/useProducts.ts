import { useQuery } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { MyProduct } from '@/types'

export const useProducts = () => {
  return useQuery({
    queryKey: ['products'],
    queryFn: async () => {
      const response = await api.get('/products/')
      return response.data as MyProduct[]
    },
  })
}

export const useProduct = (asin: string) => {
  return useQuery({
    queryKey: ['products', asin],
    queryFn: async () => {
      const response = await api.get(`/products/${asin}`)
      return response.data as MyProduct
    },
    enabled: !!asin,
  })
}