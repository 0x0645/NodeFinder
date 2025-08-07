"""Models for the nodes app."""

from django.db import models


class Node(models.Model):
    """A node in the graph."""

    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Connection(models.Model):
    """A connection between two nodes."""

    from_node = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="outgoing_connections"
    )
    to_node = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="incoming_connections"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["from_node", "to_node"]
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.from_node.name} -> {self.to_node.name}"
