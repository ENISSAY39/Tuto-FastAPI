import { useEffect, useState } from 'react'
import PageShell from '../components/PageShell.jsx'
import Pagination from '../components/Pagination.jsx'
import PortfolioCard from '../components/PortfolioCard.jsx'
import Alert from '../components/ui/Alert.jsx'
import Button from '../components/ui/Button.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import Field from '../components/ui/Field.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import { api } from '../lib/api.js'

/** Read the initial state from the address bar so a search stays shareable. */
function initialParams() {
  const params = new URLSearchParams(window.location.search)
  const page = Number.parseInt(params.get('page') ?? '1', 10)
  return {
    query: params.get('query') ?? '',
    page: Number.isNaN(page) || page < 1 ? 1 : page,
  }
}

/** Keep the address bar in step without reloading this document. */
function syncAddressBar(query, page) {
  const params = new URLSearchParams()
  if (query) params.set('query', query)
  if (page > 1) params.set('page', String(page))

  const search = params.toString()
  window.history.replaceState(null, '', search ? `?${search}` : window.location.pathname)
}

export default function PortfoliosPage() {
  const [{ query, page }, setSearchState] = useState(initialParams)
  // The text input is separate from the submitted query so typing does not
  // fire a request on every keystroke.
  const [draft, setDraft] = useState(query)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let cancelled = false
    const params = new URLSearchParams({ query, page: String(page) })

    api
      .get(`/portfolios?${params}`)
      .then((data) => {
        if (cancelled) return
        setResult(data)
        // The server clamps an out-of-range page, so the address bar records
        // the page it actually answered with rather than the one requested.
        syncAddressBar(data.query, data.current_page)
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    // An answer that arrives after the visitor changed page must not overwrite
    // the newer one.
    return () => {
      cancelled = true
    }
  }, [query, page, reloadKey])

  /**
   * Every navigation goes through here: the spinner is armed by the gesture
   * that triggers the request, never by the effect that performs it.
   */
  const goTo = (nextState) => {
    setLoading(true)
    setError('')
    setSearchState(nextState)
  }

  const handleSearch = (event) => {
    event.preventDefault()
    // A new search always restarts at the first page.
    goTo({ query: draft.trim(), page: 1 })
  }

  const clearSearch = () => {
    setDraft('')
    goTo({ query: '', page: 1 })
  }

  const retry = () => {
    setLoading(true)
    setError('')
    setReloadKey((key) => key + 1)
  }

  const portfolios = result?.portfolios ?? []

  return (
    <PageShell current="portfolios">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-ink-900">Portfolios</h1>
          <p className="mt-1 text-sm text-ink-500">
            {result
              ? `${result.total_portfolios} public portfolio${
                  result.total_portfolios === 1 ? '' : 's'
                }${query ? ` matching “${query}”` : ''}.`
              : 'Browse every published portfolio.'}
          </p>
        </div>

        <form onSubmit={handleSearch} className="flex w-full items-end gap-2 sm:w-80">
          <Field
            label="Search"
            type="search"
            placeholder="Search by last name…"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
          <Button type="submit">Search</Button>
        </form>
      </div>

      <div className="mt-8">
        {loading ? (
          <div className="flex items-center justify-center gap-3 py-20 text-sm text-ink-400">
            <Spinner className="h-5 w-5" />
            Loading portfolios…
          </div>
        ) : error ? (
          <Alert tone="error">
            {error}{' '}
            <button
              type="button"
              onClick={retry}
              className="cursor-pointer underline underline-offset-2"
            >
              Retry
            </button>
          </Alert>
        ) : portfolios.length === 0 ? (
          <EmptyState
            title={query ? 'No portfolio matches this search' : 'No portfolio published yet'}
            description={
              query
                ? 'Try another last name, or clear the search to see everyone.'
                : 'Portfolios appear here as soon as their owners create an account.'
            }
            action={
              query ? (
                <Button variant="ghost" onClick={clearSearch}>
                  Clear search
                </Button>
              ) : null
            }
          />
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2">
              {portfolios.map((portfolio) => (
                <PortfolioCard key={portfolio.id} portfolio={portfolio} />
              ))}
            </div>

            <Pagination
              page={result.current_page}
              totalPages={result.total_pages}
              hasPrevious={result.has_previous}
              hasNext={result.has_next}
              onChange={(nextPage) => goTo({ query, page: nextPage })}
            />
          </>
        )}
      </div>
    </PageShell>
  )
}
