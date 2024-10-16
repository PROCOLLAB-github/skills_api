from django.contrib import admin

# Register your models here.
from subscription.models import SubscriptionType


@admin.register(SubscriptionType)
class SubscriptionTypesAdmin(admin.ModelAdmin):
    pass
