from django.urls import path

from .views import command, csrf_token, voice

app_name = "gmed_liza_api"

urlpatterns = [
    path("csrf/", csrf_token, name="csrf"),
    path("command/", command, name="command"),
    path("voice/", voice, name="voice"),
]
