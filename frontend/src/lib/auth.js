import { api } from './api.js'
import { saveCurrentUser, clearSession, isAuthenticated } from './session.js'

/**
 * Logging in returns the profile; the credential itself never reaches this
 * code, because the server sends it as an HTTP-only cookie.
 */
export async function login(mail, password) {
  const user = await api.post('/login', { mail, password }, { auth: false })
  saveCurrentUser(user)
  return user
}

/**
 * The signup endpoint only creates the account, it does not open a session,
 * so we log the new user straight in to avoid making them type it all again.
 */
export async function signup(account) {
  await api.post('/signup', account, { auth: false })
  return login(account.mail, account.password)
}

/**
 * Only the server can end the session, since the cookie carrying it is out of
 * reach of this code. If the call fails the visitor still leaves the app, but
 * their session is genuinely still open — hence the reload rather than a
 * silent client-side "logout".
 */
export async function logout() {
  try {
    await api.post('/logout')
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
