import { useEffect, useState } from 'react'
import { api } from '../api'
import type { DocumentItem, QuestionResponse } from '../types'

export default function AskPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [selected, setSelected] = useState<number[]>([])
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<QuestionResponse | null>(null)

  useEffect(() => {
    api
      .listDocuments()
      .then((docs) => setDocuments(docs.filter((doc) => doc.status === 'ready')))
      .catch(() => setDocuments([]))
  }, [])

  const toggle = (id: number) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((value) => value !== id) : [...prev, id],
    )
  }

  const ask = async () => {
    const value = question.trim()
    if (!value) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const response = await api.ask({
        question: value,
        document_ids: selected.length > 0 ? selected : undefined,
      })
      setResult(response)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <section>
      <div className="card">
        <h2>Belgelerinize Soru Sorun</h2>

        {documents.length > 0 && (
          <>
            <p className="muted" style={{ margin: '0 0 4px' }}>
              Arama kapsamı (boş bırakırsanız tüm hazır belgeler):
            </p>
            <div className="scope">
              {documents.map((doc) => (
                <label key={doc.id}>
                  <input
                    type="checkbox"
                    checked={selected.includes(doc.id)}
                    onChange={() => toggle(doc.id)}
                  />
                  {doc.filename}
                </label>
              ))}
            </div>
          </>
        )}

        <textarea
          rows={3}
          placeholder="Örn. Proje tesliminde hangi belgeler gerekiyor?"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          style={{ marginTop: 12 }}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
              void ask()
            }
          }}
        />
        <div className="row" style={{ marginTop: 10 }}>
          <button className="btn" onClick={() => void ask()} disabled={loading || !question.trim()}>
            {loading ? 'Yanıt üretiliyor…' : 'Sor'}
          </button>
          <span className="muted" style={{ fontSize: '0.82rem' }}>
            Cevap yalnızca yüklediğiniz belgelere dayanır.
          </span>
        </div>
      </div>

      {error && <div className="alert alert--err">{error}</div>}

      {result && (
        <div className="card">
          <h2>Cevap</h2>
          {result.no_answer && (
            <div className="alert alert--info">Bu soru belgelerinizden yanıtlanamadı.</div>
          )}
          <p className="answer">{result.answer}</p>

          {result.sources.length > 0 && (
            <>
              <h2 style={{ marginTop: 20 }}>Kaynaklar ({result.sources.length})</h2>
              <ul className="sources">
                {result.sources.map((source, index) => (
                  <li key={`${source.chunk_id ?? 'x'}-${index}`} className="source">
                    <div className="source__head">
                      [{index + 1}] {source.filename ?? 'belge'}
                      {source.page_number ? ` · sayfa ${source.page_number}` : ''}
                      {source.relevance_score != null
                        ? ` · ilgi: ${source.relevance_score.toFixed(2)}`
                        : ''}
                    </div>
                    <p className="source__text">{source.snippet}</p>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </section>
  )
}
