"""Routes JSON de creation de compte, de profil prive et de portfolio public."""

from datetime import date

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from core.authentication import CurrentUser
from core.database import SessionDep
from core.security import hash_password
from core.validation import (
    clean_text,
    normalize_email,
    normalize_phone,
    parse_birth_date,
    validate_password,
)
from schemas.api import (
    EducationOut,
    ExperienceOut,
    PortfolioDetail,
    SignupRequest,
    UserProfile,
)
from schemas.Education import Education
from schemas.Experiences import Experience
from schemas.User import User

# Ce routeur regroupe les operations centrees sur un utilisateur.
router = APIRouter(prefix="/api", tags=["users"])


def calculate_age(birth_date: date) -> int:
    """Calcule l'age revolu a la date du jour depuis une date de naissance."""

    today_date = date.today()
    age = today_date.year - birth_date.year

    # L'ecart d'annees doit etre reduit si l'anniversaire n'est pas encore
    # passe cette annee.
    if (today_date.month, today_date.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def build_user_profile(user: User) -> UserProfile:
    """Serialise un compte vers le profil expose par l'API.

    Passer par ce constructeur unique garantit qu'aucune reponse ne peut
    inclure ``hashed_password`` par distraction : le modele de sortie ne
    declare tout simplement pas ce champ.
    """

    return UserProfile(
        id=user.id,
        name=user.name,
        first_name=user.first_name,
        mail=user.mail,
        phone=user.phone,
        birth_date=user.birth_date,
        age=calculate_age(user.birth_date),
    )


def serialize_experience(experience: Experience) -> ExperienceOut:
    """Convertit une experience stockee vers sa representation JSON.

    Les colonnes sont des ``datetime`` toujours fixes a minuit ; la reponse
    expose une date simple pour que le client n'ait aucune conversion de fuseau
    horaire a faire avant de remplir un ``<input type="date">``.
    """

    return ExperienceOut(
        id=experience.id,
        title=experience.title,
        company=experience.company,
        description=experience.description,
        date_start=experience.date_start.date(),
        date_end=experience.date_end.date(),
    )


def serialize_education(education: Education) -> EducationOut:
    """Convertit une formation stockee vers sa representation JSON."""

    return EducationOut(
        id=education.id,
        school_name=education.school_name,
        major=education.major,
        description=education.description,
        date_start=education.date_start.date(),
        date_end=education.date_end.date(),
    )


@router.post("/signup", response_model=UserProfile, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, session: SessionDep):
    """Valide une inscription et cree le compte correspondant."""

    # Chaque valeur est nettoyee et validee avant la construction du modele.
    try:
        cleaned_name = clean_text(payload.name, "Name", 100)
        cleaned_first_name = clean_text(payload.first_name, "First name", 100)
        birth_date_obj = parse_birth_date(payload.birth_date)
        normalized_mail = normalize_email(payload.mail)
        normalized_phone = normalize_phone(payload.phone)
        validated_password = validate_password(payload.password)
    except ValueError as exc:
        # Les erreurs attendues de validation portent un message lisible que
        # l'interface affiche tel quel sous le formulaire.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    # Ce controle fournit une erreur lisible avant de tenter l'insertion.
    existing_user = session.exec(
        select(User).where(User.mail == normalized_mail)
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists with this email address.",
        )

    # Seul le condensat du mot de passe valide est enregistre ; le mot de passe
    # brut est ecarte.
    user = User(
        name=cleaned_name,
        first_name=cleaned_first_name,
        birth_date=birth_date_obj,
        mail=normalized_mail,
        phone=normalized_phone,
        hashed_password=hash_password(validated_password),
    )

    session.add(user)
    try:
        session.commit()
    except IntegrityError as exc:
        # La contrainte unique protege aussi contre deux inscriptions
        # concurrentes. Le rollback est obligatoire avant de pouvoir reutiliser
        # cette session SQLAlchemy.
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account already exists with this email address.",
        ) from exc

    session.refresh(user)
    return build_user_profile(user)


@router.get("/me", response_model=PortfolioDetail)
def read_own_portfolio(user: CurrentUser, session: SessionDep):
    """Renvoie le portfolio complet du compte authentifie."""

    # L'identifiant provient du jeton verifie, jamais d'un parametre client :
    # un visiteur ne peut donc pas demander le tableau de bord d'un autre.
    experiences = session.exec(
        select(Experience)
        .where(Experience.user_id == user.id)
        .order_by(Experience.date_start.desc())
    ).all()

    educations = session.exec(
        select(Education)
        .where(Education.user_id == user.id)
        .order_by(Education.date_start.desc())
    ).all()

    return PortfolioDetail(
        user=build_user_profile(user),
        experiences=[serialize_experience(item) for item in experiences],
        educations=[serialize_education(item) for item in educations],
    )


@router.get("/portfolios/{user_id}", response_model=PortfolioDetail)
def read_public_portfolio(user_id: int, session: SessionDep):
    """Renvoie le portfolio public identifie par son identifiant utilisateur."""

    # La cle primaire de l'URL permet un acces direct sans authentification.
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This portfolio does not exist.",
        )

    # Les deux collections sont filtrees sur le proprietaire demande.
    experiences = session.exec(
        select(Experience)
        .where(Experience.user_id == user.id)
        .order_by(Experience.date_start.desc())
    ).all()

    educations = session.exec(
        select(Education)
        .where(Education.user_id == user.id)
        .order_by(Education.date_start.desc())
    ).all()

    return PortfolioDetail(
        user=build_user_profile(user),
        experiences=[serialize_experience(item) for item in experiences],
        educations=[serialize_education(item) for item in educations],
    )
