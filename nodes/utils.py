"""Utils for the nodes app."""

from collections import deque

from .models import Connection
from .models import Node


def find_path(from_node: Node, to_node: Node) -> list[str] | None:
    """
    Find shortest path between two nodes using BFS.
    Returns list of node names or None if no path exists.
    """
    if from_node == to_node:
        return [from_node.name]

    # BFS to find shortest path
    queue = deque([(from_node, [from_node.name])])
    visited = {from_node.id}

    while queue:
        current_node, path = queue.popleft()

        # Get all connected nodes
        connections = Connection.objects.filter(from_node=current_node).select_related(
            "to_node",
        )

        for connection in connections:
            next_node = connection.to_node

            if next_node.id == to_node.id:
                return [*path, next_node.name]

            if next_node.id not in visited:
                visited.add(next_node.id)
                queue.append((next_node, [*path, next_node.name]))

    return None


def find_path_by_names(from_node_name: str, to_node_name: str) -> list[str] | None:
    """Find path between nodes by their names."""
    try:
        from_node = Node.objects.get(name=from_node_name)
        to_node = Node.objects.get(name=to_node_name)
        return find_path(from_node, to_node)
    except Node.DoesNotExist:
        return None
