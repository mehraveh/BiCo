from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import TalentAssessment

User = get_user_model()


# -------------------------
# 1) Register (for STAFF/ADMIN accounts)
# -------------------------
class RegisterForm(UserCreationForm):
    # Make sure the form shows these explicitly (especially role)
    role = forms.ChoiceField(
        label="نقش/موقعیت",
        choices=User.Role.choices,
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
        required=True,
    )

    national_code = forms.CharField(
        label="کد ملی",
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "inputmode": "numeric",
            "placeholder": "۱۰ رقم",
            "autocomplete": "off",
        })
    )

    phone = forms.CharField(
        label="شماره تلفن",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "inputmode": "numeric",
            "placeholder": "مثلاً 0912...",
            "autocomplete": "off",
        })
    )

    full_name = forms.CharField(
        label="نام و نام خانوادگی",
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "placeholder": "مثلاً مریم احمدی",
        })
    )

    date_of_birth = forms.DateField(
        label="تاریخ تولد",
        required=True,
        widget=forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date"})
    )

    gender = forms.ChoiceField(
        label="جنسیت",
        choices=User.Gender.choices,
        required=True,
        widget=forms.Select(attrs={"class": "form-select form-select-lg"}),
    )

    email = forms.EmailField(
        label="ایمیل (اختیاری)",
        required=False,
        widget=forms.EmailInput(attrs={"class": "form-control form-control-lg"}),
    )

    bio = forms.CharField(
        label="شرح حال / توضیحات (اختیاری)",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control form-control-lg", "rows": 3}),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "role",
            "national_code",
            "phone",
            "full_name",
            "date_of_birth",
            "gender",
            "email",
            "bio",
            "password1",
            "password2",
        )
        labels = {
            "username": "نام کاربری",
            "password1": "رمز عبور",
            "password2": "تکرار رمز عبور",
        }

    def clean_national_code(self):
        nc = (self.cleaned_data.get("national_code") or "").strip()
        if not nc.isdigit() or len(nc) != 10:
            raise forms.ValidationError("کد ملی باید دقیقاً ۱۰ رقم باشد.")
        return nc

    def clean_phone(self):
        ph = (self.cleaned_data.get("phone") or "").strip()
        digits = "".join([c for c in ph if c.isdigit()])
        if len(digits) < 10:
            raise forms.ValidationError("شماره تلفن معتبر وارد کنید.")
        return digits

    def save(self, commit=True):
        user = super().save(commit=False)

        # copy extra fields onto your custom User model
        user.role = self.cleaned_data["role"]
        user.national_code = self.cleaned_data["national_code"]
        user.phone = self.cleaned_data["phone"]
        user.full_name = self.cleaned_data["full_name"]
        user.date_of_birth = self.cleaned_data["date_of_birth"]
        user.gender = self.cleaned_data["gender"]
        user.email = self.cleaned_data.get("email", "")
        user.bio = self.cleaned_data.get("bio", "") or ""

        if commit:
            user.save()
        return user

# -------------------------
# 2) Small field: search client by national_code
# -------------------------
class ClientSearchForm(forms.Form):
    national_code = forms.CharField(
        label="کد ملی کلاینت",
        max_length=10,
        widget=forms.TextInput(attrs={
            "class": "form-control form-control-lg",
            "inputmode": "numeric",
            "placeholder": "مثلاً 1234567890",
            "autocomplete": "off",
        })
    )

    def clean_national_code(self):
        nc = self.cleaned_data["national_code"].strip()
        if (not nc.isdigit()) or len(nc) != 10:
            raise forms.ValidationError("کد ملی باید ۱۰ رقم باشد.")
        return nc


# -------------------------
# 3) Create client (User with role=CLIENT)
# -------------------------
class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("national_code", "phone", "full_name", "date_of_birth", "gender", "bio")
        labels = {
            "national_code": "کد ملی",
            "phone": "شماره تلفن",
            "full_name": "نام و نام خانوادگی",
            "date_of_birth": "تاریخ تولد",
            "gender": "جنسیت",
            "bio": "شرح حال (اختیاری)",
        }
        widgets = {
            "national_code": forms.TextInput(attrs={"class": "form-control form-control-lg", "inputmode": "numeric"}),
            "phone": forms.TextInput(attrs={"class": "form-control form-control-lg", "inputmode": "numeric"}),
            "full_name": forms.TextInput(attrs={"class": "form-control form-control-lg"}),
            "date_of_birth": forms.DateInput(attrs={"class": "form-control form-control-lg", "type": "date"}),
            "gender": forms.Select(attrs={"class": "form-select form-select-lg"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.role = User.Role.CLIENT
        # optional: generate username automatically if you want
        if not obj.username:
            obj.username = f"client_{obj.national_code}"
        if commit:
            obj.save()
        return obj


# -------------------------
# 4) Talent assessment form
# -------------------------
class TalentAssessmentForm(forms.ModelForm):
    class Meta:
        model = TalentAssessment
        fields = [
            "assessment_date",

            "coach_motor", "coach_cognitive", "coach_social", "coach_emotional",
            "parent_motor", "parent_cognitive", "parent_social", "parent_emotional",

            "motor_peer", "cognitive_peer", "social_peer", "emotional_peer",
            "notes",
        ]
        labels = {
            "assessment_date": "تاریخ ارزیابی",

            "coach_motor": "حرکتی (مربی)",
            "coach_cognitive": "شناختی (مربی)",
            "coach_social": "اجتماعی (مربی)",
            "coach_emotional": "هیجانی (مربی)",

            "parent_motor": "حرکتی (والد)",
            "parent_cognitive": "شناختی (والد)",
            "parent_social": "اجتماعی (والد)",
            "parent_emotional": "هیجانی (والد)",

            "motor_peer": "وضعیت حرکتی نسبت به همسالان",
            "cognitive_peer": "وضعیت شناختی نسبت به همسالان",
            "social_peer": "وضعیت اجتماعی نسبت به همسالان",
            "emotional_peer": "وضعیت هیجانی نسبت به همسالان",

            "notes": "توضیحات (اختیاری)",
        }
        widgets = {
            "assessment_date": forms.DateInput(attrs={"type": "date", "class": "form-control form-control-lg"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({"class": "form-select form-select-lg"})
            elif "class" not in field.widget.attrs:
                field.widget.attrs.update({"class": "form-control form-control-lg"})