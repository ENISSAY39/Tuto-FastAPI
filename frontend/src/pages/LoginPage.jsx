import { useState } from 'react'
import AuthLayout from '../components/AuthLayout.jsx'
import Alert from '../components/ui/Alert.jsx'
import Button from '../components/ui/Button.jsx'
import Field from '../components/ui/Field.jsx'
import { login } from '../lib/auth.js'

function safeNextTarget() {
  const next = new URLSearchParams(window.location.search).get('next')
  // Only accept same-site paths, never an absolute URL from the query string.
  if (next && next.startsWith('/') && !next.startsWith('//')) return next
  return '/profile.html'
}

export default function LoginPage() {
  const [mail, setMail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const reason = new URLSearchParams(window.location.search).get('reason')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      await login(mail.trim(), password)
      window.location.href = safeNextTarget()
    } catch (loginError) {
      // The server answers one generic message for both an unknown address and
      // a wrong password, so nothing here reveals which accounts exist.
      setError(loginError.message)
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout
      title="Welcome back"
      subtitle="Log in to manage your portfolio."
      footer={
        <>
          No account yet?{' '}
          <a href="/signup.html" className="text-accent-600 hover:text-accent-700">
            Create one
          </a>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {reason === 'expired' && (
          <Alert tone="warning">Your session expired. Please log in again.</Alert>
        )}
        <Alert tone="error">{error}</Alert>

        <Field
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={mail}
          onChange={(event) => setMail(event.target.value)}
          autoFocus
          required
        />

        <Field
          label="Password"
          type="password"
          autoComplete="current-password"
          placeholder="••••••••"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />

        <Button type="submit" className="w-full" loading={submitting}>
          Log in
        </Button>
      </form>
    </AuthLayout>
  )
}
