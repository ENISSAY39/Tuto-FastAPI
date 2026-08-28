import Logo from './Logo.jsx'
import { APP_NAME } from '../lib/constants.js'

/** Centered layout shared by the login and signup pages. */
export default function AuthLayout({ title, subtitle, children, footer, wide = false }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <a href="/" className="mb-8 flex items-center gap-3">
        <Logo className="h-10 w-10" />
        <span className="text-lg font-semibold text-slate-100">{APP_NAME}</span>
      </a>

      <div
        className={[
          'w-full rounded-xl border border-white/8 bg-surface-900/80 p-6 shadow-xl shadow-black/40 sm:p-8',
          wide ? 'max-w-xl' : 'max-w-md',
        ].join(' ')}
      >
        <h1 className="text-xl font-semibold text-slate-100">{title}</h1>
        {subtitle && <p className="mt-1.5 text-sm text-slate-400">{subtitle}</p>}
        <div className="mt-6">{children}</div>
      </div>

      {footer && <div className="mt-6 text-sm text-slate-400">{footer}</div>}
    </div>
  )
}
