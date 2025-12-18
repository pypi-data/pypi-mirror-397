[![Test Status](https://github.com/codesyntax/django-cs-robots/workflows/Test/badge.svg)](https://github.com/codesyntax/django-cs-robots/actions)
[![PyPI Version](https://img.shields.io/pypi/v/django-cs-robots.svg)](https://pypi.python.org/pypi/django-cs-robots)

# 🤖 Django CS Robots

A simple, database-free Django app to manage your `robots.txt` file directly from the admin interface.

## ✨ Introduction

This package provides a straightforward solution for allowing site administrators to edit the `robots.txt` file without developer intervention. Instead of storing the content in a database model, this app reads from and writes directly to a **physical file** on your server. The file's path is fully configurable in your project's `settings.py`.

## 🌟 Key Features

* **Edit in the Admin:** ✏️ Provides a simple and intuitive form within the Django admin to modify your `robots.txt` content.
* **Database-Free:** 💾 Directly reads from and writes to a file on the filesystem, avoiding database overhead and migrations.
* **Configurable Path:** ⚙️ You can specify the exact location of your `robots.txt` file in your `settings.py` for full control.
* **Dynamic Serving:** 🌐 Includes a view that serves the `robots.txt` file dynamically, ensuring that any changes made in the admin are live immediately.
* **Easy Integration:** 🔌 Designed to be a plug-and-play addition to any Django project.

## 🛠️ Installation & Setup

### 1. Installation

Install the package from PyPI:

```bash
pip install django-cs-robots
```

### 2. `settings.py` Configuration

Add the app to your INSTALLED_APPS in settings.py. For the admin index page link to appear, place 'cs_robots' before 'django.contrib.admin'.

```python
# settings.py
import os

INSTALLED_APPS = [
    'cs_robots', # 👈 Place before admin
    'django.contrib.admin',
    # ... other apps
]

# Define the absolute path to your robots.txt file
# (e.g., inside your project's static directory)
ROBOTS_TXT_PATH = os.path.join(BASE_DIR, 'static', 'robots.txt')
```

### 3. URL Configuration

Add the cs_robots paths to your project's urls.py.

```python
# your_project/urls.py
from django.contrib import admin
from django.urls import path, include
from cs_robots.views import serve_robots_txt # 👈 Import the serving view

urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Add the URL for the admin editor
    path('admin/tools/', include('cs_robots.urls')),

    # 2. Add the URL to serve the robots.txt file publicly
    path('robots.txt', serve_robots_txt, name='robots_txt'),

    # ... other project urls
]
```

## 💖 Contributions

Bug reports and feature requests are welcome!