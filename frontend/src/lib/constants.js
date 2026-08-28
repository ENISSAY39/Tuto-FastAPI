export const APP_NAME = 'e-Portfolio'

export const REPO_URL = 'https://github.com/ENISSAY39/e-portfolio-fastapi'

export const REPO_LABEL = 'ENISSAY39/e-portfolio-fastapi'

/** Mirrors PORTFOLIOS_PER_PAGE in routers/auth.py, for the pager wording. */
export const PORTFOLIOS_PER_PAGE = 10

/** Mirrors the limits enforced by core/validation.py on the server. */
export const FIELD_LIMITS = {
  name: 100,
  firstName: 100,
  title: 150,
  company: 150,
  schoolName: 150,
  major: 150,
  description: 3000,
}

export const PASSWORD_HINT =
  'At least 10 characters, with a lowercase letter, an uppercase letter and a digit.'
