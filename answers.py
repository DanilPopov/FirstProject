def get_answer(question):
    question_lower = question.lower()
    answers = {'привет': 'И тебе привет!', "как дела": "Лучше всех!", "пока": "Увидимся"}
    return answers[question_lower]
user_phrase = input('')
print(get_answer(str(user_phrase)))