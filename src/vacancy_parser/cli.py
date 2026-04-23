from __future__ import annotations

import argparse
import asyncio
import logging

from vacancy_parser.db.session import init_db
from vacancy_parser.fetcher import fetch_and_store
from vacancy_parser.hh.client import HHClient
from vacancy_parser.logging_config import setup_logging

log = logging.getLogger("vacancy_parser.cli")


def _csv(value: str) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="vacancy_parser", description="hh.ru vacancy parser")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("initdb", help="Create database tables")

    p_fetch = sub.add_parser("fetch", help="Fetch vacancies from hh.ru into the DB")
    p_fetch.add_argument("--text", help="Keyword search (hh `text`)")
    p_fetch.add_argument("--area", type=_csv, help="Comma-separated area ids (e.g. 1,2)")
    p_fetch.add_argument("--schedule", type=_csv, help="remote,fullDay,flexible,shift,flyInFlyOut")
    p_fetch.add_argument("--employment", type=_csv, help="full,part,project,volunteer,probation")
    p_fetch.add_argument(
        "--experience", type=_csv,
        help="noExperience,between1And3,between3And6,moreThan6",
    )
    p_fetch.add_argument("--role", dest="professional_role", type=_csv, help="Professional role ids")
    p_fetch.add_argument("--industry", type=_csv, help="Industry ids")
    p_fetch.add_argument("--salary", type=int, help="Minimum salary")
    p_fetch.add_argument("--currency", help="RUR / USD / EUR / ...")
    p_fetch.add_argument("--only-with-salary", action="store_true")
    p_fetch.add_argument("--date-from", help="ISO-8601 datetime, e.g. 2025-01-01T00:00:00")
    p_fetch.add_argument("--per-page", type=int, default=50)
    p_fetch.add_argument("--max-pages", type=int, default=None)

    return parser


async def cmd_initdb() -> None:
    await init_db()
    log.info("Database initialised")


async def cmd_fetch(args: argparse.Namespace) -> None:
    await init_db()
    async with HHClient() as client:
        stats = await fetch_and_store(
            client=client,
            text=args.text,
            area=args.area,
            schedule=args.schedule,
            employment=args.employment,
            experience=args.experience,
            professional_role=args.professional_role,
            industry=args.industry,
            salary=args.salary,
            currency=args.currency,
            only_with_salary=args.only_with_salary,
            date_from=args.date_from,
            per_page=args.per_page,
            max_pages=args.max_pages,
        )
    log.info(
        "done: pages=%d fetched=%d inserted=%d updated=%d",
        stats.pages, stats.fetched, stats.inserted, stats.updated,
    )


def main() -> None:
    setup_logging()
    args = build_parser().parse_args()
    if args.command == "initdb":
        asyncio.run(cmd_initdb())
    elif args.command == "fetch":
        asyncio.run(cmd_fetch(args))


if __name__ == "__main__":
    main()
