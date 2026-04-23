from __future__ import annotations

import logging
from enum import IntEnum, auto

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from vacancy_parser.bot import areas, keyboards, repository, texts
from vacancy_parser.hh.dictionaries import CURRENCIES, EMPLOYMENT, EXPERIENCE, SCHEDULE

log = logging.getLogger(__name__)


class State(IntEnum):
    SCHEDULE = auto()
    EXPERIENCE = auto()
    EMPLOYMENT = auto()
    TEXT = auto()
    AREA = auto()
    SALARY = auto()
    CURRENCY = auto()
    CONFIRM = auto()


def _draft(context: ContextTypes.DEFAULT_TYPE) -> dict:
    draft = context.user_data.setdefault("draft", {})
    draft.setdefault("schedule", [])
    draft.setdefault("experience", [])
    draft.setdefault("employment", [])
    return draft


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    await repository.get_or_create_user(user.id, user.username)
    context.user_data["draft"] = {"schedule": [], "experience": [], "employment": []}

    await update.message.reply_text(texts.GREETING)
    await update.message.reply_text(
        texts.ASK_SCHEDULE,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboards.schedule_keyboard(set()),
    )
    return State.SCHEDULE


async def cmd_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(texts.CANCELLED)
    context.user_data.clear()
    return ConversationHandler.END


# ---------- multi-select helpers ----------

async def _handle_multiselect(
    update: Update, context: ContextTypes.DEFAULT_TYPE, field: str,
    options: dict[str, str], keyboard_fn, next_state: State, next_prompt: str, next_keyboard_fn,
) -> int:
    query = update.callback_query
    await query.answer()
    draft = _draft(context)
    data = query.data.split(":")
    action = data[0]

    if action == keyboards.CB_TOGGLE:
        _, _, value = data
        if value not in options:
            return getattr(State, field.upper())
        cur = set(draft[field])
        if value in cur:
            cur.remove(value)
        else:
            cur.add(value)
        draft[field] = list(cur)
        await query.edit_message_reply_markup(reply_markup=keyboard_fn(cur))
        return getattr(State, field.upper())

    if action == keyboards.CB_SKIP:
        draft[field] = []
    # DONE or SKIP fall through to next step
    await query.message.reply_text(
        next_prompt,
        parse_mode=ParseMode.HTML,
        reply_markup=next_keyboard_fn() if next_keyboard_fn else None,
    )
    return next_state


async def on_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _handle_multiselect(
        update, context, "schedule", SCHEDULE, keyboards.schedule_keyboard,
        next_state=State.EXPERIENCE,
        next_prompt=texts.ASK_EXPERIENCE,
        next_keyboard_fn=lambda: keyboards.experience_keyboard(set()),
    )


