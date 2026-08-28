import { redirectIfAuthenticated } from '../lib/auth.js'
import { mountPage } from '../lib/mount.jsx'
import SignupPage from '../pages/SignupPage.jsx'

if (redirectIfAuthenticated()) {
  mountPage(SignupPage)
}
