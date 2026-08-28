import { mountPage } from '../lib/mount.jsx'
import HomePage from '../pages/HomePage.jsx'

// The landing page is public and stays readable when signed in, so it carries
// no guard: it adapts its call to action instead of redirecting.
mountPage(HomePage)
