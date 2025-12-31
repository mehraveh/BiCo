from django.urls import path
from . import views

urlpatterns = [
    # Home
    path("", views.home, name="home"),

    # Auth
    path("register/", views.register, name="register"),

    # Talent
    path("talent/", views.talent_start, name="talent_start"),
    path("clients/new/", views.client_create, name="client_create"),
    path("talent/new/<int:client_id>/", views.talent_new, name="talent_new"),
    path("talent/<int:pk>/", views.talent_detail, name="talent_detail"),

    # Questionnaires (chooser + fill)
    path("questionnaires_home/", views.questionnaires_home, name="questionnaires_home"),
    #path("questionnaires/<str:code>/", views.questionnaire_fill, name="questionnaire_fill"),
]