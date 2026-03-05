from celery import Celery
from asgiref.sync import async_to_sync

from src.mail import create_message, mail

c_app = Celery()

c_app.config_from_object("src.config")


@c_app.task()
def send_email(emails: list[str], subject: str, body: str):
    message = create_message(emails, subject, body)
    async_to_sync(mail.send_message)(message)


# run celery worker using  "celery -A src.celery_tasks.c_app worker"
