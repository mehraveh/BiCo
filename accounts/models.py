from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "ادمین"
        THERAPIST = "THERAPIST", "تراپیست"
        ASSESSOR = "ASSESSOR", "ارزیاب"
        CLIENT = "CLIENT", "کلاینت"

    role = models.CharField(max_length=15, choices=Role.choices, default=Role.CLIENT)

    # required for ALL users
    national_code = models.CharField("کد ملی", max_length=10, unique=True, db_index=True)
    full_name = models.CharField("نام و نام خانوادگی", max_length=150)
    date_of_birth = models.DateField("تاریخ تولد")

    class Gender(models.TextChoices):
        F = "F", "دختر"
        M = "M", "پسر"
        O = "O", "سایر"

    gender = models.CharField("جنسیت", max_length=1, choices=Gender.choices)

    # optional fields
    phone = models.CharField("شماره تلفن", max_length=20, blank=True, default="")
    email = models.EmailField("ایمیل", blank=True)
    bio = models.TextField("شرح حال", blank=True, default="")

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class TalentAssessment(models.Model):
    PEER_STATUS_CHOICES = [
        ("1", "کمتر از همسالان"),
        ("1.5", "هم‌سطح همسالان"),
        ("2", "بالاتر از همسالان"),
    ]

    # این همون “کلاینت” هست (User با role=CLIENT)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="talent_assessments",
        limit_choices_to={"role": "CLIENT"},
    )

    # ثبت کننده رکورد (staff یا admin)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_talent_assessments",
        limit_choices_to={"role__in": ["ADMIN", "THERAPIST", "ASSESSOR"]},
    )

    assessor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True, blank=True,
        related_name="assessed_talent_assessments",
        limit_choices_to={"role__in": ["THERAPIST", "ASSESSOR"]},
    )

    assessment_date = models.DateField()

    # نمرات مربی
    coach_motor = models.PositiveSmallIntegerField()
    coach_cognitive = models.PositiveSmallIntegerField()
    coach_social = models.PositiveSmallIntegerField()
    coach_emotional = models.PositiveSmallIntegerField()
    coach_total_score = models.FloatField(null=True, blank=True)

    # نمرات والد (فعلاً به عنوان ورودی دوم؛ حتی اگر “والد اکانت ندارد”)
    parent_motor = models.PositiveSmallIntegerField()
    parent_cognitive = models.PositiveSmallIntegerField()
    parent_social = models.PositiveSmallIntegerField()
    parent_emotional = models.PositiveSmallIntegerField()
    parent_total_score = models.FloatField()

    # وضعیت نسبت به همسالان (یک بار برای هر دامنه)
    motor_peer = models.CharField(max_length=3, choices=PEER_STATUS_CHOICES)
    cognitive_peer = models.CharField(max_length=3, choices=PEER_STATUS_CHOICES)
    social_peer = models.CharField(max_length=3, choices=PEER_STATUS_CHOICES)
    emotional_peer = models.CharField(max_length=3, choices=PEER_STATUS_CHOICES)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)