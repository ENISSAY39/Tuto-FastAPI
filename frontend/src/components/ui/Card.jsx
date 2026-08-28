export default function Card({ className = '', children, ...props }) {
  return (
    <div
      className={[
        'rounded-xl border border-ink-900/10 bg-surface-900/80 shadow-lg shadow-ink-900/8',
        'backdrop-blur-sm',
        className,
      ].join(' ')}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ title, subtitle, actions, className = '' }) {
  return (
    <div
      className={`flex flex-wrap items-start justify-between gap-3 border-b border-ink-900/10 px-5 py-4 ${className}`}
    >
      <div className="min-w-0">
        <h2 className="truncate text-sm font-semibold tracking-wide text-ink-900 uppercase">
          {title}
        </h2>
        {subtitle && <p className="mt-1 text-sm text-ink-500">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </div>
  )
}
