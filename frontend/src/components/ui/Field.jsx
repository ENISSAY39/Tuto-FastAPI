import { useId } from 'react'

const CONTROL_CLASSES = [
  'w-full rounded-lg border border-white/10 bg-surface-850 px-3 py-2 text-sm text-slate-100',
  'placeholder:text-slate-500',
  'transition-colors focus:border-accent-500 focus:outline-none',
  'disabled:cursor-not-allowed disabled:opacity-60',
].join(' ')

function Wrapper({ id, label, hint, error, children }) {
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={id} className="mb-1.5 block text-xs font-medium text-slate-400">
          {label}
        </label>
      )}
      {children}
      {error ? (
        <p className="mt-1.5 text-xs text-rose-400">{error}</p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-slate-500">{hint}</p>
      ) : null}
    </div>
  )
}

export default function Field({ label, hint, error, className = '', ...props }) {
  const generatedId = useId()
  const id = props.id ?? generatedId
  return (
    <Wrapper id={id} label={label} hint={hint} error={error}>
      <input
        id={id}
        aria-invalid={error ? 'true' : undefined}
        className={[CONTROL_CLASSES, error ? 'border-rose-500/60' : '', className].join(' ')}
        {...props}
      />
    </Wrapper>
  )
}

export function TextareaField({ label, hint, error, className = '', rows = 4, ...props }) {
  const generatedId = useId()
  const id = props.id ?? generatedId
  return (
    <Wrapper id={id} label={label} hint={hint} error={error}>
      <textarea
        id={id}
        rows={rows}
        aria-invalid={error ? 'true' : undefined}
        className={[CONTROL_CLASSES, 'resize-y', error ? 'border-rose-500/60' : '', className].join(' ')}
        {...props}
      />
    </Wrapper>
  )
}
