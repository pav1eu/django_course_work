from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
    TemplateView,
)
from .models import Client, Message, Mailing, MailingAttempt
from .forms import ClientForm, MessageForm, MailingForm, CustomUserCreationForm
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


from .permissions import OwnerOrManagerMixin


# Create your views here.
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "account/signup.html"
    success_url = reverse_lazy("user:login")


class ClientListView(ListView):
    model = Client
    template_name = "user/client_list.html"
    context_object_name = "client_list"


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "user/client_form.html"
    success_url = reverse_lazy("user:client_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "user/client_form.html"
    success_url = reverse_lazy("user:client_list")


class ClientDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Client
    template_name = "user/client_confirm_delete.html"
    success_url = reverse_lazy("user:client_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "user/message_list.html"
    context_object_name = "message"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "user/message_form.html"
    success_url = reverse_lazy("user:message_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(OwnerOrManagerMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "user/message_form.html"
    success_url = reverse_lazy("user:message_list")


class MessageDeleteView(OwnerOrManagerMixin, DeleteView):
    model = Message
    template_name = "user/message_confirm_delete.html"
    success_url = reverse_lazy("user:message_list")


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "user/mailing_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.groups.filter(name="Менеджер").exists():
            return qs
        return qs.filter(owner=self.request.user)


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = "user/mailing_form.html"
    success_url = reverse_lazy("user:mailing_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, OwnerOrManagerMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "user/mailing_form.html"
    success_url = reverse_lazy("user:mailing_list")


class MailingDeleteView(LoginRequiredMixin, OwnerOrManagerMixin, DeleteView):
    model = Mailing
    template_name = "user/mailing_confirm_delete.html"
    success_url = reverse_lazy("user:mailing_list")


class MailingDetailView(LoginRequiredMixin, OwnerOrManagerMixin, DetailView):
    model = Mailing
    template_name = "user/mailing_detail.html"
    context_object_name = "mailing"


class SendMailingView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        result = mailing.send()
        messages.success(
            request,
            f"Рассылка отправлена. Успешно: {result['success']}, Ошибки: {result['failed']}",
        )
        return redirect("user:mailing_detail", pk=pk)


class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = "user/mailing_attempt_list.html"
    context_object_name = "attempts"

    def get_queryset(self):
        return MailingAttempt.objects.filter(mailing_id=self.kwargs["pk"]).order_by(
            "-timestamp"
        )


@method_decorator(cache_page(60 * 5), name="dispatch")
class HomePageView(TemplateView):
    template_name = "user/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_mailings"] = Mailing.objects.count()
        context["active_mailings"] = Mailing.objects.filter(status="Запущена").count()
        context["unique_clients"] = Client.objects.count()
        return context


class UserStatsView(LoginRequiredMixin, TemplateView):
    template_name = "user/user_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempts = MailingAttempt.objects.filter(mailing__owner=self.request.user)
        context.update(
            {
                "total": attempts.count(),
                "success": attempts.filter(status="Успешно").count(),
                "failed": attempts.filter(status="Не успешно").count(),
            }
        )
        return context
