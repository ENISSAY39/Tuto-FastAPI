"""Declare the JSON request and response bodies exchanged with the browser.

These models are deliberately separate from the SQLModel tables in this
package: they decide what the API accepts and, more importantly, which stored
columns are ever serialized back to a client. ``hashed_password`` has no
representation here and therefore cannot leak through a response.

Incoming payloads type every field as ``str`` because the shared helpers in
:mod:`core.validation` own the real rules and produce the human-readable
messages the interface displays. Pydantic is used here for shape, not for
business validation.
"""

from datetime import date

from pydantic import BaseModel


class SignupRequest(BaseModel):
    """Account creation payload submitted by the signup form."""

    name: str
    first_name: str
    birth_date: str
    mail: str
    phone: str
    password: str


class LoginRequest(BaseModel):
    """Credentials submitted by the login form."""

    mail: str
    password: str


class ExperienceRequest(BaseModel):
    """Professional experience submitted by its create or edit form."""

    title: str
    company: str
    description: str
    date_start: str
    date_end: str


class EducationRequest(BaseModel):
    """Education entry submitted by its create or edit form."""

    school_name: str
    major: str
    description: str
    date_start: str
    date_end: str


class UserSummary(BaseModel):
    """Minimal identity used by the public portfolio directory listing."""

    id: int
    name: str
    first_name: str


class UserProfile(BaseModel):
    """Identity and contact details shown on a portfolio page.

    The same shape serves the authenticated dashboard and the public portfolio
    because the previous server-rendered pages already displayed the same
    contact fields to visitors.
    """

    id: int
    name: str
    first_name: str
    mail: str
    phone: str
    birth_date: date
    age: int


class ExperienceOut(BaseModel):
    """One stored professional experience as returned to the client."""

    id: int
    title: str
    company: str
    description: str
    date_start: date
    date_end: date


class EducationOut(BaseModel):
    """One stored education entry as returned to the client."""

    id: int
    school_name: str
    major: str
    description: str
    date_start: date
    date_end: date


class AuthenticatedUser(BaseModel):
    """Answer to a successful login: the token plus who it belongs to."""

    token: str
    user: UserProfile


class PortfolioDetail(BaseModel):
    """A complete portfolio: its owner and both owned collections."""

    user: UserProfile
    experiences: list[ExperienceOut]
    educations: list[EducationOut]


class PortfolioPage(BaseModel):
    """One page of the public directory, with everything its pager needs.

    The page number is echoed back because the API clamps out-of-range values,
    so the client must display the page it actually received rather than the
    one it asked for.
    """

    portfolios: list[UserSummary]
    query: str
    current_page: int
    total_pages: int
    total_portfolios: int
    has_previous: bool
    has_next: bool
