from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from user.models import Mailing, MailingAttempt
from django.utils import timezone


class Command(BaseCommand):
    help = "Отправка рассылки вручную"

    def add_arguments(self, parser):
        parser.add_argument("mailing_id", type=int)

    def handle(self, *args, **kwargs):
        mailing_id = kwargs["mailing_id"]
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
            result = mailing.send()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Рассылка #{mailing_id} отправлена: {result['success']} успешно, {result['failed']} с ошибками"
                )
            )
        except Mailing.DoesNotExist:
            self.stdout.write(self.style.ERROR("Рассылка не найдена"))

    def send_mailing(mailing):
        for client in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.title,
                    message=mailing.message.body,
                    from_email="your_email@example.com",
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = "Успешно"
                response = "Письмо успешно отправлено"
            except Exception as e:
                status = "Не успешно"
                response = str(e)

            MailingAttempt.objects.create(
                mailing=mailing,
                timestamp=timezone.now(),
                status=status,
                server_response=response,
            )
