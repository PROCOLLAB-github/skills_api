# Generated by Django 5.0.3 on 2024-05-14 16:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("questions", "0003_answerconnect_file_left_answerconnect_file_right_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="questionsingleanswer",
            options={
                "verbose_name": "Вопрос с одним правильным ответом",
                "verbose_name_plural": "Вопросы с одним правильным ответом",
            },
        ),
    ]
