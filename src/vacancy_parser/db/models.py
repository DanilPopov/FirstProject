from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # telegram user_id
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    subscription_active: Mapped[bool] = mapped_column(Boolean, default=False)
    subscription_ends_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    filters: Mapped[list["UserFilter"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserFilter(Base):
    __tablename__ = "user_filters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(128), default="default")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # hh.ru native filters (lists stored as JSON)
    schedule: Mapped[list | None] = mapped_column(JSON, nullable=True)           # remote/fullDay/...
    employment: Mapped[list | None] = mapped_column(JSON, nullable=True)         # full/part/project
    experience: Mapped[list | None] = mapped_column(JSON, nullable=True)         # noExperience/between1And3/...
    professional_roles: Mapped[list | None] = mapped_column(JSON, nullable=True) # role ids
    industry: Mapped[list | None] = mapped_column(JSON, nullable=True)           # industry ids
    area: Mapped[list | None] = mapped_column(JSON, nullable=True)               # area ids
    text: Mapped[str | None] = mapped_column(String(512), nullable=True)         # keywords
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)       # RUR/USD/EUR

    user: Mapped[User] = relationship(back_populates="filters")


class Vacancy(Base):
    __tablename__ = "vacancies"

    id: Mapped[str] = mapped_column(String(32), primary_key=True)  # hh vacancy id
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(String(512))
    alternate_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    company_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(256), nullable=True)

    area_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    salary_gross: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    schedule: Mapped[str | None] = mapped_column(String(32), nullable=True)
    employment: Mapped[str | None] = mapped_column(String(32), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(32), nullable=True)

    professional_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)

    snippet_requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    snippet_responsibility: Mapped[str | None] = mapped_column(Text, nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    fetched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    raw: Mapped[dict | None] = mapped_column(JSON, nullable=True)


class SentVacancy(Base):
    __tablename__ = "sent_vacancies"
    __table_args__ = (UniqueConstraint("user_id", "vacancy_id", name="uq_user_vacancy"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"))
    vacancy_id: Mapped[str] = mapped_column(String(32), ForeignKey("vacancies.id", ondelete="CASCADE"))
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
