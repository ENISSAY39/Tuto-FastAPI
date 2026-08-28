import Badge from './ui/Badge.jsx'
import Button from './ui/Button.jsx'
import { formatDateRange, formatDuration } from '../lib/format.js'

/**
 * One dated entry — an experience or an education — in the same visual shape,
 * because both models carry a title, a subtitle, a period and a description.
 *
 * The action buttons are only rendered when the viewer owns the record: the
 * public portfolio passes no handler at all.
 */
export default function TimelineEntry({ title, subtitle, entry, onEdit, onDelete }) {
  const duration = formatDuration(entry.date_start, entry.date_end)

  return (
    <article className="relative rounded-xl border border-white/8 bg-surface-900/60 p-5 transition-colors hover:border-white/15">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="text-base font-semibold text-balance text-slate-100">{title}</h3>
          <p className="mt-0.5 text-sm text-accent-400">{subtitle}</p>
        </div>

        {(onEdit || onDelete) && (
          <div className="flex shrink-0 items-center gap-1">
            {onEdit && (
              <Button variant="quiet" size="sm" onClick={onEdit}>
                Edit
              </Button>
            )}
            {onDelete && (
              <Button variant="quiet" size="sm" onClick={onDelete}>
                Delete
              </Button>
            )}
          </div>
        )}
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-slate-500">
        <span>{formatDateRange(entry.date_start, entry.date_end)}</span>
        {duration && <Badge>{duration}</Badge>}
      </div>

      <p className="mt-3 text-sm whitespace-pre-line text-slate-400">{entry.description}</p>
    </article>
  )
}
