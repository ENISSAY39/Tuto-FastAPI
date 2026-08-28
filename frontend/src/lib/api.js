import { readCookie } from './cookies.js'
import { clearSession } from './session.js'

/**
 * API client.
 *
 * Calls always use a relative path, so the same build works in dev (Vite
 * proxies /api to FastAPI) and in production (FastAPI serves both the API and
 * these pages). There is no API base URL to configure.
 *
 * Authentication rides on cookies the browser attaches by itself, so nothing
 * here handles a credential. What the client must do is prove the request came
 * from this page: it copies the CSRF cookie into a header, which a cross-site
 * caller can neither read nor set.
 */

const API_PREFIX = '/api'
const CSRF_COOKIE = 'csrf_token'
const CSRF_HEADER = 'X-CSRF-Token'
const SAFE_METHODS = new Set(['GET', 'HEAD', 'OPTIONS'])

export class ApiError extends Error {
  constructor(message, status, payload) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.payload = payload
  }
}

function redirectToLogin(reason) {
  const next = encodeURIComponent(window.location.pathname + window.location.search)
  window.location.replace(`/login.html?reason=${reason}&next=${next}`)
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }

  if (!SAFE_METHODS.has(method)) {
    const csrfToken = readCookie(CSRF_COOKIE)
    if (csrfToken) headers[CSRF_HEADER] = csrfToken
  }

  let response
  try {
    response = await fetch(API_PREFIX + path, {
      method,
      headers,
      // The session cookies are same-origin; being explicit documents that
      // this client depends on them.
      credentials: 'same-origin',
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError('Cannot reach the server. Is the backend running?', 0, null)
  }

  // The API answers JSON everywhere, but a 500 behind a proxy can still return
  // HTML — parse defensively instead of letting response.json() throw.
  let payload = null
  const text = await response.text()
  if (text) {
    try {
      payload = JSON.parse(text)
    } catch {
      payload = null
    }
  }

  // A 401 on a call that expected a session means it expired or was revoked:
  // drop the cached profile and send the user back to the login page. A 401 on
  // the login call itself is just wrong credentials, and must be shown inline.
  if (response.status === 401 && auth) {
    clearSession()
    redirectToLogin('expired')
    throw new ApiError('Your session has expired.', 401, payload)
  }

  if (!response.ok) {
    throw new ApiError(
      payload?.error || `Request failed (${response.status})`,
      response.status,
      payload,
    )
  }

  return payload
}

export const api = {
  get: (path) => request(path),
  post: (path, body, options) => request(path, { method: 'POST', body, ...options }),
  put: (path, body, options) => request(path, { method: 'PUT', body, ...options }),
  del: (path, options) => request(path, { method: 'DELETE', ...options }),
}
