import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import ToastProvider from '../components/ui/Toast.jsx'
import '../styles/tailwind.css'

/**
 * Every HTML page mounts its own React root through this helper, so the
 * shared providers stay in one place instead of being repeated in each entry.
 */
export function mountPage(Page) {
  const container = document.getElementById('root')
  if (!container) throw new Error('#root element is missing from the page')

  createRoot(container).render(
    <StrictMode>
      <ToastProvider>
        <Page />
      </ToastProvider>
    </StrictMode>,
  )
}
