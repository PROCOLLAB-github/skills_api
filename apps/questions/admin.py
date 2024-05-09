from django.contrib import admin

from questions.models import (
    QuestionSingleAnswer,
    AnswerSingle,
    InfoSlide,
    QuestionConnect,
    AnswerConnect,
    QuestionWrite,
)


class ConnectAnswersInline(admin.TabularInline):  # Или StackedInline для другого стиля отображения
    model = AnswerConnect
    extra = 0


@admin.register(QuestionConnect)
class QuestionConnectAdmin(admin.ModelAdmin):
    inlines = [ConnectAnswersInline]


class SingleAnswersInline(admin.StackedInline):
    model = AnswerSingle
    extra = 0


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(admin.ModelAdmin):
    inlines = [SingleAnswersInline]


@admin.register(InfoSlide)
class InfoSlideAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionWrite)
class QuestionWriteAdmin(admin.ModelAdmin):
    pass