async def on_experience(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _handle_multiselect(
        update, context, "experience", EXPERIENCE, keyboards.experience_keyboard,
        next_state=State.EMPLOYMENT,
        next_prompt=texts.ASK_EMPLOYMENT,
        next_keyboard_fn=lambda: keyboards.employment_keyboard(set()),
    )


async def on_employment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _handle_multiselect(
        update, context, "employment", EMPLOYMENT, keyboards.employment_keyboard,
        next_state=State.TEXT,
        next_prompt=texts.ASK_TEXT,
        next_keyboard_fn=lambda: keyboards.skip_only_keyboard("text"),
    )


# ---------- free-text / skip-button steps ----------

async def on_text_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    _draft(context)["text"] = None
    await q.message.reply_text(
        texts.ASK_AREA, parse_mode=ParseMode.HTML,
        reply_markup=keyboards.skip_only_keyboard("area"),
    )
    return State.AREA


async def on_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    _draft(context)["text"] = update.message.text.strip()
    await update.message.reply_text(
        texts.ASK_AREA, parse_mode=ParseMode.HTML,
        reply_markup=keyboards.skip_only_keyboard("area"),
    )
    return State.AREA


async def on_area_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    _draft(context)["area"] = None
    await q.message.reply_text(
        texts.ASK_SALARY, parse_mode=ParseMode.HTML,
        reply_markup=keyboards.skip_only_keyboard("salary"),
    )
    return State.SALARY


async def on_area_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.message.text.strip()
    try:
        candidates = await areas.search_areas(query)
    except Exception:
        log.exception("area lookup failed")
        candidates = []

    if not candidates:
        await update.message.reply_text(
            texts.AREA_NOT_FOUND,
            reply_markup=keyboards.skip_only_keyboard("area"),
        )
        return State.AREA

    await update.message.reply_text(
        "Выбери вариант:",
        reply_markup=keyboards.area_candidates_keyboard(candidates),
    )
    return State.AREA


async def on_area_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    _, area_id = q.data.split(":", 1)
    _draft(context)["area"] = [area_id]
    await q.message.reply_text(
        texts.ASK_SALARY, parse_mode=ParseMode.HTML,
        reply_markup=keyboards.skip_only_keyboard("salary"),
    )
    return State.SALARY


async def on_salary_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    draft = _draft(context)
    draft["salary_min"] = None
    draft["currency"] = None
    return await _show_confirm(update, context)


async def on_salary_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    raw = update.message.text.strip().replace(" ", "").replace(",", "")
    try:
        value = int(raw)
        if value <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Нужно положительное число. Попробуй ещё раз или /cancel.")
        return State.SALARY
    _draft(context)["salary_min"] = value
    await update.message.reply_text(texts.ASK_CURRENCY, parse_mode=ParseMode.HTML,
                                    reply_markup=keyboards.currency_keyboard())
    return State.CURRENCY


async def on_currency_pick(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    _, code = q.data.split(":", 1)
    if code not in CURRENCIES:
        return State.CURRENCY
    _draft(context)["currency"] = code
    return await _show_confirm(update, context)


# ---------- confirm ----------

def _summarise(draft: dict) -> str:
    def fmt_list(field_name: str, mapping: dict[str, str]) -> str:
        vals = draft.get(field_name) or []
        if not vals:
            return "—"
        return ", ".join(mapping.get(v, v) for v in vals)

    area = draft.get("area") or []
    area_str = ", ".join(area) if area else "вся РФ"
    salary = draft.get("salary_min")
    currency = draft.get("currency") or ""
    salary_str = f"{salary} {currency}".strip() if salary else "—"

    return (
        f"Формат: {fmt_list('schedule', SCHEDULE)}\n"
        f"Грейд: {fmt_list('experience', EXPERIENCE)}\n"
        f"Занятость: {fmt_list('employment', EMPLOYMENT)}\n"
        f"Ключевые слова: {draft.get('text') or '—'}\n"
        f"Регион: {area_str}\n"
        f"Мин. ЗП: {salary_str}"
    )


async def _show_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    draft = _draft(context)
    text = texts.CONFIRM_HEADER + _summarise(draft)
    target = update.effective_message
    await target.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=keyboards.confirm_keyboard())
    return State.CONFIRM


async def on_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    q = update.callback_query
    await q.answer()
    _, action = q.data.split(":", 1)
    if action == "restart":
        context.user_data["draft"] = {"schedule": [], "experience": [], "employment": []}
        await q.message.reply_text(
            texts.ASK_SCHEDULE, parse_mode=ParseMode.HTML,
            reply_markup=keyboards.schedule_keyboard(set()),
        )
        return State.SCHEDULE

    # save
    user_id = update.effective_user.id
    await repository.save_filter(user_id, _draft(context))
    await q.message.reply_text(texts.SAVED)
    context.user_data.clear()
    return ConversationHandler.END


def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", cmd_start)],
        states={
            State.SCHEDULE: [CallbackQueryHandler(on_schedule, pattern=r"^(tog|done|skip):schedule")],
            State.EXPERIENCE: [CallbackQueryHandler(on_experience, pattern=r"^(tog|done|skip):experience")],
            State.EMPLOYMENT: [CallbackQueryHandler(on_employment, pattern=r"^(tog|done|skip):employment")],
            State.TEXT: [
                CallbackQueryHandler(on_text_skip, pattern=r"^skip:text$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_text_input),
            ],
            State.AREA: [
                CallbackQueryHandler(on_area_skip, pattern=r"^skip:area$"),
                CallbackQueryHandler(on_area_pick, pattern=r"^area_pick:"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_area_input),
            ],
            State.SALARY: [
                CallbackQueryHandler(on_salary_skip, pattern=r"^skip:salary$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, on_salary_input),
            ],
            State.CURRENCY: [CallbackQueryHandler(on_currency_pick, pattern=r"^cur:")],
            State.CONFIRM: [CallbackQueryHandler(on_confirm, pattern=r"^cfm:")],
        },
        fallbacks=[CommandHandler("cancel", cmd_cancel)],
        name="onboarding",
        persistent=False,
    )


def register(app: Application) -> None:
    app.add_handler(build_conversation_handler())
