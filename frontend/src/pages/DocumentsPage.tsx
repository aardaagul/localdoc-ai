import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import StatusBadge from '../components/StatusBadge'
import type { DocumentItem } from '../types'

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString('tr-TR')
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [error, setError] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const refresh = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments())
      setError(null)
    } catch (err) {
      setError((err as Error).message)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  // İşlenmekte olan belge varsa durumu periyodik olarak yenile.
  useEffect(() => {
    if (!documents.some((doc) => doc.status === 'processing')) return
    const timer = setInterval(() => void refresh(), 2500)
    return () => clearInterval(timer)
  }, [documents, refresh])

  const handleFiles = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    setUploading(true)
    setError(null)
    try {
      for (const file of Array.from(files)) {
        await api.uploadDocument(file)
      }
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setUploading(false)
      if (inputRef.current) inputRef.current.value = ''
    }
  }

  const handleDelete = async (id: number) => {
    if (!window.confirm('Bu belge ve ilişkili tüm parçalar silinecek. Emin misiniz?')) return
    try {
      await api.deleteDocument(id)
      await refresh()
    } catch (err) {
      setError((err as Error).message)
    }
  }

  return (
    <section>
      <div className="card">
        <h2>Belge Yükle</h2>
        <div
          className="dropzone"
          onClick={() => inputRef.current?.click()}
          onDragOver={(event) => event.preventDefault()}
          onDrop={(event) => {
            event.preventDefault()
            void handleFiles(event.dataTransfer.files)
          }}
        >
          {uploading ? 'Yükleniyor…' : 'PDF veya TXT dosyanızı sürükleyip bırakın ya da tıklayarak seçin'}
        </div>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.txt"
          multiple
          hidden
          onChange={(event) => void handleFiles(event.target.files)}
        />
      </div>

      {error && <div className="alert alert--err">{error}</div>}

      <div className="card">
        <h2>Belgeler ({documents.length})</h2>
        {documents.length === 0 ? (
          <p className="muted">Henüz belge yüklenmedi.</p>
        ) : (
          <ul className="doc-list">
            {documents.map((doc) => (
              <li key={doc.id} className="doc-item">
                <div className="doc-item__meta">
                  <div className="doc-item__name">{doc.filename}</div>
                  <div className="doc-item__sub">
                    {doc.file_type.toUpperCase()} · {formatSize(doc.file_size)} ·{' '}
                    {doc.chunk_count} parça · {formatDate(doc.created_at)}
                  </div>
                  {doc.status === 'error' && doc.error_message && (
                    <div className="doc-item__sub" style={{ color: 'var(--err)' }}>
                      {doc.error_message}
                    </div>
                  )}
                </div>
                <StatusBadge status={doc.status} />
                <button className="btn btn--ghost" onClick={() => void handleDelete(doc.id)}>
                  Sil
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  )
}
