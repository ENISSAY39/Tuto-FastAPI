import Button from './ui/Button.jsx'

/**
 * Pager for the public directory. The server clamps out-of-range pages, so the
 * numbers displayed here are the ones it actually answered with.
 */
export default function Pagination({ page, totalPages, hasPrevious, hasNext, onChange }) {
  if (totalPages <= 1) return null

  return (
    <nav className="mt-8 flex items-center justify-center gap-4" aria-label="Pagination">
      <Button
        variant="ghost"
        size="sm"
        disabled={!hasPrevious}
        onClick={() => onChange(page - 1)}
      >
        Previous
      </Button>

      <span className="text-xs text-ink-400">
        Page {page} of {totalPages}
      </span>

      <Button variant="ghost" size="sm" disabled={!hasNext} onClick={() => onChange(page + 1)}>
        Next
      </Button>
    </nav>
  )
}
