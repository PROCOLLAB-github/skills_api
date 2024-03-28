from django.contrib import admin

from questions.models import (
    QuestionSingleAnswer,
    SingleAnswer,
    InfoSlide,
    QuestionConnect,
    ConnectAnswer,
)


class ConnectAnswersInline(admin.TabularInline):  # Или StackedInline для другого стиля отображения
    model = ConnectAnswer
    extra = 0


@admin.register(QuestionConnect)
class QuestionConnectAdmin(admin.ModelAdmin):
    inlines = [ConnectAnswersInline]


@admin.register(ConnectAnswer)
class ConnectAnswerAdmin(admin.ModelAdmin):
    pass


class SingleAnswersInline(admin.StackedInline):
    model = SingleAnswer
    extra = 0


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(admin.ModelAdmin):
    inlines = [SingleAnswersInline]


@admin.register(SingleAnswer)
class SingleAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(InfoSlide)
class InfoSlideAdmin(admin.ModelAdmin):
    pass
