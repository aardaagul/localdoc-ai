interface Props {
  status: string
}

const LABELS: Record<string, { text: string; className: string }> = {
  processing: { text: 'İşleniyor…', className: 'badge badge--warn' },
  ready: { text: 'Hazır', className: 'badge badge--ok' },
  error: { text: 'Hata', className: 'badge badge--err' },
}

export default function StatusBadge({ status }: Props) {
  const info = LABELS[status] ?? { text: status, className: 'badge' }
  return <span className={info.className}>{info.text}</span>
}
