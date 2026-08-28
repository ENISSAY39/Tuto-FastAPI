import Avatar from './Avatar.jsx'
import Card from './ui/Card.jsx'
import { fullNameOf } from '../lib/format.js'

function ContactRow({ label, value, href }) {
  return (
    <div className="min-w-0">
      <p className="text-xs font-medium text-slate-500 uppercase">{label}</p>
      {href ? (
        <a
          href={href}
          className="mt-0.5 block truncate text-sm text-accent-400 hover:text-accent-300"
        >
          {value}
        </a>
      ) : (
        <p className="mt-0.5 truncate text-sm text-slate-200">{value}</p>
      )}
    </div>
  )
}

/**
 * Identity header shared by the owner's dashboard and the public portfolio.
 * Both showed the same contact details before this rewrite, so the component
 * does not branch on who is looking.
 */
export default function ProfileCard({ user, actions }) {
  return (
    <Card className="p-6 sm:p-8">
      <div className="flex flex-wrap items-start gap-5">
        <Avatar firstName={user.first_name} name={user.name} size="lg" />

        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-semibold text-balance text-slate-50">
            {fullNameOf(user)}
          </h1>
          <p className="mt-1 text-sm text-slate-400">{user.age} years old</p>
        </div>

        {actions && <div className="flex shrink-0 items-center gap-2">{actions}</div>}
      </div>

      <div className="mt-6 grid gap-4 border-t border-white/8 pt-5 sm:grid-cols-2">
        <ContactRow label="Email" value={user.mail} href={`mailto:${user.mail}`} />
        <ContactRow label="Phone" value={user.phone} href={`tel:${user.phone}`} />
      </div>
    </Card>
  )
}
