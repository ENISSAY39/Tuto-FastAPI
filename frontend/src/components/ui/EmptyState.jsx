export default function EmptyState({ icon, title, description, action, className = '' }) {
  return (
    <div
      className={`flex flex-col items-center justify-center rounded-xl border border-dashed border-white/10 px-6 py-12 text-center ${className}`}
    >
      {icon && <div className="mb-3 text-slate-500">{icon}</div>}
      <p className="text-sm font-medium text-slate-300">{title}</p>
      {description && <p className="mt-1 max-w-sm text-sm text-slate-500">{description}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
