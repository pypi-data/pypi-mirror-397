# src/cs_robots/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404, HttpResponse

# core/views.py
from django.shortcuts import redirect, render

from .apps import CSRobotsConfig
from .forms import RobotsTxtForm


@staff_member_required
def edit_robots_txt(request):
    file_path = getattr(settings, "ROBOTS_TXT_PATH", "")
    initial_content = ""

    # Intentar leer el contenido actual del fichero
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            initial_content = f.read()
    except FileNotFoundError:
        messages.warning(
            request, "The robots.txt file did not exist and will be created."
        )
    except Exception as e:
        messages.error(request, f"Error reading the file: {e}")

    if request.method == "POST":
        form = RobotsTxtForm(request.POST)
        if form.is_valid():
            try:
                # Escribir el nuevo contenido en el fichero
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(form.cleaned_data["content"])
                messages.success(request, "robots.txt file saved successfully!")
                return redirect("edit_robots_txt")  # Redirigir para mostrar el éxito
            except Exception as e:
                messages.error(request, f"Error saving the file: {e}")
    else:
        # Mostrar el formulario con el contenido actual
        form = RobotsTxtForm(initial={"content": initial_content})
    context = {
        "title": "Edit robots.txt",
        "form": form,
        "opts": {"app_label": CSRobotsConfig.name},
    }
    return render(request, "cs_robots/edit_cs_robots.html", context)


def serve_robots_txt(request):

    try:
        file_path = settings.ROBOTS_TXT_PATH
    except AttributeError:
        raise ImproperlyConfigured("ROBOTS_TXT_PATH is not defined in settings.py")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HttpResponse(content, content_type="text/plain")
    except FileNotFoundError:
        raise Http404("robots.txt not found.")
