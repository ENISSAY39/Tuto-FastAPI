import { getToken, clearSession } from './session.js'

/**
 * API client.
 *
 * Calls always use a relative path, so the same build works in dev (Vite
 * proxies /api to FastAPI) and in production (FastAPI serves both the API and
 * these pages). There is no API base URL to configure.
 */

const API_PREFIX = '/api'

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
  const token = auth ? getToken() : null
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(API_PREFIX + path, {
      method,
      headers,
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

  // A 401 while we were holding a token means it expired or was revoked:
  // drop it and send the user back to the login page. A 401 without a token
  // is just wrong credentials on the login form, and must be shown inline.
  if (response.status === 401 && token) {
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
