import SiteHeader from './SiteHeader.jsx'
import { APP_NAME } from '../lib/constants.js'

/** Common chrome shared by every page except the landing and auth screens. */
export default function PageShell({ current, children }) {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader current={current} />
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6">{children}</main>
      <footer className="border-t border-white/8 py-6">
        <p className="mx-auto max-w-6xl px-4 text-xs text-slate-600 sm:px-6">
          {APP_NAME} — FastAPI, SQLModel &amp; React
        </p>
      </footer>
    </div>
  )
}
