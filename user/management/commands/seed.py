from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from user.models import CustomUser, Client, Message, Mailing
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Заполняет базу тестовыми данными"

    def handle(self, *args, **kwargs):
        # Создание группы "Менеджеры"
        manager_group, created = Group.objects.get_or_create(name="Менеджеры")
        if created:
            self.stdout.write("Группа Менеджеры создана")
        else:
            self.stdout.write("Группа Менеджеры уже существует")

        # Назначим разрешение только на просмотр
        mailing_content_type = ContentType.objects.get_for_model(Mailing)
        permission = Permission.objects.get(
            codename="view_mailing", content_type=mailing_content_type
        )
        manager_group.permissions.add(permission)

        # Создание менеджера
        manager, created = CustomUser.objects.get_or_create(
            email="manager@example.com",
            defaults={"username": "manager", "is_staff": True, "is_active": True},
        )
        if created:
            manager.set_password("manager123")
            manager.save()
            manager.groups.add(manager_group)
            self.stdout.write("Менеджер создан")
        else:
            self.stdout.write("Менеджер уже существует")

        # Создание обычного пользователя
        user, created = CustomUser.objects.get_or_create(
            email="user@example.com", defaults={"username": "user", "is_active": True}
        )
        if created:
            user.set_password("user123")
            user.save()
            self.stdout.write("Пользователь создан")
        else:
            self.stdout.write("Пользователь уже существует")

        # Создание клиента
        client, _ = Client.objects.get_or_create(
            email="client@example.com",
            full_name="Иван Иванов",
            comment="Тестовый клиент",
        )

        # Создание сообщения
        message, _ = Message.objects.get_or_create(
            title="Приветствие", body="Добро пожаловать в нашу рассылку!"
        )

        # Создание рассылки
        Mailing.objects.get_or_create(
            owner=user,
            start_datetime=timezone.now(),
            end_datetime=timezone.now() + timezone.timedelta(days=1),
            status="created",
            message=message,
        )

        self.stdout.write(self.style.SUCCESS("База успешно заполнена."))
