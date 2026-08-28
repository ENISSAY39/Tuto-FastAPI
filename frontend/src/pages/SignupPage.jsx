import { useState } from 'react'
import AuthLayout from '../components/AuthLayout.jsx'
import Alert from '../components/ui/Alert.jsx'
import Button from '../components/ui/Button.jsx'
import Field from '../components/ui/Field.jsx'
import { signup } from '../lib/auth.js'
import { FIELD_LIMITS, PASSWORD_HINT } from '../lib/constants.js'

const EMPTY_ACCOUNT = {
  first_name: '',
  name: '',
  birth_date: '',
  mail: '',
  phone: '',
  password: '',
}

export default function SignupPage() {
  const [account, setAccount] = useState(EMPTY_ACCOUNT)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const update = (field) => (event) =>
    setAccount((current) => ({ ...current, [field]: event.target.value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      // Signup logs the new account straight in, so the visitor lands on their
      // (still empty) portfolio instead of typing their password twice.
      await signup({
        ...account,
        first_name: account.first_name.trim(),
        name: account.name.trim(),
        mail: account.mail.trim(),
        phone: account.phone.trim(),
      })
      window.location.href = '/profile.html'
    } catch (signupError) {
      // Every rule is enforced server-side; its message is what is shown here.
      setError(signupError.message)
      setSubmitting(false)
    }
  }

  return (
    <AuthLayout
      wide
      title="Create your portfolio"
      subtitle="A few details about you, then you can start adding entries."
      footer={
        <>
          Already registered?{' '}
          <a href="/login.html" className="text-accent-600 hover:text-accent-700">
            Log in
          </a>
        </>
      }
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <Alert tone="error">{error}</Alert>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="First name"
            autoComplete="given-name"
            placeholder="Ada"
            value={account.first_name}
            onChange={update('first_name')}
            maxLength={FIELD_LIMITS.firstName}
            autoFocus
            required
          />
          <Field
            label="Last name"
            autoComplete="family-name"
            placeholder="Lovelace"
            value={account.name}
            onChange={update('name')}
            maxLength={FIELD_LIMITS.name}
            required
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Date of birth"
            type="date"
            autoComplete="bday"
            value={account.birth_date}
            onChange={update('birth_date')}
            required
          />
          <Field
            label="Phone"
            type="tel"
            autoComplete="tel"
            placeholder="+33612345678"
            value={account.phone}
            onChange={update('phone')}
            required
          />
        </div>

        <Field
          label="Email"
          type="email"
          autoComplete="email"
          placeholder="you@example.com"
          value={account.mail}
          onChange={update('mail')}
          required
        />

        <Field
          label="Password"
          type="password"
          autoComplete="new-password"
          placeholder="••••••••"
          hint={PASSWORD_HINT}
          value={account.password}
          onChange={update('password')}
          required
        />

        <Button type="submit" className="w-full" loading={submitting}>
          Create my account
        </Button>
      </form>
    </AuthLayout>
  )
}
