import { useState } from 'react'
import Avatar from './Avatar.jsx'
import GitHubIcon from './GitHubIcon.jsx'
import Logo from './Logo.jsx'
import Button, { LinkButton } from './ui/Button.jsx'
import { logout } from '../lib/auth.js'
import { getCurrentUser, isAuthenticated } from '../lib/session.js'
import { APP_NAME, REPO_URL } from '../lib/constants.js'
import { fullNameOf } from '../lib/format.js'

/**
 * One header for every page.
 *
 * Pages are separate documents, so the signed-in state is read from storage
 * on each load rather than held in a shared client-side store. The directory
 * link stays visible to everyone because the portfolio list is public.
 */
export default function SiteHeader({ current }) {
  const signedIn = isAuthenticated()
  const user = getCurrentUser()
  const [loggingOut, setLoggingOut] = useState(false)

  const handleLogout = async () => {
    setLoggingOut(true)
    await logout()
  }

  const linkClasses = (name) =>
    [
      'rounded-lg px-3 py-1.5 text-sm transition-colors',
      current === name
        ? 'bg-ink-900/10 text-ink-900'
        : 'text-ink-500 hover:bg-ink-900/5 hover:text-ink-700',
    ].join(' ')

  return (
    <header className="sticky top-0 z-40 border-b border-ink-900/10 bg-surface-950/80 backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-6xl items-center gap-4 px-4 sm:px-6">
        <a href="/" className="flex items-center gap-2.5">
          <Logo />
          <span className="hidden text-sm font-semibold text-ink-900 sm:block">{APP_NAME}</span>
        </a>

        <nav className="flex items-center gap-1">
          <a href="/portfolios.html" className={linkClasses('portfolios')}>
            Portfolios
          </a>
          {signedIn && (
            <a href="/profile.html" className={linkClasses('profile')}>
              My portfolio
            </a>
          )}
        </nav>

        <div className="ml-auto flex items-center gap-3">
          {signedIn ? (
            <>
              {user && (
                <a
                  href="/profile.html"
                  className="flex items-center gap-2.5 no-underline"
                  title={user.mail}
                >
                  <Avatar firstName={user.first_name} name={user.name} size="sm" />
                  <div className="hidden leading-tight sm:block">
                    <p className="text-sm text-ink-700">{fullNameOf(user)}</p>
                    <p className="text-xs text-ink-400">{user.mail}</p>
                  </div>
                </a>
              )}
              <Button variant="ghost" size="sm" onClick={handleLogout} loading={loggingOut}>
                Log out
              </Button>
            </>
          ) : (
            <>
              <a
                href={REPO_URL}
                target="_blank"
                rel="noreferrer noopener"
                title="Source code on GitHub"
                aria-label="Source code on GitHub"
                className="mr-1 hidden rounded-lg p-2 text-ink-500 transition-colors hover:bg-ink-900/5 hover:text-ink-900 sm:block"
              >
                <GitHubIcon className="h-5 w-5" />
              </a>
              <LinkButton href="/login.html" variant="ghost" size="sm">
                Log in
              </LinkButton>
              <LinkButton href="/signup.html" size="sm">
                Sign up
              </LinkButton>
            </>
          )}
        </div>
      </div>
    </header>
  )
}
