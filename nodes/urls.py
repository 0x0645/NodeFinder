"""URLs for the nodes app."""

from django.urls import path

from .api.views import (
    AsyncFindPathView,
    AsyncPathResultView,
    ConnectNodesView,
    CreateNodeView,
    FindPathView,
    ListNodesView,
)

app_name = "nodes"

urlpatterns = [
    # Node management
    path("nodes/create/", CreateNodeView.as_view(), name="create_node"),
    path("nodes/connect/", ConnectNodesView.as_view(), name="connect_nodes"),
    path("nodes/list/", ListNodesView.as_view(), name="list_nodes"),
    # Synchronous path finding
    path("path/find/", FindPathView.as_view(), name="find_path"),
    # Simple async path finding
    path("path/async/", AsyncFindPathView.as_view(), name="async_find_path"),
    path(
        "path/async/result/",
        AsyncPathResultView.as_view(),
        name="get_async_path_result",
    ),
]
