export default function Logo({ className = 'h-8 w-8' }) {
  return (
    <span
      className={`inline-flex ${className} items-center justify-center rounded-lg bg-gradient-to-br from-accent-400 to-accent-600 text-surface-950 shadow-sm shadow-accent-500/30`}
      aria-hidden="true"
    >
      <svg viewBox="0 0 24 24" fill="none" className="h-1/2 w-1/2">
        <rect
          x="3"
          y="7.5"
          width="18"
          height="13"
          rx="2.5"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinejoin="round"
        />
        <path
          d="M8.5 7.5V5.8A1.8 1.8 0 0 1 10.3 4h3.4a1.8 1.8 0 0 1 1.8 1.8v1.7"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
        />
      </svg>
    </span>
  )
}
