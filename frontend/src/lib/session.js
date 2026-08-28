/**
 * Session storage.
 *
 * The JWT lives in localStorage and is attached automatically by the API
 * client, so nothing token-related is ever shown in the UI.
 *
 * Every access is wrapped: localStorage throws in private-mode / blocked-cookie
 * setups, and a storage failure must never take the whole page down.
 */

const TOKEN_KEY = 'eportfolio.token'
const USER_KEY = 'eportfolio.user'

export function getToken() {
  try {
    return window.localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function getCurrentUser() {
  try {
    const raw = window.localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function saveSession(token, user) {
  try {
    window.localStorage.setItem(TOKEN_KEY, token)
    window.localStorage.setItem(USER_KEY, JSON.stringify(user ?? null))
  } catch {
    /* session simply won't survive a reload — not worth crashing over */
  }
}

/** Refresh the cached profile after the user edits it, keeping the token. */
export function saveCurrentUser(user) {
  try {
    window.localStorage.setItem(USER_KEY, JSON.stringify(user ?? null))
  } catch {
    /* ignore */
  }
}

export function clearSession() {
  try {
    window.localStorage.removeItem(TOKEN_KEY)
    window.localStorage.removeItem(USER_KEY)
  } catch {
    /* ignore */
  }
}

export function isAuthenticated() {
  return Boolean(getToken())
}
