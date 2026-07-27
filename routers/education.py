"""Routes protégées de création, consultation, modification et suppression de formations."""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from core.auth_guard import auth_guard
from core.authentication import load_owned_record
from core.csrf import validate_csrf_token
from core.database import get_session
from core.validation import clean_text, parse_date_range
from schemas.Education import Education

# Ce routeur expose les opérations CRUD des parcours de formation.
router = APIRouter()

# Le même template prend en charge la création et l'édition grâce à la valeur edu.
templates = Jinja2Templates(directory="templates")


@router.get("/profil/education", response_class=HTMLResponse)
def show_form(
    request: Request,
    session: Session = Depends(get_session),
):
    """Affiche le formulaire vide de création d'une formation authentifiée."""

    auth_result = auth_guard(request, session)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user = auth_result

    # edu=None place le template partagé en mode création et form_values initialise les champs.
    return templates.TemplateResponse(
        request,
        "education.html",
        {"request": request, "edu": None, "form_values": {}},
    )


@router.post("/profil/education")
def create_education(
    request: Request,
    csrf_token: str = Form(""),
    school_name: str = Form(...),
    date_start: str = Form(...),
    date_end: str = Form(...),
    description: str = Form(...),
    major: str = Form(...),
    session: Session = Depends(get_session),
):
    """Valide et enregistre une formation pour l'utilisateur authentifié."""

    auth_result = auth_guard(request, session)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user = auth_result

    # La mutation n'est autorisée qu'avec le jeton CSRF associé au navigateur courant.
    validate_csrf_token(request, csrf_token)

    # La saisie brute est conservée uniquement pour réafficher le formulaire en cas d'erreur.
    form_values = {
        "school_name": school_name,
        "date_start": date_start,
        "date_end": date_end,
        "description": description,
        "major": major,
    }

    # Les textes sont nettoyés et bornés ; la plage vérifie le format et l'ordre des dates.
    try:
        cleaned_school_name = clean_text(school_name, "School", 150)
        cleaned_description = clean_text(description, "Description", 3000)
        cleaned_major = clean_text(major, "Major", 150)
        parsed_start, parsed_end = parse_date_range(date_start, date_end)
    except ValueError as exc:
        # Le template reste en mode création et présente l'erreur de validation au client.
        return templates.TemplateResponse(
            request,
            "education.html",
            {
                "request": request,
                "edu": None,
                "error": str(exc),
                "form_values": form_values,
            },
            status_code=400,
        )

    # user_id provient exclusivement du compte authentifié et établit la propriété en base.
    education = Education(
        school_name=cleaned_school_name,
        date_start=parsed_start,
        date_end=parsed_end,
        description=cleaned_description,
        major=cleaned_major,
        user_id=user.id,
    )

    # La session injectée regroupe l'insertion et sa validation dans la requête courante.
    session.add(education)
    session.commit()

    # Le code 303 évite de soumettre une seconde fois le formulaire lors d'une actualisation.
    return RedirectResponse("/profil", status_code=303)


@router.post("/profil/education/delete/{edu_id}")
def delete_education(
    request: Request,
    edu_id: int,
    csrf_token: str = Form(""),
    session: Session = Depends(get_session),
):
    """Supprime une formation uniquement si elle appartient au compte authentifié."""

    auth_result = auth_guard(request, session)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user = auth_result

    # Le contrôle CSRF précède le chargement de la ressource destinée à être supprimée.
    validate_csrf_token(request, csrf_token)

    # Vérification que l'éducation appartient bien à l'utilisateur authentifié avant suppression
    edu = load_owned_record(session, Education, edu_id, user)
    
    if edu:
        session.delete(edu)
        session.commit()

    # La réponse identique masque l'existence des ressources étrangères et applique PRG.
    return RedirectResponse("/profil", status_code=303)


@router.get("/profil/education/edit/{edu_id}", response_class=HTMLResponse)
def edit_education_form(
    request: Request,
    edu_id: int,
    session: Session = Depends(get_session),
):
    """Affiche le formulaire d'édition d'une formation possédée par le compte courant."""

    auth_result = auth_guard(request, session)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user = auth_result

    # Vérification que l'éducation appartient bien à l'utilisateur authentifié avant édition
    edu = load_owned_record(session, Education, edu_id, user)
    
    if not edu:
        return RedirectResponse("/profil", status_code=303)

    # edu active le mode édition du template ; les valeurs persistées préremplissent les champs.
    return templates.TemplateResponse(
        request,
        "education.html",
        {"request": request, "edu": edu, "form_values": {}},
    )


@router.post("/profil/education/edit/{edu_id}")
def update_education(
    request: Request,
    edu_id: int,
    csrf_token: str = Form(""),
    school_name: str = Form(...),
    date_start: str = Form(...),
    date_end: str = Form(...),
    description: str = Form(...),
    major: str = Form(...),
    session: Session = Depends(get_session),
):
    """Valide puis met à jour une formation appartenant au compte authentifié."""

    auth_result = auth_guard(request, session)
    if isinstance(auth_result, RedirectResponse):
        return auth_result
    user = auth_result

    # Le jeton CSRF protège la requête POST contre une soumission depuis un site tiers.
    validate_csrf_token(request, csrf_token)

    # L'ID de l'enregistrement provient de l'URL et ne constitue jamais une preuve de propriété
    edu = load_owned_record(session, Education, edu_id, user)
    
    if not edu:
        return RedirectResponse("/profil", status_code=303)

    # La saisie d'origine permet de ne pas effacer les champs après une validation refusée.
    form_values = {
        "school_name": school_name,
        "date_start": date_start,
        "date_end": date_end,
        "description": description,
        "major": major,
    }

    # Les mêmes règles qu'à la création maintiennent des données cohérentes après l'édition.
    try:
        cleaned_school_name = clean_text(school_name, "School", 150)
        cleaned_description = clean_text(description, "Description", 3000)
        cleaned_major = clean_text(major, "Major", 150)
        parsed_start, parsed_end = parse_date_range(date_start, date_end)
    except ValueError as exc:
        # L'objet edu conserve le mode édition pendant que form_values restaure la saisie invalide.
        return templates.TemplateResponse(
            request,
            "education.html",
            {
                "request": request,
                "edu": edu,
                "error": str(exc),
                "form_values": form_values,
            },
            status_code=400,
        )

    # Les valeurs validées remplacent les champs de l'entité déjà suivie par la session.
    edu.school_name = cleaned_school_name
    edu.date_start = parsed_start
    edu.date_end = parsed_end
    edu.description = cleaned_description
    edu.major = cleaned_major

    # commit persiste toutes les modifications atomiquement dans la base configurée.
    session.commit()

    # Le navigateur revient au profil par un GET distinct après la mise à jour.
    return RedirectResponse("/profil", status_code=303)
