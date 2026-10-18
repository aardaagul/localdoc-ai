export interface Health {
  status: string
  app: string
  ollama: {
    available: boolean
    base_url: string
    chat_model: string
    embed_model: string
    models: string[]
  }
}

export type DocumentStatus = 'processing' | 'ready' | 'error'

export interface DocumentItem {
  id: number
  filename: string
  file_type: string
  file_size: number
  status: DocumentStatus | string
  error_message: string | null
  chunk_count: number
  created_at: string
}

export interface Source {
  chunk_id: number | null
  document_id: number | null
  filename: string | null
  page_number: number | null
  relevance_score: number | null
  snippet: string | null
}

export interface QuestionRequest {
  question: string
  document_ids?: number[]
  conversation_id?: number | null
  top_k?: number | null
}

export interface QuestionResponse {
  answer: string
  no_answer: boolean
  sources: Source[]
  conversation_id: number
  message_id: number
}

export interface MessageItem {
  id: number
  role: string
  content: string
  created_at: string
  sources: Source[]
}

export interface ConversationItem {
  id: number
  title: string | null
  created_at: string
}

export interface ConversationDetail extends ConversationItem {
  messages: MessageItem[]
}
