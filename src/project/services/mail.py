from typing import Annotated

from fastapi import Depends
from project.repositories.celery import CeleryRepository
from project.repositories import CeleryRepoDep
import smtplib
from email.message import EmailMessage
from project.config import settings


class MailService:
    def __init__(self, celery_repo: CeleryRepository):
        self.repo = celery_repo
        self.smtp = smtplib.SMTP_SSL(host=settings.SMTP_HOST, port=settings.SMTP_PORT)

    async def send_message(
        self, from_email: str, to_email: str, subject: str | None, body: str, **kwargs
    ):
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(body)

        @self.repo.wrap_task
        def _msg():
            with self.smtp as smtp:
                smtp.login(settings.SMTP_LOGIN, settings.SMTP_PASSWORD)
                smtp.send_message(msg)

        return self.repo.send_task(_msg, **kwargs)


async def get_mail_service(celery_repo: CeleryRepoDep):
    return MailService(celery_repo)


MailServiceDep = Annotated[MailService, Depends(get_mail_service)]
