import importlib

from django.conf import settings
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.views.generic import ListView


models = importlib.import_module(settings.MODELS_MODULE + ".models")


class SubtaskListView(ListView):
    model = models.Subtask
    ordering = ["name"]
    template_name = "views/subtask_list.html"

    paginate_by = 10

    # max number of pagination links to show (excluding current page)
    link_count = 20

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.select_related("task", "task__project", "task__project__account")

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data["title"] = self.model._meta.object_name + pluralize(10)

        # better page links than just "next"/"prev"
        if data["is_paginated"]:
            page = data["page_obj"].number
            num_pages = data["page_obj"].paginator.num_pages
            page_numbers = range(max(1, page - self.link_count // 2), min(num_pages, page + self.link_count // 2))
            data["page_links"] = {
                n: reverse("subtasks_page", kwargs={"page": n}) if n != 1 else reverse("subtasks")
                for n in page_numbers
            }

        return data
