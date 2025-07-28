from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Client, Message, Mailing


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["email", "full_name", "comment"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["title", "body"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "body": forms.Textarea(attrs={"class": "form-control"}),
        }


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ["start_datetime", "end_datetime", "status", "message", "recipients"]
        widgets = {
            "start_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "end_datetime": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "status": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Select(attrs={"class": "form-select"}),
            "recipients": forms.SelectMultiple(attrs={"class": "form-select"}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="Обязательное поле. Введите корректный email."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
