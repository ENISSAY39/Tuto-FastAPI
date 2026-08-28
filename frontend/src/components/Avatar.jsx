import { initialsOf } from '../lib/format.js'

const SIZES = {
  sm: 'h-8 w-8 text-xs',
  md: 'h-11 w-11 text-sm',
  lg: 'h-16 w-16 text-lg',
}

/** Initials standing in for the profile picture the model does not store. */
export default function Avatar({ firstName, name, size = 'md', className = '', ...props }) {
  return (
    <span
      className={[
        'inline-flex shrink-0 items-center justify-center rounded-full',
        'bg-surface-700 font-semibold text-ink-700',
        SIZES[size] ?? SIZES.md,
        className,
      ].join(' ')}
      {...props}
    >
      {initialsOf(firstName, name)}
    </span>
  )
}
