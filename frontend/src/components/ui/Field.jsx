import { useId } from 'react'

const CONTROL_CLASSES = [
  'w-full rounded-lg border border-ink-900/12 bg-surface-850 px-3 py-2 text-sm text-ink-900',
  'placeholder:text-ink-400',
  'transition-colors focus:border-accent-600 focus:outline-none',
  'disabled:cursor-not-allowed disabled:opacity-60',
].join(' ')

function Wrapper({ id, label, hint, error, children }) {
  return (
    <div className="w-full">
      {label && (
        <label htmlFor={id} className="mb-1.5 block text-xs font-medium text-ink-500">
          {label}
        </label>
      )}
      {children}
      {error ? (
        <p className="mt-1.5 text-xs text-rose-600">{error}</p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-ink-400">{hint}</p>
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
        className={[CONTROL_CLASSES, error ? 'border-rose-400' : '', className].join(' ')}
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
        className={[CONTROL_CLASSES, 'resize-y', error ? 'border-rose-400' : '', className].join(' ')}
        {...props}
      />
    </Wrapper>
  )
}
