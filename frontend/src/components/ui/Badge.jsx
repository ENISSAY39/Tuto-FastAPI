const TONES = {
  neutral: 'border-white/10 bg-white/5 text-slate-300',
  sky: 'border-sky-500/25 bg-sky-500/10 text-sky-300',
  amber: 'border-amber-500/25 bg-amber-500/10 text-amber-300',
  emerald: 'border-emerald-500/25 bg-emerald-500/10 text-emerald-300',
  rose: 'border-rose-500/25 bg-rose-500/10 text-rose-300',
  violet: 'border-violet-500/25 bg-violet-500/10 text-violet-300',
}

export default function Badge({ tone = 'neutral', className = '', children }) {
  return (
    <span
      className={[
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium whitespace-nowrap',
        TONES[tone] ?? TONES.neutral,
        className,
      ].join(' ')}
    >
      {children}
    </span>
  )
}
