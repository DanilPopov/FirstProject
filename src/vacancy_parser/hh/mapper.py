from __future__ import annotations

from datetime import datetime

from vacancy_parser.db.models import Vacancy
from vacancy_parser.hh.schemas import HHVacancy


def hh_to_vacancy(hh: HHVacancy) -> Vacancy:
    """Convert a pydantic HHVacancy into a SQLAlchemy Vacancy row (not yet persisted)."""
    salary = hh.salary
    area = hh.area
    employer = hh.employer
    snippet = hh.snippet

    return Vacancy(
        id=hh.id,
        title=hh.name,
        url=hh.url,
        alternate_url=hh.alternate_url,
        company_id=employer.id if employer else None,
        company_name=employer.name if employer else None,
        area_id=area.id if area else None,
        area_name=area.name if area else None,
        salary_from=salary.from_ if salary else None,
        salary_to=salary.to if salary else None,
        salary_currency=salary.currency if salary else None,
        salary_gross=salary.gross if salary else None,
        schedule=hh.schedule.id if hh.schedule else None,
        employment=hh.employment.id if hh.employment else None,
        experience=hh.experience.id if hh.experience else None,
        professional_roles=[r.id for r in hh.professional_roles if r.id] or None,
        snippet_requirement=snippet.requirement if snippet else None,
        snippet_responsibility=snippet.responsibility if snippet else None,
        published_at=hh.published_at,
        fetched_at=datetime.utcnow(),
        raw=hh.model_dump(mode="json"),
    )
