"""
API views for node management and path finding.
"""

from celery.result import AsyncResult
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Node
from ..pagination import NodePagination
from ..serializers import (
    ConnectNodesSerializer,
    CreateNodeSerializer,
    FindPathSerializer,
    NodeSerializer,
    TaskResultSerializer,
)
from ..tasks import simple_find_path_task
from ..utils import find_path_by_names


class CreateNodeView(APIView):
    """Create a new node."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=CreateNodeSerializer,
        responses={201: NodeSerializer, 400: None},
        description="Create a new node with a unique name",
        examples=[
            OpenApiExample(
                "Create Node Request",
                value={"name": "MyNode"},
                request_only=True,
            ),
            OpenApiExample(
                "Node Created Successfully",
                value={
                    "id": 1,
                    "name": "MyNode",
                    "created_at": "2025-08-07T16:35:00.124944Z",
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Validation Error",
                value={"name": ["This field is required."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        """Create a new node."""
        serializer = CreateNodeSerializer(data=request.data)
        if serializer.is_valid():
            node = serializer.save()
            return Response(NodeSerializer(node).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConnectNodesView(APIView):
    """Connect two nodes."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=ConnectNodesSerializer,
        responses={201: None, 400: None},
        description="Create a connection between two nodes",
        examples=[
            OpenApiExample(
                "Connect Nodes Request",
                value={"from_node": "NodeA", "to_node": "NodeB"},
                request_only=True,
            ),
            OpenApiExample(
                "Connection Created Successfully",
                value={"message": "Nodes connected successfully"},
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Node Not Found Error",
                value={"from_node": ["Node with name 'InvalidNode' does not exist."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        """Connect two nodes."""
        serializer = ConnectNodesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Nodes connected successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FindPathView(APIView):
    """Find path between two nodes synchronously."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=FindPathSerializer,
        responses={200: None, 400: None},
        description="Find path between two nodes (synchronous)",
        examples=[
            OpenApiExample(
                "Find Path Request",
                value={"from_node": "NodeA", "to_node": "NodeC"},
                request_only=True,
            ),
            OpenApiExample(
                "Path Found Successfully",
                value={
                    "path": ["NodeA", "NodeB", "NodeC"],
                    "from_node": "NodeA",
                    "to_node": "NodeC",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "No Path Available",
                value={"path": None, "from_node": "NodeA", "to_node": "IsolatedNode"},
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Node Not Found Error",
                value={"from_node": ["Node with name 'InvalidNode' does not exist."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        """Find path between two nodes synchronously."""
        serializer = FindPathSerializer(data=request.data)
        if serializer.is_valid():
            from_node_name = serializer.validated_data["from_node"].name
            to_node_name = serializer.validated_data["to_node"].name

            path = find_path_by_names(from_node_name, to_node_name)

            return Response(
                {"path": path, "from_node": from_node_name, "to_node": to_node_name}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListNodesView(ListAPIView):
    """List all nodes with pagination."""

    queryset = Node.objects.all().order_by("created_at")
    serializer_class = NodeSerializer
    permission_classes = [AllowAny]
    pagination_class = NodePagination


# Async path finding views
class AsyncFindPathView(APIView):
    """Start simple async path finding task."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=FindPathSerializer,
        responses={202: None, 400: None},
        description="Start simple async path finding task (5 second delay)",
        examples=[
            OpenApiExample(
                "Async Path Request",
                value={"from_node": "NodeA", "to_node": "NodeC"},
                request_only=True,
            ),
            OpenApiExample(
                "Task Started Successfully",
                value={
                    "task_id": "abc123-def456-ghi789",
                    "status": "PENDING",
                    "message": "simple_async path finding task started",
                    "algorithm": "simple_async",
                    "estimated_time": "5 seconds",
                },
                response_only=True,
                status_codes=["202"],
            ),
            OpenApiExample(
                "Node Not Found Error",
                value={"from_node": ["Node with name 'InvalidNode' does not exist."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        """Start an async path finding task."""
        serializer = FindPathSerializer(data=request.data)
        if serializer.is_valid():
            from_node_name = serializer.validated_data["from_node"].name
            to_node_name = serializer.validated_data["to_node"].name

            task = simple_find_path_task.apply_async(
                args=[from_node_name, to_node_name], countdown=5
            )

            return Response(
                {
                    "task_id": task.id,
                    "status": "PENDING",
                    "message": "simple_async path finding task started",
                    "algorithm": "simple_async",
                    "estimated_time": "5 seconds",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AsyncPathResultView(APIView):
    """Get result of simple async path finding task."""

    permission_classes = [AllowAny]

    @extend_schema(
        request=TaskResultSerializer,
        responses={200: None, 500: None, 400: None},
        description="Get the result of simple async path finding task",
        examples=[
            OpenApiExample(
                "Get Task Result Request",
                value={"task_id": "abc123-def456-ghi789"},
                request_only=True,
            ),
            OpenApiExample(
                "Task Completed Successfully",
                value={
                    "task_id": "abc123-def456-ghi789",
                    "status": "SUCCESS",
                    "result": {
                        "path": ["NodeA", "NodeB", "NodeC"],
                        "from_node": "NodeA",
                        "to_node": "NodeC",
                        "algorithm": "simple_async",
                    },
                    "algorithm": "simple_async",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Task Still Processing",
                value={
                    "task_id": "abc123-def456-ghi789",
                    "status": "PENDING",
                    "message": "simple_async task is still processing...",
                    "algorithm": "simple_async",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Task Failed",
                value={
                    "task_id": "abc123-def456-ghi789",
                    "status": "FAILURE",
                    "error": "Node not found",
                    "algorithm": "simple_async",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Invalid Task ID",
                value={"task_id": ["This field is required."]},
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        """Get the result of an async path finding task."""
        serializer = TaskResultSerializer(data=request.data)
        if serializer.is_valid():
            task_id = serializer.validated_data["task_id"]

            try:
                result = AsyncResult(task_id)

                if result.ready():
                    if result.successful():
                        return Response(
                            {
                                "task_id": task_id,
                                "status": "SUCCESS",
                                "result": result.result,
                                "algorithm": (
                                    result.result.get("algorithm", "simple_async")
                                    if result.result
                                    else "simple_async"
                                ),
                            }
                        )
                    else:
                        return Response(
                            {
                                "task_id": task_id,
                                "status": "FAILURE",
                                "error": str(result.result),
                                "algorithm": "simple_async",
                            }
                        )
                else:
                    return Response(
                        {
                            "task_id": task_id,
                            "status": "PENDING",
                            "message": "simple_async task is still processing...",
                            "algorithm": "simple_async",
                        }
                    )
            except Exception as e:
                return Response(
                    {
                        "task_id": task_id,
                        "status": "ERROR",
                        "error": str(e),
                        "algorithm": "simple_async",
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
