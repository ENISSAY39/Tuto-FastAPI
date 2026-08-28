"""Routes JSON du CRUD des formations possedees par le compte authentifie."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlmodel import select

from core.authentication import CurrentUser, load_owned_record
from core.database import SessionDep
from core.validation import clean_text, parse_date_range
from routers.user import serialize_education
from schemas.api import EducationOut, EducationRequest
from schemas.Education import Education

router = APIRouter(prefix="/api/educations", tags=["educations"])


def validate_education_payload(payload: EducationRequest):
    """Normalise une saisie de formation ou repond 400 avec son message.

    Les memes regles servent a la creation et a la modification, ce qui evite
    qu'une edition puisse enregistrer une valeur qu'une creation aurait refusee.
    """

    try:
        return (
            clean_text(payload.school_name, "School name", 150),
            clean_text(payload.major, "Major", 150),
            clean_text(payload.description, "Description", 3000),
            *parse_date_range(payload.date_start, payload.date_end),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


def load_own_education(session: SessionDep, education_id: int, user) -> Education:
    """Charge une formation appartenant au compte courant, ou repond 404.

    Un identifiant inconnu et un identifiant appartenant a quelqu'un d'autre
    recoivent exactement la meme reponse : l'existence d'une ressource
    etrangere n'est jamais revelee.
    """

    education = load_owned_record(session, Education, education_id, user)
    if education is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This education entry does not exist.",
        )
    return education


@router.get("", response_model=list[EducationOut])
def list_educations(user: CurrentUser, session: SessionDep):
    """Liste les formations du compte authentifie, de la plus recente."""

    educations = session.exec(
        select(Education)
        .where(Education.user_id == user.id)
        .order_by(Education.date_start.desc())
    ).all()
    return [serialize_education(item) for item in educations]


@router.post("", response_model=EducationOut, status_code=status.HTTP_201_CREATED)
def create_education(
    payload: EducationRequest,
    user: CurrentUser,
    session: SessionDep,
):
    """Enregistre une nouvelle formation pour le compte authentifie."""

    school_name, major, description, date_start, date_end = (
        validate_education_payload(payload)
    )

    # user_id provient exclusivement du compte authentifie et etablit la
    # propriete en base : une valeur envoyee par le client serait ignoree.
    education = Education(
        school_name=school_name,
        major=major,
        description=description,
        date_start=date_start,
        date_end=date_end,
        user_id=user.id,
    )

    session.add(education)
    session.commit()
    session.refresh(education)
    return serialize_education(education)


@router.put("/{education_id}", response_model=EducationOut)
def update_education(
    education_id: int,
    payload: EducationRequest,
    user: CurrentUser,
    session: SessionDep,
):
    """Met a jour une formation appartenant au compte authentifie."""

    # L'identifiant de l'URL ne constitue jamais une preuve de propriete : la
    # verification precede toute lecture des valeurs soumises.
    education = load_own_education(session, education_id, user)

    school_name, major, description, date_start, date_end = (
        validate_education_payload(payload)
    )

    education.school_name = school_name
    education.major = major
    education.description = description
    education.date_start = date_start
    education.date_end = date_end

    session.add(education)
    session.commit()
    session.refresh(education)
    return serialize_education(education)


@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_education(
    education_id: int,
    user: CurrentUser,
    session: SessionDep,
):
    """Supprime une formation appartenant au compte authentifie."""

    education = load_own_education(session, education_id, user)

    session.delete(education)
    session.commit()

    # 204 interdit tout corps de reponse : le client se contente du statut.
    return Response(status_code=status.HTTP_204_NO_CONTENT)
