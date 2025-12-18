# src/cs_robots/urls.py
from django.urls import path
from cs_robots.views import edit_robots_txt


urlpatterns = [
    path("edit-robots-txt/", edit_robots_txt, name="edit_robots_txt"),
]
