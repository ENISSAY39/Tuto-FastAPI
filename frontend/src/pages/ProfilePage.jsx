import { useCallback, useEffect, useState } from 'react'
import EducationFormModal from '../components/EducationFormModal.jsx'
import ExperienceFormModal from '../components/ExperienceFormModal.jsx'
import PageShell from '../components/PageShell.jsx'
import ProfileCard from '../components/ProfileCard.jsx'
import TimelineEntry from '../components/TimelineEntry.jsx'
import Alert from '../components/ui/Alert.jsx'
import Button, { LinkButton } from '../components/ui/Button.jsx'
import ConfirmDialog from '../components/ui/ConfirmDialog.jsx'
import EmptyState from '../components/ui/EmptyState.jsx'
import Spinner from '../components/ui/Spinner.jsx'
import { useToast } from '../components/ui/toastContext.js'
import { api } from '../lib/api.js'
import { saveCurrentUser } from '../lib/session.js'

/**
 * The two collections behave identically, so their differences are described
 * once here instead of being spelled out twice in the page body.
 */
const SECTIONS = {
  experience: {
    title: 'Experience',
    endpoint: '/experiences',
    addLabel: 'Add experience',
    emptyTitle: 'No experience yet',
    emptyDescription: 'Add the roles you held so visitors can see your track record.',
    titleOf: (entry) => entry.title,
    subtitleOf: (entry) => entry.company,
    nameOf: (entry) => entry.title,
  },
  education: {
    title: 'Education',
    endpoint: '/educations',
    addLabel: 'Add education',
    emptyTitle: 'No education yet',
    emptyDescription: 'Add the degrees and programmes you completed.',
    titleOf: (entry) => entry.school_name,
    subtitleOf: (entry) => entry.major,
    nameOf: (entry) => entry.school_name,
  },
}

export default function ProfilePage() {
  const toast = useToast()

  const [portfolio, setPortfolio] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // `null` means closed; an object means open, carrying the record being
  // edited (or null when adding).
  const [experienceForm, setExperienceForm] = useState(null)
  const [educationForm, setEducationForm] = useState(null)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleting, setDeleting] = useState(false)

  const load = useCallback(async () => {
    const data = await api.get('/me')
    setPortfolio(data)
    // Keep the cached profile the header reads in step with the server.
    saveCurrentUser(data.user)
    return data
  }, [])

  useEffect(() => {
    let cancelled = false

    // Inlined rather than calling load(), so no state is written after this
    // page unmounts mid-request.
    api
      .get('/me')
      .then((data) => {
        if (cancelled) return
        setPortfolio(data)
        saveCurrentUser(data.user)
      })
      .catch((loadError) => {
        if (!cancelled) setError(loadError.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  /** Create or update, then reload so the ordering stays the server's. */
  const submitEntry = (kind) => async (values) => {
    const section = SECTIONS[kind]
    const editing = kind === 'experience' ? experienceForm?.entry : educationForm?.entry

    if (editing) {
      await api.put(`${section.endpoint}/${editing.id}`, values)
    } else {
      await api.post(section.endpoint, values)
    }

    await load()
    toast.success(editing ? `${section.title} updated.` : `${section.title} added.`)
  }

  const handleDelete = async () => {
    const section = SECTIONS[pendingDelete.kind]
    setDeleting(true)

    try {
      await api.del(`${section.endpoint}/${pendingDelete.entry.id}`)
      setPendingDelete(null)
      await load()
      toast.success(`${section.title} deleted.`)
    } catch (deleteError) {
      toast.error(deleteError.message)
    } finally {
      setDeleting(false)
    }
  }

  if (loading) {
    return (
      <PageShell current="profile">
        <div className="flex items-center justify-center gap-3 py-20 text-sm text-ink-400">
          <Spinner className="h-5 w-5" />
          Loading your portfolio…
        </div>
      </PageShell>
    )
  }

  if (error || !portfolio) {
    return (
      <PageShell current="profile">
        <Alert tone="error">{error || 'Your portfolio could not be loaded.'}</Alert>
      </PageShell>
    )
  }

  const renderSection = (kind, entries, openForm) => {
    const section = SECTIONS[kind]

    return (
      <section className="mt-10">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-semibold tracking-wide text-ink-700 uppercase">
            {section.title}
          </h2>
          <Button size="sm" onClick={() => openForm({ entry: null })}>
            {section.addLabel}
          </Button>
        </div>

        {entries.length === 0 ? (
          <EmptyState
            className="mt-4"
            title={section.emptyTitle}
            description={section.emptyDescription}
            action={
              <Button variant="ghost" onClick={() => openForm({ entry: null })}>
                {section.addLabel}
              </Button>
            }
          />
        ) : (
          <div className="mt-4 grid gap-4">
            {entries.map((entry) => (
              <TimelineEntry
                key={entry.id}
                title={section.titleOf(entry)}
                subtitle={section.subtitleOf(entry)}
                entry={entry}
                onEdit={() => openForm({ entry })}
                onDelete={() => setPendingDelete({ kind, entry })}
              />
            ))}
          </div>
        )}
      </section>
    )
  }

  return (
    <PageShell current="profile">
      <ProfileCard
        user={portfolio.user}
        actions={
          <LinkButton
            href={`/portfolio.html?id=${portfolio.user.id}`}
            variant="ghost"
            size="sm"
          >
            View public page
          </LinkButton>
        }
      />

      {renderSection('experience', portfolio.experiences, setExperienceForm)}
      {renderSection('education', portfolio.educations, setEducationForm)}

      {experienceForm && (
        <ExperienceFormModal
          experience={experienceForm.entry}
          onClose={() => setExperienceForm(null)}
          onSubmit={submitEntry('experience')}
        />
      )}

      {educationForm && (
        <EducationFormModal
          education={educationForm.entry}
          onClose={() => setEducationForm(null)}
          onSubmit={submitEntry('education')}
        />
      )}

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title={
          pendingDelete
            ? `Delete “${SECTIONS[pendingDelete.kind].nameOf(pendingDelete.entry)}”?`
            : ''
        }
        description="It will disappear from your public portfolio straight away."
        confirmLabel="Delete"
        destructive
        loading={deleting}
        onCancel={() => setPendingDelete(null)}
        onConfirm={handleDelete}
      />
    </PageShell>
  )
}
