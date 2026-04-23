from __future__ import annotations

import logging

from telegram.ext import Application

from vacancy_parser.bot import onboarding
from vacancy_parser.config import settings
from vacancy_parser.db.session import init_db

log = logging.getLogger(__name__)


def build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")
    app = Application.builder().token(settings.telegram_bot_token).build()
    onboarding.register(app)
    return app


async def _post_init(_: Application) -> None:
    await init_db()
    log.info("Bot ready")


def run() -> None:
    app = build_application()
    app.post_init = _post_init
    log.info("Starting Telegram bot (long polling)")
    app.run_polling(allowed_updates=None, close_loop=False)
