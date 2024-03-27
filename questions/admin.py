from django.contrib import admin

from questions.models import QuestionSingleAnswer, SingleAnswer, InfoSlide, QuestionConnect, ConnectAnswer


@admin.register(QuestionConnect)
class QuestionConnectAdmin(admin.ModelAdmin):
    pass


@admin.register(ConnectAnswer)
class ConnectAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestionSingleAnswer)
class QuestionSingleAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(SingleAnswer)
class SingleAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(InfoSlide)
class InfoSlideAdmin(admin.ModelAdmin):
    pass
