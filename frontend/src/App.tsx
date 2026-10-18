import { useEffect, useState } from 'react'
import { api } from './api'
import type { Health } from './types'
import AskPage from './pages/AskPage'
import DocumentsPage from './pages/DocumentsPage'
import HistoryPage from './pages/HistoryPage'

type Tab = 'documents' | 'ask' | 'history'

const TABS: { id: Tab; label: string }[] = [
  { id: 'documents', label: '📁 Belgeler' },
  { id: 'ask', label: '💬 Soru-Cevap' },
  { id: 'history', label: '🕘 Geçmiş' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('documents')
  const [health, setHealth] = useState<Health | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)

  useEffect(() => {
    let active = true
    const load = () => {
      api
        .health()
        .then((value) => {
          if (!active) return
          setHealth(value)
          setHealthError(null)
        })
        .catch((error: Error) => {
          if (!active) return
          setHealth(null)
          setHealthError(error.message)
        })
    }
    load()
    const timer = setInterval(load, 15000)
    return () => {
      active = false
      clearInterval(timer)
    }
  }, [])

  return (
    <div className="app">
      <header className="app__header">
        <h1>📄 LocalDoc AI</h1>
        <p className="app__subtitle">
          Yerel LLM destekli doküman bilgi sistemi — belgeleriniz hakkında soru sorun,
          cevapları kaynaklarıyla görün.
        </p>
        <div className="status">
          {health ? (
            health.ollama.available ? (
              <span className="badge badge--ok">
                Model hazır · {health.ollama.chat_model}
              </span>
            ) : (
              <span className="badge badge--warn">Ollama kapalı — yalnızca arama çalışır</span>
            )
          ) : (
            <span className="badge badge--err">Backend'e ulaşılamıyor</span>
          )}
          {healthError && <span className="status__hint">{healthError}</span>}
        </div>
      </header>

      <nav className="tabs">
        {TABS.map((item) => (
          <button
            key={item.id}
            className={item.id === tab ? 'tab tab--active' : 'tab'}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <main>
        {tab === 'documents' && <DocumentsPage />}
        {tab === 'ask' && <AskPage />}
        {tab === 'history' && <HistoryPage />}
      </main>

      <footer className="app__footer">
        LocalDoc AI · Tüm işlemler yerel makinenizde gerçekleşir.
      </footer>
    </div>
  )
}
