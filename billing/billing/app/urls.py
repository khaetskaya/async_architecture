from django.contrib import admin
from django.urls import include, path

from authentication.views import (AuthCallbackView, AuthLoginView,
                                  AuthLogoutView, AuthRedirectView)
from billing.views import UserInfoView, DailyStatsView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/login_redirect", AuthLoginView.as_view(), name="login_redirect"),
    path("api/callback", AuthCallbackView.as_view(), name="callback"),
    path("api/redirect", AuthRedirectView.as_view(), name="redirect"),
    path("api/logout", AuthLogoutView.as_view(), name="logout"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("user_info/", UserInfoView.as_view(), name="user-info"),
    path("daily_stats/", DailyStatsView.as_view(), name="dailystats-view"),

]