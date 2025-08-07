"""
Serializers for nodes API.
"""

from rest_framework import serializers

from .models import Connection
from .models import Node


class NodeSerializer(serializers.ModelSerializer):
    """Serializer for Node model."""

    class Meta:
        model = Node
        fields = ["id", "name", "created_at"]


class CreateNodeSerializer(serializers.ModelSerializer):
    """Serializer for creating a new node."""

    class Meta:
        model = Node
        fields = ["name"]

    def validate_name(self, value):
        """Validate that node name is unique."""
        if Node.objects.filter(name=value).exists():
            msg = "A node with this name already exists."
            raise serializers.ValidationError(msg)
        return value


class ConnectNodesSerializer(serializers.ModelSerializer):
    """Serializer for connecting two nodes."""

    from_node = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all(),
    )
    to_node = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all(),
    )

    class Meta:
        model = Connection
        fields = ["from_node", "to_node"]

    def validate(self, data):
        """Validate the connection."""
        from_node = data.get("from_node")
        to_node = data.get("to_node")

        if from_node == to_node:
            msg = "Cannot connect a node to itself."
            raise serializers.ValidationError(msg)

        # Check if connection already exists
        if Connection.objects.filter(from_node=from_node, to_node=to_node).exists():
            msg = "Connection already exists between these nodes."
            raise serializers.ValidationError(
                msg,
            )

        return data


class FindPathSerializer(serializers.Serializer):
    """Serializer for path finding requests."""

    from_node = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all(),
        help_text="Name of the starting node",
    )
    to_node = serializers.SlugRelatedField(
        slug_field="name",
        queryset=Node.objects.all(),
        help_text="Name of the destination node",
    )

    def validate(self, data):
        """Validate the path finding request."""
        from_node = data.get("from_node")
        to_node = data.get("to_node")

        if from_node == to_node:
            msg = "Source and destination nodes cannot be the same."
            raise serializers.ValidationError(
                msg,
            )

        return data


class TaskResultSerializer(serializers.Serializer):
    """Serializer for task result requests."""

    task_id = serializers.CharField(max_length=255, help_text="UUID of the Celery task")

    def validate_task_id(self, value):
        """Validate that task_id is not empty."""
        if not value or not value.strip():
            msg = "Task ID cannot be empty."
            raise serializers.ValidationError(msg)
        return value.strip()
