from django.shortcuts import render

# Create your views here.


# GET задания
# request: /courses/{task_id}
# response:
a = {
    "count": int,  # количество "шагов" всего
    "step_data": [
        {
            "id": int,
            "type": str,  # на выбор из: "connection", "single_correct", "exclude_wrong", "upload_file"
            "is_done": bool,  # если человек это уже проходил - true. если нет - false
        }
    ],
}

# GET информационного слайда
# request: /courses/info-slide/{id}
# response:
b = {"text": str, "file": str or None}  # url файла


# GET единичного вопроса
# request: /courses/single-correct/{id}
# response:
c = {
    "question_text": str,
    "description": str or None,
    "file": str or None,
    "answers": [{"id": int, "answer_text": str}],
}


# POST единичного запроса
# request: /courses/single-correct/{answer_id}
# response:
e = {
    "is_correct": bool,
    "correct_answer": int
    or None,  # выдаёт id правильного ответа, если is_correct = false. иначе - null
}

# GET вопроса на соотношение
# request: /courses/connect/{id}
# response:
f = {
    "question_text": str or None,
    "connect_left": [{"id": int, "text": str}],
    "connect_right": [{"text": str}],
}

# POST вопроса на соотношение
# request: /courses/connect/{question_id}
# body:
g = [{"left_id": int, "right_text": str}]
# response:
h = [{"left_id": int, "right_text": str, "is_correct": bool}]

# GET вопроса на исключение
# request: /courses/exclude/{question_id}
# response:
i = {
    "question_text": str,
    "question_description": str or None,
    "options": [{"id": int, "text": str}],
}

# POST вопроса на исключение
# request: /courses/exclude/{question_id}
# body:
j = [int]  # список всех id ответов, которые юзер исключил
# response:
k = [int]  # список всех неправильно исключённых id ответов

# GET вопроса на загрузку файлов

# POST вопроса на загрузку файлов
