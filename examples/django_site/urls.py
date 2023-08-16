import importlib

from django.conf import settings
from django.urls import path
from django.urls import reverse_lazy
from django.views.generic import RedirectView

views = importlib.import_module(settings.MODELS_MODULE + ".views")

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("subtasks")), name="homepage"),
    path("subtasks/", views.SubtaskListView.as_view(), name="subtasks"),
    path("subtasks/<int:page>/", views.SubtaskListView.as_view(), name="subtasks_page"),
]
