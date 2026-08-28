const TONES = {
  error: 'border-rose-500/30 bg-rose-500/10 text-rose-200',
  success: 'border-emerald-500/30 bg-emerald-500/10 text-emerald-200',
  info: 'border-sky-500/30 bg-sky-500/10 text-sky-200',
  warning: 'border-amber-500/30 bg-amber-500/10 text-amber-200',
}

export default function Alert({ tone = 'info', className = '', children }) {
  if (!children) return null
  return (
    <div
      role={tone === 'error' ? 'alert' : 'status'}
      className={`rounded-lg border px-3 py-2 text-sm ${TONES[tone] ?? TONES.info} ${className}`}
    >
      {children}
    </div>
  )
}
