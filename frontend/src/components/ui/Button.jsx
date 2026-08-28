import Spinner from './Spinner.jsx'

const VARIANTS = {
  primary:
    'bg-accent-600 text-white shadow-sm shadow-accent-600/20 hover:bg-accent-700 active:bg-accent-800',
  ghost:
    'border border-ink-900/12 bg-transparent text-ink-700 hover:border-ink-900/25 hover:bg-ink-900/5',
  subtle: 'bg-surface-700 text-ink-900 hover:bg-surface-600',
  danger: 'bg-rose-600 text-white hover:bg-rose-700 active:bg-rose-800',
  quiet: 'text-ink-500 hover:bg-ink-900/5 hover:text-ink-900',
}

const SIZES = {
  sm: 'h-8 gap-1.5 px-3 text-xs',
  md: 'h-10 gap-2 px-4 text-sm',
  lg: 'h-11 gap-2 px-5 text-sm',
}

function buttonClasses({ variant, size, className }) {
  return [
    'inline-flex cursor-pointer items-center justify-center rounded-lg font-medium no-underline',
    'transition-colors duration-150',
    'disabled:cursor-not-allowed disabled:opacity-50',
    VARIANTS[variant] ?? VARIANTS.primary,
    SIZES[size] ?? SIZES.md,
    className,
  ].join(' ')
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  className = '',
  children,
  ...props
}) {
  return (
    <button
      disabled={disabled || loading}
      className={buttonClasses({ variant, size, className })}
      {...props}
    >
      {loading && <Spinner className="h-3.5 w-3.5" />}
      {children}
    </button>
  )
}

/**
 * Same look, but a real anchor — pages are separate documents here, so
 * navigation must stay middle-click and open-in-new-tab friendly.
 */
export function LinkButton({ variant = 'primary', size = 'md', className = '', children, ...props }) {
  return (
    <a className={buttonClasses({ variant, size, className })} {...props}>
      {children}
    </a>
  )
}
