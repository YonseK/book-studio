import type { Book, BookEdition } from '../types/book'
import type { Page } from '../types/page'
import type { Panel } from '../types/panel'
import type { AISessionResponse, DesignPatternListItem, DesignPatternSet } from '../types/ai'

export interface RestClientConfig {
  baseURL: string
  headers?: Record<string, string>
  getToken?: () => string | null
}

export function restClient(config: RestClientConfig) {
  const { baseURL, headers: customHeaders, getToken } = config

  async function request<T>(
    path: string,
    options: RequestInit = {},
  ): Promise<T> {
    const url = `${baseURL}${path}`
    const token = getToken?.()
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/)?.[1]
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...customHeaders,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
      ...(options.headers as Record<string, string> ?? {}),
    }

    const res = await fetch(url, { ...options, headers, credentials: 'same-origin' })
    if (!res.ok) {
      const body = await res.text()
      throw new Error(`API Error ${res.status}: ${body}`)
    }
    if (res.status === 204) return null as T
    const json = await res.json()
    // DRF 페이지네이션 응답 자동 unwrap: {results: [...]} → [...]
    if (json && typeof json === 'object' && Array.isArray(json.results) && 'count' in json) {
      return json.results as T
    }
    return json
  }

  return {
    // ─── Base URL (SSE EventSource에 필요) ───
    getBaseURL: () => baseURL,

    // ─── Book ───
    books: {
      list: () => request<Book[]>('/books/'),
      get: (id: string) => request<Book>(`/books/${id}/`),
      create: (data: Partial<Book>) => request<Book>('/books/', { method: 'POST', body: JSON.stringify(data) }),
      update: (id: string, data: Partial<Book>) => request<Book>(`/books/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
      delete: (id: string) => request<void>(`/books/${id}/`, { method: 'DELETE' }),
      clone: (id: string) => request<Book>(`/books/${id}/clone/`, { method: 'POST' }),
      publish: (id: string) => request<BookEdition>(`/books/${id}/publish/`, { method: 'POST' }),
    },

    // ─── Edition ───
    editions: {
      list: (bookId: string) => request<BookEdition[]>(`/books/${bookId}/editions/`),
      get: (bookId: string, id: string) => request<BookEdition>(`/books/${bookId}/editions/${id}/`),
      update: (bookId: string, id: string, data: Partial<BookEdition>) =>
        request<BookEdition>(`/books/${bookId}/editions/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
    },

    // ─── Page ───
    pages: {
      list: (bookId: string, editionId: string) =>
        request<Page[]>(`/books/${bookId}/editions/${editionId}/pages/`),
      get: (bookId: string, editionId: string, id: string) =>
        request<Page>(`/books/${bookId}/editions/${editionId}/pages/${id}/`),
      create: (bookId: string, editionId: string, data: Partial<Page>) =>
        request<Page>(`/books/${bookId}/editions/${editionId}/pages/`, { method: 'POST', body: JSON.stringify(data) }),
      update: (bookId: string, editionId: string, id: string, data: Partial<Page>) =>
        request<Page>(`/books/${bookId}/editions/${editionId}/pages/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
      delete: (bookId: string, editionId: string, id: string) =>
        request<void>(`/books/${bookId}/editions/${editionId}/pages/${id}/`, { method: 'DELETE' }),
      sort: (bookId: string, editionId: string, pageIds: string[]) =>
        request<void>(`/books/${bookId}/editions/${editionId}/pages/sort/`, { method: 'POST', body: JSON.stringify({ page_ids: pageIds }) }),
      clone: (bookId: string, editionId: string, id: string) =>
        request<Page>(`/books/${bookId}/editions/${editionId}/pages/${id}/clone/`, { method: 'POST' }),
    },

    // ─── Panel ───
    panels: {
      list: (pageId: string) => request<Panel[]>(`/pages/${pageId}/panels/`),
      get: (pageId: string, id: string) => request<Panel>(`/pages/${pageId}/panels/${id}/`),
      create: (pageId: string, data: Partial<Panel>) =>
        request<Panel>(`/pages/${pageId}/panels/`, { method: 'POST', body: JSON.stringify(data) }),
      update: (pageId: string, id: string, data: Partial<Panel>) =>
        request<Panel>(`/pages/${pageId}/panels/${id}/`, { method: 'PATCH', body: JSON.stringify(data) }),
      delete: (pageId: string, id: string) =>
        request<void>(`/pages/${pageId}/panels/${id}/`, { method: 'DELETE' }),
      sort: (pageId: string, panelIds: string[]) =>
        request<void>(`/pages/${pageId}/panels/sort/`, { method: 'POST', body: JSON.stringify({ panel_ids: panelIds }) }),
      clone: (pageId: string, id: string) =>
        request<Panel>(`/pages/${pageId}/panels/${id}/clone/`, { method: 'POST' }),
    },

    // ─── Upload ───
    upload: {
      photo: (file: File, title?: string) => {
        const formData = new FormData()
        formData.append('image', file)
        if (title) formData.append('title', title)
        return request<{ id: string; image_url: string; image_view_url: string }>('/photos/', {
          method: 'POST',
          body: formData,
          headers: {} as any, // Content-Type은 브라우저가 자동 설정
        })
      },
    },

    // ─── Export ───
    export: {
      htmlPage: (pageId: string, responsive = false) =>
        request<{ html: string }>(`/export/html/page/${pageId}/?responsive=${responsive}`),
      htmlBook: (editionId: string, responsive = false) =>
        request<{ pages: { page_id: string; html: string }[] }>(`/export/html/edition/${editionId}/?responsive=${responsive}`),
    },

    // ─── Import ───
    import: {
      html: (editionId: string, html: string) =>
        request<{ pages: Page[] }>('/import/html/', { method: 'POST', body: JSON.stringify({ edition_id: editionId, html }) }),
    },

    // ─── AI ───
    ai: {
      createSession: (data: {
        book: string; edition: string; prompt: string
        options?: Record<string, unknown>; pattern_set?: string
      }) => request<AISessionResponse>('/ai/sessions/', { method: 'POST', body: JSON.stringify(data) }),

      getSession: (id: string) => request<AISessionResponse>(`/ai/sessions/${id}/`),

      approveSession: (id: string, data?: { plan?: unknown; pattern_set_id?: string }) =>
        request<AISessionResponse>(`/ai/sessions/${id}/approve/`, { method: 'POST', body: JSON.stringify(data || {}) }),

      cancelSession: (id: string) =>
        request<AISessionResponse>(`/ai/sessions/${id}/cancel/`, { method: 'POST' }),

      listPatterns: (params?: { category?: string; target_layout?: string }) => {
        const qs = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : ''
        return request<DesignPatternListItem[]>(`/ai/design-patterns/${qs}`)
      },

      listPatternSets: () => request<DesignPatternSet[]>('/ai/design-pattern-sets/'),
    },
  }
}

export type BookStudioClient = ReturnType<typeof restClient>
