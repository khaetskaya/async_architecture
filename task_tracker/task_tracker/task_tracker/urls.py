"""
URL configuration for task_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from authentication.views import (AuthCallbackView, AuthLoginView,
                                  AuthLogoutView, AuthRedirectView)
from tasks.views import (CloseTaskView, CreateTaskView, MyTasksView,
                         ReassignTasksView, UserList)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login_redirect", AuthLoginView.as_view(), name="login_redirect"),
    path("api/callback", AuthCallbackView.as_view(), name="callback"),
    path("api/redirect", AuthRedirectView.as_view(), name="redirect"),
    path("api/logout", AuthLogoutView.as_view(), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("users/", UserList.as_view()),
    path("tasks/create/", CreateTaskView.as_view(), name="task-create"),
    path("tasks/view/", MyTasksView.as_view(), name="task-view"),
    path("tasks/reassign/", ReassignTasksView.as_view(), name="task-reassign"),
    path("tasks/close/", CloseTaskView.as_view(), name="task-close"),
]
