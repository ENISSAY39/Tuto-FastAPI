import { requireAuth } from '../lib/auth.js'
import { mountPage } from '../lib/mount.jsx'
import ProfilePage from '../pages/ProfilePage.jsx'

// The guard runs before React mounts, so the dashboard never flashes to a
// logged-out visitor before redirecting.
if (requireAuth()) {
  mountPage(ProfilePage)
}
