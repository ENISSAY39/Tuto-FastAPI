"""Routes JSON de decouverte publique et d'authentification."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import func
from sqlmodel import select

from core.authentication import clear_session_cookies, set_session_cookies
from core.database import SessionDep
from core.security import create_access_token, verify_password
from core.validation import normalize_email
from routers.user import build_user_profile
from schemas.api import (
    LoginRequest,
    PortfolioPage,
    UserProfile,
    UserSummary,
)
from schemas.User import User

# Toutes les routes de l'application vivent sous /api : le reste des URL est
# servi par le frontend compile, qui doit pouvoir recevoir n'importe quel
# chemin sans entrer en conflit avec une route de l'API.
router = APIRouter(prefix="/api", tags=["auth"])

# Une taille de page fixe garde les liens precedent/suivant coherents entre
# deux requetes successives.
PORTFOLIOS_PER_PAGE = 10


@router.get("/portfolios", response_model=PortfolioPage)
def list_portfolios(
    session: SessionDep,
    query: str = "",
    page: int = 1,
):
    """Liste les portfolios publics, filtres par nom et pagines par dix.

    Une recherche vide se comporte comme l'ancienne page d'accueil : le filtre
    ``contains("")`` accepte toutes les lignes, ce qui evite de maintenir deux
    routes presque identiques.
    """

    # Les numeros negatifs ou nuls sont ramenes a la premiere page.
    if page < 1:
        page = 1

    # La meme condition sert au comptage puis au chargement de la tranche.
    search_condition = User.name.contains(query)

    # COUNT laisse le total au moteur SQL au lieu de charger toutes les lignes
    # en memoire uniquement pour les compter.
    total_portfolios = session.exec(
        select(func.count()).select_from(User).where(search_condition)
    ).one()

    # Une recherche sans resultat conserve une page logique pour que le pager
    # affiche "Page 1 of 1" plutot qu'une division par zero.
    total_pages = max(
        1,
        (total_portfolios + PORTFOLIOS_PER_PAGE - 1) // PORTFOLIOS_PER_PAGE,
    )

    # Une page situee au dela des resultats est ramenee a la derniere valide.
    if page > total_pages:
        page = total_pages

    # OFFSET est indexe a partir de zero, contrairement au numero affiche.
    offset = (page - 1) * PORTFOLIOS_PER_PAGE

    portfolios = session.exec(
        select(User)
        .where(search_condition)
        .order_by(User.id)
        .offset(offset)
        .limit(PORTFOLIOS_PER_PAGE)
    ).all()

    return PortfolioPage(
        # UserSummary ne publie que l'identite : ni contact ni condensat de mot
        # de passe ne transitent par la liste publique.
        portfolios=[
            UserSummary(id=user.id, name=user.name, first_name=user.first_name)
            for user in portfolios
        ],
        query=query,
        current_page=page,
        total_pages=total_pages,
        total_portfolios=total_portfolios,
        has_previous=page > 1,
        has_next=page < total_pages,
    )


@router.post("/login", response_model=UserProfile)
def login(payload: LoginRequest, response: Response, session: SessionDep):
    """Authentifie un compte et ouvre sa session navigateur.

    Le jeton n'apparait pas dans le corps de la reponse : il part uniquement
    dans un cookie HTTP-only, hors de portee des scripts de la page.
    """

    # La normalisation rend la recherche insensible aux espaces et a la casse.
    try:
        normalized_mail = normalize_email(payload.mail)
    except ValueError:
        # Une adresse mal formee suit quand meme le chemin d'echec generique :
        # repondre differemment revelerait quelles adresses sont valides.
        normalized_mail = payload.mail.strip().lower()

    user = session.exec(select(User).where(User.mail == normalized_mail)).first()

    # Un message unique evite de reveler si l'adresse existe en base.
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # L'adresse stockee devient le sujet du JWT et permettra de recharger le
    # compte a chaque requete protegee.
    token = create_access_token(data={"sub": user.mail})
    set_session_cookies(response, token)

    return build_user_profile(user)


@router.post("/logout")
def logout(response: Response):
    """Ferme la session en supprimant les cookies qui la portent.

    Le jeton etant hors de portee des scripts, seule cette route peut mettre
    fin a une session : l'interface ne peut pas le faire elle-meme.
    """

    clear_session_cookies(response)
    return {"status": "logged out"}
