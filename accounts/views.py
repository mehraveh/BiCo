from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, get_user_model

from .forms import RegisterForm, ClientSearchForm, ClientCreateForm, TalentAssessmentForm
from .models import TalentAssessment

User = get_user_model()


@login_required
def home(request):
    return render(request, "accounts/home.html")


@require_http_methods(["GET", "POST"])
def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
            return redirect("home")
        messages.error(request, "لطفاً خطاهای فرم را بررسی کنید.")

    return render(request, "accounts/register.html", {"form": form})


@login_required
def talent_start(request):
    form = ClientSearchForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        nc = form.cleaned_data["national_code"]
        client = User.objects.filter(role=User.Role.CLIENT, national_code=nc).first()

        if client:
            return redirect("talent_new", client_id=client.id)

        return redirect(f"{reverse('client_create')}?national_code={nc}")

    return render(request, "accounts/talent_start.html", {"form": form})


@login_required
def client_create(request):
    initial = {}
    nc = request.GET.get("national_code")
    if nc:
        initial["national_code"] = nc

    form = ClientCreateForm(request.POST or None, initial=initial)

    if request.method == "POST" and form.is_valid():
        client = form.save()
        return redirect("talent_new", client_id=client.id)

    return render(request, "accounts/client_create.html", {"form": form})


@login_required
def talent_new(request, client_id):
    client = get_object_or_404(User, id=client_id, role=User.Role.CLIENT)
    form = TalentAssessmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        ta = form.save(commit=False)
        ta.client = client
        ta.created_by = request.user

        if request.user.role in [User.Role.THERAPIST, User.Role.ASSESSOR]:
            ta.assessor = request.user

        ta.save()
        return redirect("talent_detail", pk=ta.pk)

    return render(request, "accounts/talent_form.html", {"form": form, "client": client})


@login_required
def talent_detail(request, pk):
    ta = get_object_or_404(TalentAssessment, pk=pk)
    return render(request, "accounts/talent_detail.html", {"ta": ta})


@login_required
def questionnaires_home(request):
    """
    صفحه انتخاب نوع پرسشنامه
    """
    return render(request, "accounts/questionnaires_home.html")