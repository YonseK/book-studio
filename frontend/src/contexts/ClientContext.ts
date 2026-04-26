import { createContext, useContext } from 'react'
import type { BookStudioClient } from '../api/restClient'

export const ClientContext = createContext<BookStudioClient | null>(null)

export function useClient(): BookStudioClient {
  const client = useContext(ClientContext)
  if (!client) throw new Error('useClient must be used within ClientContext.Provider')
  return client
}
