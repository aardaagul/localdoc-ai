import type {
  ConversationDetail,
  ConversationItem,
  DocumentItem,
  Health,
  QuestionRequest,
  QuestionResponse,
} from './types'

const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

async function errorFrom(response: Response): Promise<Error> {
  let message = `İstek başarısız (HTTP ${response.status}).`
  try {
    const body = await response.json()
    if (typeof body?.detail === 'string') {
      message = body.detail
    } else if (Array.isArray(body?.detail)) {
      message = body.detail.map((item: { msg?: string }) => item.msg ?? '').join(' ')
    }
  } catch {
    // gövde JSON değilse varsayılan mesajı kullan
  }
  return new Error(message)
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers ?? {}) },
    ...options,
  })
  if (!response.ok) {
    throw await errorFrom(response)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export const api = {
  health: () => request<Health>('/api/health'),

  listDocuments: () => request<DocumentItem[]>('/api/documents'),

  getDocument: (id: number) => request<DocumentItem>(`/api/documents/${id}`),

  deleteDocument: (id: number) =>
    request<void>(`/api/documents/${id}`, { method: 'DELETE' }),

  async uploadDocument(file: File): Promise<DocumentItem> {
    const form = new FormData()
    form.append('file', file)
    const response = await fetch(`${API_BASE}/api/documents`, {
      method: 'POST',
      body: form,
    })
    if (!response.ok) {
      throw await errorFrom(response)
    }
    return (await response.json()) as DocumentItem
  },

  ask: (payload: QuestionRequest) =>
    request<QuestionResponse>('/api/questions', {
      method: 'POST',
      body: JSON.stringify(payload),
    }),

  listConversations: () => request<ConversationItem[]>('/api/conversations'),

  getConversation: (id: number) =>
    request<ConversationDetail>(`/api/conversations/${id}`),

  deleteConversation: (id: number) =>
    request<void>(`/api/conversations/${id}`, { method: 'DELETE' }),
}
