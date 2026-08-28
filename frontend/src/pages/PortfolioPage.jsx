import { useEffect, useMemo, useState } from 'react'
import PageShell from '../components/PageShell.jsx'
import ProfileCard from '../components/ProfileCard.jsx'
import TimelineEntry from '../components/TimelineEntry.jsx'
import Alert from '../components/ui/Alert.jsx'
import { LinkButton } from '../components/ui/Button.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import { api } from '../lib/api.js'

/** The portfolio to display is named by the query string: /portfolio.html?id=7 */
function requestedPortfolioId() {
  const id = Number.parseInt(new URLSearchParams(window.location.search).get('id') ?? '', 10)
  return Number.isNaN(id) ? null : id
}

function Section({ title, entries, emptyLabel, subtitleOf, titleOf }) {
  return (
    <section className="mt-10">
      <h2 className="text-sm font-semibold tracking-wide text-ink-700 uppercase">{title}</h2>

      {entries.length === 0 ? (
        <p className="mt-4 rounded-xl border border-dashed border-ink-900/12 px-5 py-8 text-center text-sm text-ink-400">
          {emptyLabel}
        </p>
      ) : (
        <div className="mt-4 grid gap-4">
          {entries.map((entry) => (
            <TimelineEntry
              key={entry.id}
              title={titleOf(entry)}
              subtitle={subtitleOf(entry)}
              entry={entry}
            />
          ))}
        </div>
      )}
    </section>
  )
}

export default function PortfolioPage() {
  // The address of this document never changes while it is open, so the
  // requested id is read once and the initial state derived from it. A missing
  // id is therefore an error the first render already knows about, with no
  // request to make and nothing for the effect to correct afterwards.
  const portfolioId = useMemo(() => requestedPortfolioId(), [])

  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(portfolioId !== null)
  const [error, setError] = useState(
    portfolioId === null ? 'This portfolio address is not valid.' : '',
  )

  useEffect(() => {
    if (portfolioId === null) return undefined

    let cancelled = false

    api
      .get(`/portfolios/${portfolioId}`)
      .then((data) => {
        if (!cancelled) setPortfolio(data)
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [portfolioId])

  if (loading) {
    return (
      <PageShell current="portfolios">
        <div className="flex items-center justify-center gap-3 py-20 text-sm text-ink-400">
          <Spinner className="h-5 w-5" />
          Loading portfolio…
        </div>
      </PageShell>
    )
  }

  if (error || !portfolio) {
    return (
      <PageShell current="portfolios">
        <EmptyState
          title="Portfolio unavailable"
          description={error || 'This portfolio does not exist.'}
          action={
            <LinkButton href="/portfolios.html" variant="ghost">
              Back to the directory
            </LinkButton>
          }
        />
      </PageShell>
    )
  }

  return (
    <PageShell current="portfolios">
      <ProfileCard user={portfolio.user} />

      <Section
        title="Experience"
        entries={portfolio.experiences}
        emptyLabel="No experience published yet."
        titleOf={(entry) => entry.title}
        subtitleOf={(entry) => entry.company}
      />

      <Section
        title="Education"
        entries={portfolio.educations}
        emptyLabel="No education published yet."
        titleOf={(entry) => entry.school_name}
        subtitleOf={(entry) => entry.major}
      />

      <Alert tone="info" className="mt-10">
        This portfolio is public: anyone holding its address can read it.
      </Alert>
    </PageShell>
  )
}
