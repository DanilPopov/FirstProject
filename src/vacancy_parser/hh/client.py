from __future__ import annotations

from typing import Any

import httpx

from vacancy_parser.config import settings
from vacancy_parser.hh.schemas import HHSearchResponse

HH_API_BASE = "https://api.hh.ru"


class HHClient:
    """Thin async client for the hh.ru public API.

    Docs: https://api.hh.ru/openapi/redoc
    """

    def __init__(self, base_url: str = HH_API_BASE, user_agent: str | None = None) -> None:
        self._base_url = base_url
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={"User-Agent": user_agent or settings.hh_user_agent},
            timeout=15.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HHClient":
        return self

    async def __aexit__(self, *_exc: Any) -> None:
        await self.close()

    async def search_vacancies(
        self,
        *,
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
        page: int = 0,
        per_page: int = 20,
        order_by: str = "publication_time",
        date_from: str | None = None,
    ) -> HHSearchResponse:
        params: list[tuple[str, str]] = []

        def add_multi(key: str, values: list[str] | None) -> None:
            if not values:
                return
            for v in values:
                params.append((key, v))

        if text:
            params.append(("text", text))
        add_multi("area", area)
        add_multi("schedule", schedule)
        add_multi("employment", employment)
        add_multi("experience", experience)
        add_multi("professional_role", professional_role)
        add_multi("industry", industry)
        if salary is not None:
            params.append(("salary", str(salary)))
        if currency:
            params.append(("currency", currency))
        if only_with_salary:
            params.append(("only_with_salary", "true"))
        params.append(("page", str(page)))
        params.append(("per_page", str(per_page)))
        params.append(("order_by", order_by))
        if date_from:
            params.append(("date_from", date_from))

        resp = await self._client.get("/vacancies", params=params)
        resp.raise_for_status()
        return HHSearchResponse.model_validate(resp.json())
