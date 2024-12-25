from datetime import datetime

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from procollab_skills.celery import app
from procollab_skills.settings import EMAIL_USER


@app.task
def send_webinar_oline_link_email(
    user_email: str,
    webinar_online_link: str,
    webinar_title: str,
    webinar_description: str,
    webinar_datetime: datetime,
):
    webinar_start: str = webinar_datetime.strftime("%d.%m.%Y %H:%M")
    context = {
        "webinar_online_link": webinar_online_link,
        "webinar_title": webinar_title,
        "webinar_description": webinar_description,
        "webinar_start": webinar_start,
    }
    email_html_message = render_to_string("email/webinar_registration.html", context=context)
    email = EmailMessage(
        subject="Procollab | Вебинар",
        body=email_html_message,
        from_email=EMAIL_USER,
        to=[user_email],
    )
    email.content_subtype = "html"
    email.send(fail_silently=False)
