export default function Card({ className = '', children, ...props }) {
  return (
    <div
      className={[
        'rounded-xl border border-white/8 bg-surface-900/80 shadow-lg shadow-black/30',
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
      className={`flex flex-wrap items-start justify-between gap-3 border-b border-white/8 px-5 py-4 ${className}`}
    >
      <div className="min-w-0">
        <h2 className="truncate text-sm font-semibold tracking-wide text-slate-100 uppercase">
          {title}
        </h2>
        {subtitle && <p className="mt-1 text-sm text-slate-400">{subtitle}</p>}
      </div>
      {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
    </div>
  )
}
