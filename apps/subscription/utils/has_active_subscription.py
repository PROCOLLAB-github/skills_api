from datetime import date

from dateutil.relativedelta import relativedelta


def user_has_active_subscription(user):
    if user.is_superuser or user.is_staff:
        return True

    user_profile = getattr(user, "profiles", None)
    if not user_profile:
        return False

    last_subscription_type = getattr(user_profile, "last_subscription_type", None)
    last_subscription_date = getattr(user_profile, "last_subscription_date", None)

    if not last_subscription_type or not isinstance(last_subscription_date, date):
        return False

    subscription_valid_until = last_subscription_date + relativedelta(months=1)
    return date.today() < subscription_valid_until
