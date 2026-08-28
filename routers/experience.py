"""Routes JSON du CRUD des experiences possedees par le compte authentifie."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from core.authentication import CurrentUser, load_owned_record
from core.database import SessionDep
from core.validation import clean_text, parse_date_range
from routers.user import serialize_experience
from schemas.api import ExperienceOut, ExperienceRequest
from schemas.Experiences import Experience

router = APIRouter(prefix="/api/experiences", tags=["experiences"])


def validate_experience_payload(payload: ExperienceRequest):
    """Normalise une saisie d'experience ou repond 400 avec son message.

    Les memes regles servent a la creation et a la modification, ce qui evite
    qu'une edition puisse enregistrer une valeur qu'une creation aurait refusee.
    """

    try:
        return (
            clean_text(payload.title, "Title", 150),
            clean_text(payload.company, "Company", 150),
            clean_text(payload.description, "Description", 3000),
            *parse_date_range(payload.date_start, payload.date_end),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def load_own_experience(session: SessionDep, experience_id: int, user) -> Experience:
    """Charge une experience appartenant au compte courant, ou repond 404.

    Un identifiant inconnu et un identifiant appartenant a quelqu'un d'autre
    recoivent exactement la meme reponse : l'existence d'une ressource
    etrangere n'est jamais revelee.
    """

    experience = load_owned_record(session, Experience, experience_id, user)
    if experience is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This experience does not exist.",
        )
    return experience


@router.get("", response_model=list[ExperienceOut])
def list_experiences(user: CurrentUser, session: SessionDep):
    """Liste les experiences du compte authentifie, de la plus recente."""

    experiences = session.exec(
        select(Experience)
        .where(Experience.user_id == user.id)
        .order_by(Experience.date_start.desc())
    ).all()
    return [serialize_experience(item) for item in experiences]


@router.post("", response_model=ExperienceOut, status_code=status.HTTP_201_CREATED)
def create_experience(
    payload: ExperienceRequest,
    user: CurrentUser,
    session: SessionDep,
):
    """Enregistre une nouvelle experience pour le compte authentifie."""

    title, company, description, date_start, date_end = validate_experience_payload(
        payload
    )

    # user_id provient exclusivement du compte authentifie et etablit la
    # propriete en base : une valeur envoyee par le client serait ignoree.
    experience = Experience(
        title=title,
        company=company,
        description=description,
        date_start=date_start,
        date_end=date_end,
        user_id=user.id,
    )

    session.add(experience)
    session.commit()
    session.refresh(experience)
    return serialize_experience(experience)


@router.put("/{experience_id}", response_model=ExperienceOut)
def update_experience(
    experience_id: int,
    payload: ExperienceRequest,
    user: CurrentUser,
    session: SessionDep,
):
    """Met a jour une experience appartenant au compte authentifie."""

    # L'identifiant de l'URL ne constitue jamais une preuve de propriete : la
    # verification precede toute lecture des valeurs soumises.
    experience = load_own_experience(session, experience_id, user)

    title, company, description, date_start, date_end = validate_experience_payload(
        payload
    )

    experience.title = title
    experience.company = company
    experience.description = description
    experience.date_start = date_start
    experience.date_end = date_end

    session.add(experience)
    session.commit()
    session.refresh(experience)
    return serialize_experience(experience)


@router.delete("/{experience_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experience(
    experience_id: int,
    user: CurrentUser,
    session: SessionDep,
):
    """Supprime une experience appartenant au compte authentifie."""

    experience = load_own_experience(session, experience_id, user)

    session.delete(experience)
    session.commit()

    # 204 interdit tout corps de reponse : le client se contente du statut.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
