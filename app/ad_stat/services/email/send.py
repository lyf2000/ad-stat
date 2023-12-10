
from django.conf import settings
from django.core.mail import EmailMessage


class EmailSenderService:
    def __init__(self, to: list[str], title: str, body: str, attachements: list | None = None):
        self.to = to
        self.title = title
        self.body = body
        self.attachements = attachements or []

    def send(self):
        mail = EmailMessage(self.title, self.body, settings.EMAIL_HOST_USER, self.to)
        for attach in self.attachements:
            mail.attach(attach[0], attach[1].read())
        mail.send()
