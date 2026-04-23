from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HHDictItem(BaseModel):
    id: str | None = None
    name: str | None = None


class HHSalary(BaseModel):
    model_config = ConfigDict(extra="ignore")

    from_: int | None = Field(default=None, alias="from")
    to: int | None = None
    currency: str | None = None
    gross: bool | None = None


class HHArea(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    name: str | None = None


class HHEmployer(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str | None = None
    name: str | None = None


class HHSnippet(BaseModel):
    model_config = ConfigDict(extra="ignore")

    requirement: str | None = None
    responsibility: str | None = None


class HHVacancy(BaseModel):
    """Minimal projection of a vacancy from hh.ru `/vacancies` search response."""

    model_config = ConfigDict(extra="ignore")

    id: str
    name: str
    url: str  # API url
    alternate_url: str | None = None

    area: HHArea | None = None
    employer: HHEmployer | None = None
    salary: HHSalary | None = None

    schedule: HHDictItem | None = None
    employment: HHDictItem | None = None
    experience: HHDictItem | None = None

    professional_roles: list[HHDictItem] = Field(default_factory=list)

    snippet: HHSnippet | None = None
    published_at: datetime | None = None


class HHSearchResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    items: list[HHVacancy] = Field(default_factory=list)
    found: int = 0
    pages: int = 0
    page: int = 0
    per_page: int = 0
