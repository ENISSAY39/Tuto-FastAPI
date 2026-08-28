import { useState } from 'react'
import Alert from './ui/Alert.jsx'
import Button from './ui/Button.jsx'
import Field, { TextareaField } from './ui/Field.jsx'
import Modal from './ui/Modal.jsx'
import { FIELD_LIMITS } from '../lib/constants.js'
import { toDateInputValue } from '../lib/format.js'

/**
 * Create and edit share this form, exactly as the two server-rendered
 * templates it replaces did: `experience` is null when adding, and the record
 * itself when editing.
 *
 * The modal is rendered only while open (the parent unmounts it on close), so
 * the fields reset simply by being mounted again — no effect needed to clear
 * them.
 */
export default function ExperienceFormModal({ experience, onClose, onSubmit }) {
  const editing = Boolean(experience)

  const [title, setTitle] = useState(experience?.title ?? '')
  const [company, setCompany] = useState(experience?.company ?? '')
  const [description, setDescription] = useState(experience?.description ?? '')
  const [dateStart, setDateStart] = useState(toDateInputValue(experience?.date_start))
  const [dateEnd, setDateEnd] = useState(toDateInputValue(experience?.date_end))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')

    try {
      // The server re-runs every rule and owns the messages shown here, so the
      // form does not duplicate them client-side.
      await onSubmit({
        title: title.trim(),
        company: company.trim(),
        description: description.trim(),
        date_start: dateStart,
        date_end: dateEnd,
      })
      onClose()
    } catch (submitError) {
      setError(submitError.message)
      setSaving(false)
    }
  }

  return (
    <Modal
      open
      onClose={saving ? undefined : onClose}
      title={editing ? 'Edit experience' : 'Add an experience'}
      description="A role you held, with the period it covered."
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" form="experience-form" loading={saving}>
            {editing ? 'Save changes' : 'Add experience'}
          </Button>
        </>
      }
    >
      <form id="experience-form" onSubmit={handleSubmit} className="space-y-4">
        <Alert tone="error">{error}</Alert>

        <Field
          label="Title"
          placeholder="Software engineering intern"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          maxLength={FIELD_LIMITS.title}
          autoFocus
          required
        />

        <Field
          label="Company"
          placeholder="Acme"
          value={company}
          onChange={(event) => setCompany(event.target.value)}
          maxLength={FIELD_LIMITS.company}
          required
        />

        <div className="grid gap-4 sm:grid-cols-2">
          <Field
            label="Start date"
            type="date"
            value={dateStart}
            onChange={(event) => setDateStart(event.target.value)}
            required
          />
          <Field
            label="End date"
            type="date"
            value={dateEnd}
            onChange={(event) => setDateEnd(event.target.value)}
            required
          />
        </div>

        <TextareaField
          label="Description"
          placeholder="What you worked on, and what you achieved."
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={FIELD_LIMITS.description}
          required
        />
      </form>
    </Modal>
  )
}
