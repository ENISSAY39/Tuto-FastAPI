/**
 * Reading a cookie from `document.cookie` — needed for exactly two of them,
 * both deliberately readable: the CSRF token the client has to echo back in a
 * header, and the flag saying a session exists. The credential itself is
 * HTTP-only and never appears here.
 */
export function readCookie(name) {
  const prefix = `${encodeURIComponent(name)}=`

  for (const part of document.cookie.split('; ')) {
    if (part.startsWith(prefix)) {
      return decodeURIComponent(part.slice(prefix.length))
    }
  }
  return null
}
