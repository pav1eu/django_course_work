from django.contrib import admin
from .models import Client, Message, Mailing, MailingAttempt


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email')
    search_fields = ('full_name', 'email')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'start_datetime', 'end_datetime', 'status')
    list_filter = ('status', 'start_datetime')
    search_fields = ('owner__username',)
    filter_horizontal = ('recipients',)  # удобный выбор получателей


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ('mailing', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('server_response',)
