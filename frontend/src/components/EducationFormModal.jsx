import { useState } from 'react'
import Alert from './ui/Alert.jsx'
import Button from './ui/Button.jsx'
import Field, { TextareaField } from './ui/Field.jsx'
import Modal from './ui/Modal.jsx'
import { FIELD_LIMITS } from '../lib/constants.js'
import { toDateInputValue } from '../lib/format.js'

/**
 * Create and edit share this form: `education` is null when adding, and the
 * record itself when editing.
 */
export default function EducationFormModal({ education, onClose, onSubmit }) {
  const editing = Boolean(education)

  const [schoolName, setSchoolName] = useState(education?.school_name ?? '')
  const [major, setMajor] = useState(education?.major ?? '')
  const [description, setDescription] = useState(education?.description ?? '')
  const [dateStart, setDateStart] = useState(toDateInputValue(education?.date_start))
  const [dateEnd, setDateEnd] = useState(toDateInputValue(education?.date_end))
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setSaving(true)
    setError('')

    try {
      await onSubmit({
        school_name: schoolName.trim(),
        major: major.trim(),
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
      title={editing ? 'Edit education' : 'Add an education entry'}
      description="A degree or programme, with the period it covered."
      footer={
        <>
          <Button variant="ghost" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" form="education-form" loading={saving}>
            {editing ? 'Save changes' : 'Add education'}
          </Button>
        </>
      }
    >
      <form id="education-form" onSubmit={handleSubmit} className="space-y-4">
        <Alert tone="error">{error}</Alert>

        <Field
          label="School"
          placeholder="EPF Engineering School"
          value={schoolName}
          onChange={(event) => setSchoolName(event.target.value)}
          maxLength={FIELD_LIMITS.schoolName}
          autoFocus
          required
        />

        <Field
          label="Major"
          placeholder="Computer Science"
          value={major}
          onChange={(event) => setMajor(event.target.value)}
          maxLength={FIELD_LIMITS.major}
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
          placeholder="What the programme covered, and what you specialised in."
          value={description}
          onChange={(event) => setDescription(event.target.value)}
          maxLength={FIELD_LIMITS.description}
          required
        />
      </form>
    </Modal>
  )
}
