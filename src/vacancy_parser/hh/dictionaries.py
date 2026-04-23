"""Static reference for hh.ru enum values used in filters.

Full dictionaries can be fetched at runtime from https://api.hh.ru/dictionaries
(for names/localization) and https://api.hh.ru/areas, /industries, /professional_roles.
"""

# /vacancies `schedule`
SCHEDULE = {
    "fullDay": "Полный день",
    "shift": "Сменный график",
    "flexible": "Гибкий график",
    "remote": "Удаленная работа",
    "flyInFlyOut": "Вахтовый метод",
}

# /vacancies `employment`
EMPLOYMENT = {
    "full": "Полная занятость",
    "part": "Частичная занятость",
    "project": "Проектная работа",
    "volunteer": "Волонтёрство",
    "probation": "Стажировка",
}

# /vacancies `experience`
EXPERIENCE = {
    "noExperience": "Нет опыта (Стажер)",
    "between1And3": "От 1 до 3 лет (Джуниор)",
    "between3And6": "От 3 до 6 лет (Мидл)",
    "moreThan6": "Более 6 лет (Сеньор+)",
}

# Common currencies supported by hh
CURRENCIES = ("RUR", "USD", "EUR", "KZT", "UAH", "BYR")
