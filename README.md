# Vacancy Parser

Telegram-бот, который парсит вакансии с hh.ru по фильтрам пользователя и
присылает новые подходящие вакансии в реальном времени.

## Статус

Этап 0 — каркас проекта. См. `docs/roadmap.md`.

## Структура

```
src/vacancy_parser/
├── config.py            # настройки из .env
├── db/
│   ├── models.py        # SQLAlchemy модели (User, UserFilter, Vacancy, SentVacancy)
│   └── session.py       # async engine / session factory
└── hh/
    ├── client.py        # async клиент к https://api.hh.ru
    ├── schemas.py       # pydantic-модели ответа
    └── dictionaries.py  # маппинг enum-значений фильтров
```

## Локальный запуск

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# дальше — CLI и бот появятся на Этапе 1–2
```

## Деплой

Railway. Два сервиса в одном проекте:
- `bot` — Telegram-бот (long-running process)
- `worker` — fetcher + matcher (APScheduler в том же процессе либо отдельный)

Хранилище — SQLite на volume для MVP, позже миграция на Railway Postgres
через Alembic (модели уже async-совместимые).

## Дорожная карта

- **Этап 0** (текущий) — каркас, конфиг, модели БД, клиент hh.ru.
- **Этап 1** — fetcher (глобальный воркер) + сохранение вакансий в БД, CLI для отладки.
- **Этап 2** — Telegram-бот: онбординг, пошаговый выбор фильтров вручную, первая подборка из 10, real-time уведомления через matcher.
- **Этап 3** — монетизация: Telegram Stars, триал 24 часа, помесячная подписка.
- **Этап 4** (опционально) — международные источники (RemoteOK, WWR и т.д.).
