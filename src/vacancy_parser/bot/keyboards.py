from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from vacancy_parser.bot import texts
from vacancy_parser.hh.dictionaries import CURRENCIES, EMPLOYMENT, EXPERIENCE, SCHEDULE

# Callback data prefixes
CB_TOGGLE = "tog"      # tog:<field>:<value>
CB_DONE = "done"       # done:<field>
CB_SKIP = "skip"       # skip:<field>
CB_CURRENCY = "cur"    # cur:<code>
CB_CONFIRM = "cfm"     # cfm:save | cfm:restart


def _multi_select(field: str, options: dict[str, str], selected: set[str]) -> InlineKeyboardMarkup:
    rows = []
    for key, label in options.items():
        mark = "✅ " if key in selected else "▫️ "
        rows.append([InlineKeyboardButton(mark + label, callback_data=f"{CB_TOGGLE}:{field}:{key}")])
    rows.append([
        InlineKeyboardButton(texts.SKIP, callback_data=f"{CB_SKIP}:{field}"),
        InlineKeyboardButton(texts.DONE, callback_data=f"{CB_DONE}:{field}"),
    ])
    return InlineKeyboardMarkup(rows)


def schedule_keyboard(selected: set[str]) -> InlineKeyboardMarkup:
    return _multi_select("schedule", SCHEDULE, selected)


def experience_keyboard(selected: set[str]) -> InlineKeyboardMarkup:
    return _multi_select("experience", EXPERIENCE, selected)


def employment_keyboard(selected: set[str]) -> InlineKeyboardMarkup:
    return _multi_select("employment", EMPLOYMENT, selected)


def skip_only_keyboard(field: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(texts.SKIP, callback_data=f"{CB_SKIP}:{field}")]]
    )


def area_candidates_keyboard(candidates: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    """candidates: list of (area_id, display_name)."""
    rows = [[InlineKeyboardButton(name, callback_data=f"area_pick:{aid}")] for aid, name in candidates]
    rows.append([InlineKeyboardButton(texts.SKIP, callback_data=f"{CB_SKIP}:area")])
    return InlineKeyboardMarkup(rows)


def currency_keyboard() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(c, callback_data=f"{CB_CURRENCY}:{c}")] for c in CURRENCIES[:3]]
    return InlineKeyboardMarkup(rows)


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(texts.CONFIRM_SAVE, callback_data=f"{CB_CONFIRM}:save"),
            InlineKeyboardButton(texts.CONFIRM_RESTART, callback_data=f"{CB_CONFIRM}:restart"),
        ]
    ])
