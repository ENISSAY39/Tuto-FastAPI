/**
 * Date helpers.
 *
 * The API sends plain calendar dates ("2020-01-31"), never timestamps. They
 * are parsed from their parts on purpose: `new Date('2020-01-31')` is read as
 * UTC midnight, which renders as the previous day for anyone west of
 * Greenwich, and `toISOString()` shifts it back for anyone east of it.
 */

const ISO_DATE = /^(\d{4})-(\d{2})-(\d{2})/

function parseApiDate(value) {
  const match = ISO_DATE.exec(String(value ?? ''))
  if (!match) return null

  const [, year, month, day] = match
  const date = new Date(Number(year), Number(month) - 1, Number(day))
  return Number.isNaN(date.getTime()) ? null : date
}

/** Human-readable date, e.g. "31 Jan 2020". */
export function formatDate(value) {
  const date = parseApiDate(value)
  if (!date) return '—'
  return date.toLocaleDateString(undefined, {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

/** Compact month-and-year label used on portfolio timelines. */
export function formatMonth(value) {
  const date = parseApiDate(value)
  if (!date) return '—'
  return date.toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
}

/** "Sep 2015 — Jun 2019", the headline of an experience or education card. */
export function formatDateRange(start, end) {
  return `${formatMonth(start)} — ${formatMonth(end)}`
}

/**
 * Rough duration of a period, in the wording a CV would use. Both bounds are
 * inclusive months, so a January-to-January entry reads as "1 yr 1 mo".
 */
export function formatDuration(start, end) {
  const from = parseApiDate(start)
  const to = parseApiDate(end)
  if (!from || !to || to < from) return ''

  const months =
    (to.getFullYear() - from.getFullYear()) * 12 + (to.getMonth() - from.getMonth()) + 1
  const years = Math.floor(months / 12)
  const remainingMonths = months % 12

  const parts = []
  if (years > 0) parts.push(`${years} yr${years === 1 ? '' : 's'}`)
  if (remainingMonths > 0) parts.push(`${remainingMonths} mo`)
  return parts.join(' ')
}

/** <input type="date"> wants exactly YYYY-MM-DD, which is what the API sends. */
export function toDateInputValue(value) {
  const match = ISO_DATE.exec(String(value ?? ''))
  return match ? match[0] : ''
}

/** Avatar fallback: "Ada Lovelace" becomes "AL", "Ada" becomes "AD". */
export function initialsOf(...names) {
  const parts = names
    .flatMap((name) => String(name || '').trim().split(/\s+/))
    .filter(Boolean)

  if (parts.length === 0) return '?'
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
}

/** "Ada Lovelace" from the two stored name columns, in a single place. */
export function fullNameOf(user) {
  if (!user) return ''
  return [user.first_name, user.name].filter(Boolean).join(' ')
}
