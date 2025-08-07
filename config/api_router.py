"""API router."""

from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter


router = DefaultRouter() if settings.DEBUG else SimpleRouter()

app_name = "api"
urlpatterns = router.urls + [
    path("nodes/", include("nodes.urls", namespace="nodes")),
]
