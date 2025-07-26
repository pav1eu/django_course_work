from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    full_name = models.CharField(max_length=100, verbose_name="ФИО")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    ACCOUNT_AUTHENTICATION_METHOD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Message(models.Model):
    title = models.CharField(max_length=100, verbose_name="Тема письма")
    body = models.TextField(blank=True, null=True, verbose_name="Содержимое письма")

    def __str__(self):
        return self.title


class Mailing(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец"
    )
    STATUS_CHOICES = [
        ("created", "Создана"),
        ("started", "Запущена"),
        ("completed", "Завершена"),
    ]

    start_datetime = models.DateTimeField(verbose_name="Дата и время начала")
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="created")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = (("can_view_all_mailings", "Can view all mailings"),)

    def update_status(self):
        now = timezone.now()
        if self.end_datetime < now:
            self.status = "completed"
        elif self.start_datetime <= now:
            self.status = "started"
        else:
            self.status = "created"
        self.save()

    def __str__(self):
        return f"Рассылка #{self.id} - {self.get_status_display()}"

    def send(self):
        success = 0
        failed = 0
        logs = []
        for client in self.recipients.all():
            try:
                send_mail(
                    subject=self.message.title,
                    message=self.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                status = "Успешно"
                response = "OK"
                success += 1
            except Exception as e:
                status = "Не успешно"
                response = str(e)
            MailingAttempt.objects.create(
                mailing=self,
                timestamp=timezone.now(),
                status=status,
                server_response=response,
            )
            logs.append(f"{client.email}: {status} — {response}")

        self.status = "completed" if timezone.now() >= self.end_datetime else "launched"
        self.last_run = timezone.now()
        self.last_result = (
            f"Успешно: {success}, Ошибок: {len(logs) - success}\n" + "\n".join(logs)
        )
        self.save()
        return {"success": success, "failed": len(logs) - success}


class MailingAttempt(models.Model):
    STATUS_CHOICES = (
        ("Успешно", "Успешно"),
        ("Не успешно", "Не успешно"),
    )

    mailing = models.ForeignKey(
        "Mailing",
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name="Рассылка",
    )
    timestamp = models.DateTimeField(
        default=timezone.now, verbose_name="Дата и время попытки"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, verbose_name="Статус"
    )
    server_response = models.TextField(
        blank=True, null=True, verbose_name="Ответ почтового сервера"
    )

    class Meta:
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.timestamp:%d.%m.%Y %H:%M} — {self.status}"
