import { redirectIfAuthenticated } from '../lib/auth.js'
import { mountPage } from '../lib/mount.jsx'
import LoginPage from '../pages/LoginPage.jsx'

if (redirectIfAuthenticated()) {
  mountPage(LoginPage)
}
