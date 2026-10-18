import { useCallback, useEffect, useState } from 'react'
import { api } from '../api'
import type { ConversationDetail, ConversationItem } from '../types'

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('tr-TR')
}

export default function HistoryPage() {
  const [conversations, setConversations] = useState<ConversationItem[]>([])
  const [selected, setSelected] = useState<ConversationDetail | null>(null)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setConversations(await api.listConversations())
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const open = async (id: number) => {
    try {
      setSelected(await api.getConversation(id))
    } catch (err) {
      setError((err as Error).message)
    }
  }

  const remove = async (id: number) => {
    if (!window.confirm('Bu konuşma silinsin mi?')) return
    try {
      await api.deleteConversation(id)
      if (selected?.id === id) setSelected(null)
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <section>
      {error && <div className="alert alert--err">{error}</div>}

      <div className="card">
        <h2>Konuşmalar ({conversations.length})</h2>
        {conversations.length === 0 ? (
          <p className="muted">Henüz soru sormadınız.</p>
        ) : (
          <ul className="conv-list">
            {conversations.map((conversation) => (
              <li
                key={conversation.id}
                className="conv-item"
                onClick={() => void open(conversation.id)}
              >
                <span className="conv-item__title">
                  {conversation.title ?? `Konuşma #${conversation.id}`}
                </span>
                <span className="muted" style={{ fontSize: '0.8rem' }}>
                  {formatDate(conversation.created_at)}
                </span>
                <button
                  className="btn btn--ghost"
                  onClick={(event) => {
                    event.stopPropagation()
                    void remove(conversation.id)
                  }}
                >
                  Sil
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {selected && (
        <div className="card">
          <h2>{selected.title ?? `Konuşma #${selected.id}`}</h2>
          {selected.messages.map((message) => (
            <div
              key={message.id}
              className={message.role === 'user' ? 'turn turn--user' : 'turn turn--assistant'}
            >
              <div className="turn__role">{message.role === 'user' ? 'Siz' : 'LocalDoc AI'}</div>
              <div className="turn__bubble">{message.content}</div>
              {message.sources.length > 0 && (
                <ul className="sources">
                  {message.sources.map((source, index) => (
                    <li key={`${message.id}-${index}`} className="source">
                      <div className="source__head">
                        [{index + 1}] {source.filename ?? 'belge'}
                        {source.page_number ? ` · sayfa ${source.page_number}` : ''}
                      </div>
                      <p className="source__text">{source.snippet}</p>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
