import GitHubIcon from '../components/GitHubIcon.jsx'
import Logo from '../components/Logo.jsx'
import { LinkButton } from '../components/ui/Button.jsx'
import { APP_NAME, REPO_LABEL, REPO_URL } from '../lib/constants.js'
import { isAuthenticated } from '../lib/session.js'

const FEATURES = [
  {
    title: 'Your portfolio',
    description:
      'Collect your experience and your education in one page, kept up to date from a single dashboard.',
  },
  {
    title: 'Public by design',
    description:
      'Every portfolio has a shareable address, and the directory is searchable without an account.',
  },
  {
    title: 'Yours alone to edit',
    description:
      'Entries are tied to their owner server-side: a signed token decides what you may change.',
  },
]

/**
 * Landing page. It stays readable for a signed-in visitor rather than
 * redirecting: the site is public, so its front door is a page people share.
 */
export default function HomePage() {
  const signedIn = isAuthenticated()

  return (
    <div className="flex min-h-screen flex-col">
      <header className="mx-auto flex h-16 w-full max-w-6xl items-center px-4 sm:px-6">
        <a href="/" className="flex items-center gap-2.5">
          <Logo />
          <span className="text-sm font-semibold text-ink-900">{APP_NAME}</span>
        </a>

        <div className="ml-auto flex items-center gap-2">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer noopener"
            title="Source code on GitHub"
            aria-label="Source code on GitHub"
            className="mr-1 rounded-lg p-2 text-ink-500 transition-colors hover:bg-ink-900/5 hover:text-ink-900"
          >
            <GitHubIcon className="h-5 w-5" />
          </a>

          {signedIn ? (
            <LinkButton href="/profile.html" size="sm">
              My portfolio
            </LinkButton>
          ) : (
            <>
              <LinkButton href="/login.html" variant="ghost" size="sm">
                Log in
              </LinkButton>
              <LinkButton href="/signup.html" size="sm">
                Sign up
              </LinkButton>
            </>
          )}
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl flex-1 px-4 sm:px-6">
        <section className="py-20 text-center sm:py-28">
          <p className="text-xs font-medium tracking-[0.2em] text-accent-600 uppercase">
            FastAPI · SQLModel · React
          </p>
          <h1 className="mx-auto mt-4 max-w-3xl text-4xl font-semibold text-balance text-ink-900 sm:text-5xl">
            Your experience and education, on one shareable page.
          </h1>
          <p className="mx-auto mt-5 max-w-xl text-base text-pretty text-ink-500">
            Create an account, add where you studied and where you worked, and publish a portfolio
            anyone can read at a stable address.
          </p>

          <div className="mt-9 flex flex-wrap items-center justify-center gap-3">
            {signedIn ? (
              <LinkButton href="/profile.html" size="lg">
                Go to my portfolio
              </LinkButton>
            ) : (
              <LinkButton href="/signup.html" size="lg">
                Create my portfolio
              </LinkButton>
            )}
            <LinkButton href="/portfolios.html" variant="ghost" size="lg">
              Browse portfolios
            </LinkButton>
          </div>
        </section>

        <section className="grid gap-4 sm:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="rounded-xl border border-ink-900/10 bg-surface-900/60 p-5"
            >
              <h2 className="text-sm font-semibold text-ink-900">{feature.title}</h2>
              <p className="mt-2 text-sm text-ink-500">{feature.description}</p>
            </div>
          ))}
        </section>

        <section className="py-20">
          <div className="rounded-xl border border-ink-900/10 bg-surface-900/60 p-8 text-center sm:p-10">
            <span className="inline-flex h-11 w-11 items-center justify-center rounded-full bg-surface-800 text-ink-700">
              <GitHubIcon className="h-5 w-5" />
            </span>

            <h2 className="mt-4 text-xl font-semibold text-ink-900">
              Open source — contributions welcome
            </h2>

            <p className="mx-auto mt-3 max-w-xl text-sm text-pretty text-ink-500">
              This is a student project, and the repository is public. If you want to collaborate,
              suggest a feature, or report something that does not work, issues and pull requests
              are very welcome.
            </p>

            <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
              <LinkButton href={REPO_URL} target="_blank" rel="noreferrer noopener">
                <GitHubIcon className="h-4 w-4" />
                View the repository
              </LinkButton>
              <LinkButton
                href={`${REPO_URL}/issues/new`}
                target="_blank"
                rel="noreferrer noopener"
                variant="ghost"
              >
                Open an issue
              </LinkButton>
            </div>

            <p className="mt-5 font-mono text-xs break-all text-ink-400">{REPO_LABEL}</p>
          </div>
        </section>
      </main>

      <footer className="border-t border-ink-900/10 py-6">
        <p className="mx-auto max-w-6xl px-4 text-xs text-ink-400 sm:px-6">
          {APP_NAME} — FastAPI, SQLModel &amp; React
        </p>
      </footer>
    </div>
  )
}
