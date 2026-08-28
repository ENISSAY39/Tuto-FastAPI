import { api } from './api.js'
import { saveSession, clearSession, isAuthenticated } from './session.js'

export async function login(mail, password) {
  const data = await api.post('/login', { mail, password }, { auth: false })
  saveSession(data.token, data.user)
  return data.user
}

/**
 * The signup endpoint only creates the account, it does not return a token,
 * so we log the new user straight in to avoid making them type it all again.
 */
export async function signup(account) {
  await api.post('/signup', account, { auth: false })
  return login(account.mail, account.password)
}

export async function logout() {
  try {
    await api.post('/logout')
  } catch {
    // A failing logout call must not trap the user in the app: the token is
    // dropped client-side either way.
  } finally {
    clearSession()
    window.location.href = '/login.html'
  }
}

/**
 * Page guards. They run before React mounts (see src/entries/*), so a
 * protected page never flashes its content to a logged-out visitor.
 * Return value says "keep going": false means a redirect is under way.
 */
export function requireAuth() {
  if (isAuthenticated()) return true
  const next = encodeURIComponent(window.location.pathname + window.location.search)
  window.location.replace(`/login.html?next=${next}`)
  return false
}

export function redirectIfAuthenticated(target = '/profile.html') {
  if (!isAuthenticated()) return true
  window.location.replace(target)
  return false
}
