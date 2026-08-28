import Avatar from './Avatar.jsx'
import { LinkButton } from './ui/Button.jsx'

/** One entry of the public directory. */
export default function PortfolioCard({ portfolio }) {
  return (
    <article className="flex items-center gap-4 rounded-xl border border-ink-900/10 bg-surface-900/80 p-5 transition-colors hover:border-ink-900/20">
      <Avatar firstName={portfolio.first_name} name={portfolio.name} />

      <div className="min-w-0 flex-1">
        <h3 className="truncate text-base font-semibold text-ink-900">
          {portfolio.first_name} {portfolio.name}
        </h3>
        <p className="mt-0.5 text-sm text-ink-400">Public portfolio</p>
      </div>

      <LinkButton size="sm" variant="ghost" href={`/portfolio.html?id=${portfolio.id}`}>
        View
      </LinkButton>
    </article>
  )
}
