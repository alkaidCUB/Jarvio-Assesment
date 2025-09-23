import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { api } from '@/utils/api'
import type { User, AuthState } from '@/types'

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token } = response.data
          
          localStorage.setItem('auth-token', access_token)
          
          const userResponse = await api.get('/auth/me')
          const user: User = userResponse.data
          
          set({ 
            user, 
            token: access_token, 
            isAuthenticated: true 
          })
        } catch (error) {
          console.error('Login failed:', error)
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('auth-token')
        set({ 
          user: null, 
          token: null, 
          isAuthenticated: false 
        })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user, 
        token: state.token, 
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)