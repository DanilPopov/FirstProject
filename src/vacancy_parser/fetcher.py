from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy import select

from vacancy_parser.db.models import Vacancy
from vacancy_parser.db.session import AsyncSessionFactory
from vacancy_parser.hh.client import HHClient
from vacancy_parser.hh.mapper import hh_to_vacancy

log = logging.getLogger(__name__)

# hh.ru caps search results: page * per_page must be <= 2000, per_page <= 100
HH_MAX_PER_PAGE = 100
HH_MAX_RESULTS = 2000


@dataclass
class FetchStats:
    pages: int = 0
    fetched: int = 0
    inserted: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)


async def fetch_and_store(
    *,
    client: HHClient,
    text: str | None = None,
    area: list[str] | None = None,
    schedule: list[str] | None = None,
    employment: list[str] | None = None,
    experience: list[str] | None = None,
    professional_role: list[str] | None = None,
    industry: list[str] | None = None,
    salary: int | None = None,
    currency: str | None = None,
    only_with_salary: bool = False,
    date_from: str | None = None,
    per_page: int = 50,
    max_pages: int | None = None,
) -> FetchStats:
    """Run a single fetch pass against hh.ru and upsert all results into the DB.

    Paginates through the search response until hh runs out of pages, the hard
    cap (2000 results) is reached, or `max_pages` is hit.
    """
    per_page = min(per_page, HH_MAX_PER_PAGE)
    stats = FetchStats()

    page = 0
    while True:
        if max_pages is not None and page >= max_pages:
            break
        if (page + 1) * per_page > HH_MAX_RESULTS:
            log.warning("Reached hh.ru hard cap of %d results, stopping", HH_MAX_RESULTS)
            break

        resp = await client.search_vacancies(
            text=text,
            area=area,
            schedule=schedule,
            employment=employment,
            experience=experience,
            professional_role=professional_role,
            industry=industry,
            salary=salary,
            currency=currency,
            only_with_salary=only_with_salary,
            date_from=date_from,
            page=page,
            per_page=per_page,
        )

        if not resp.items:
            break

        stats.pages += 1
        stats.fetched += len(resp.items)

        ids = [v.id for v in resp.items]
        async with AsyncSessionFactory() as session:
            existing_rows = await session.execute(select(Vacancy.id).where(Vacancy.id.in_(ids)))
            existing_ids = set(existing_rows.scalars())

            for hh_vac in resp.items:
                row = hh_to_vacancy(hh_vac)
                await session.merge(row)
                if hh_vac.id in existing_ids:
                    stats.updated += 1
                else:
                    stats.inserted += 1
            await session.commit()

        log.info(
            "page=%d fetched=%d total_fetched=%d inserted=%d updated=%d",
            page, len(resp.items), stats.fetched, stats.inserted, stats.updated,
        )

        if page >= resp.pages - 1:
            break
        page += 1

    return stats
