Этот фалик нужен, чтобы по быстрому ввести тебя в курс дела.

**Че за проект?**
Веб-приложение типа степика, куда люди будут заходить, покупать подписки на курсы, и проходить разные курсы. Пока что с партнёрами мы только договариваемся, так что на данных момент их 1-2 штуки.

**Какие есть приложения?**
- courses. это приложение, где лежит функционал, 
связанный с задачами и навыками. навык - это курс. задача - это набор вопросов

- files. приложение, которое позволяет обслуживать статик файлы (картинки)
через Selectel Swift API. вкраце, работает это так: в модели храним ссылку и разрешение, а сам файл загружаем в "объектное хранилище"

- questions. тут лежит логика самих вопросов. 
пока что есть: вопрос на соотношение, вопрос с единичным ответом / на исключение неправильных ответов, 
информационный слайд (тупо текст). надо добавить: вопрос с вводом текста и вопрос с загрузкой файлов

- progress. тут функционал делится на 2: вывод инфы о профилях, и отслеживание выполнения заданий 
(т.е. когда человек проходит задание, создаётся запись в БД). тут же и авторизация (надо бы тогда его в users преименовать, наверное...)

- subscriptions. тут по сути ображения к Yookassa API. много dataclasses, много обращений к API, и тут есть задачи на celery и celery-beat

**Где БД?**
Юзаем облачное БД от Selectel.

**Какие есть необычные технологии?**
- Yookassa API для оплаты подписок
- для авто-доки юзаем DRF-spectacular. гораздо удобнее drf_yasg
- Poetry для менеджмента зависимостей
- более активное использование celery-beat, чем обычно
- для авто-рефакторинга: 
black (чистат синтаксис), 
flake8 (делает то же самое + указывает на неиспользоуемые зависимости), 
ну и в будущем интегрируем pyright (static type анализатор, т.е. че-то типа проверки на этапе компиляции в  других языках) в pre-commit-hooks
- мелочь: создание сериализаторов на основе dataclasses. по мне так удобно. можно и для тайп-хинтов юзать. особенно полезно, когда работаешь с инородными API

**Каковы принципы архитектуры и кода?**
- разный функционал кидать в разные папки. 
типы в typing.py, сериализаторы в serializers.py. маппинги в mapping.py. 

- желательно разбивать проект по приложениям основываясь исключительно на их логичецкой цельности, а не размер.
не совмещать в одном приложении несвязанный друг с другом функционал.

- можно делать вместо views.py папку views и туда уже кидать вьюхи в разных файлах 
(затем впиши все нужные зависимости, которые отсюда будешь импортировать, в __init__.py этой папки, чтоб удобнее было. 
то же самое с models, то же самое с utils

- файлы по типу utils.py или services.py желательно по максимуму минимизироовать, 
вместо этого создав папку utils, где отдельный функционал кидать в отдельные папки

-активное использование type-hints приветствуется. применение dataclasses и enums тоже приветствуется, но с этим лучше не перебарщивать


**Как запустить?**
1. клонируешь репозиторий в папку
2. делаешь .env на основе .env.example, не забудь DEBUG на True поставить
3. вводишь в консоль ``` docker-compose -f docker-compose.dev-ci.yml up --build```
4. создаешь супер-юзера путём команды ```docker exec -it skills_web sh -c "cd apps && python manage.py createsuperuser"```
5. приложение работает на порту 8001. документация на странице /docs/
