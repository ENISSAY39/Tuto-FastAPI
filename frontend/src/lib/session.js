import { readCookie } from './cookies.js'

/**
 * Session state, as seen from the browser.
 *
 * The access token is NOT here: it lives in an HTTP-only cookie that scripts
 * cannot read, so a script injection on the page cannot carry the credential
 * away. What this module keeps is the cached profile — a name and an email,
 * used to draw the header without waiting for a request — and a way to ask
 * whether a session is currently open.
 *
 * Every localStorage access is wrapped: it throws in private-mode /
 * blocked-cookie setups, and a storage failure must never take the page down.
 */

const USER_KEY = 'eportfolio.user'

// Set alongside the credential, and expiring with it. It grants nothing:
// forging it only produces a request the API answers with 401.
const SESSION_HINT_COOKIE = 'signed_in'

export function getCurrentUser() {
  try {
    const raw = window.localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

/** Cache the profile the header displays, after login or after an edit. */
export function saveCurrentUser(user) {
  try {
    window.localStorage.setItem(USER_KEY, JSON.stringify(user ?? null))
  } catch {
    /* the header will simply fall back to no profile — not worth crashing over */
  }
}

export function clearSession() {
  try {
    window.localStorage.removeItem(USER_KEY)
  } catch {
    /* ignore */
  }
}

/**
 * Whether a session is open, answered synchronously so a page guard can run
 * before React mounts. It reflects the hint cookie, which the server expires
 * at the same moment as the token — so this cannot claim a session outlived
 * the credential behind it.
 */
export function isAuthenticated() {
  return readCookie(SESSION_HINT_COOKIE) === '1'
}
