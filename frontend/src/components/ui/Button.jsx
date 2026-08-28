import Spinner from './Spinner.jsx'

const VARIANTS = {
  primary:
    'bg-accent-500 text-white shadow-sm shadow-accent-500/25 hover:bg-accent-400 active:bg-accent-600',
  ghost:
    'border border-white/10 bg-white/0 text-slate-200 hover:border-white/20 hover:bg-white/5',
  subtle: 'bg-surface-700 text-slate-100 hover:bg-surface-600',
  danger: 'bg-rose-600 text-white hover:bg-rose-500 active:bg-rose-700',
  quiet: 'text-slate-400 hover:bg-white/5 hover:text-slate-100',
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
