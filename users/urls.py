from django.urls import path
from .views import dashboard, assign_role, deactivate_user

urlpatterns = []

try:
    from django.urls import include
    from rest_framework.routers import DefaultRouter
    from .views import UserViewSet

    router = DefaultRouter()
    router.register(r"users", UserViewSet)

    urlpatterns += [
        path("api/", include(router.urls)),
    ]
except Exception:
    # DRF not available in this environment
    pass

urlpatterns += [
    path("dashboard/", dashboard, name="dashboard"),
    path("assign_role/<int:user_id>/", assign_role, name="assign_role"),
    path("deactivate_user/<int:user_id>/", deactivate_user, name="deactivate_user"),
]
