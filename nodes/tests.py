"""Tests for nodes API."""

from unittest.mock import MagicMock
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Connection
from .models import Node
from .tasks import simple_find_path_task

# Test constants
TWO_NODES = 2
FIVE_NODES = 5
TEN_NODES = 10
TWENTY_NODES = 20
TWENTY_FIVE_NODES = 25


class NodeModelTest(TestCase):
    """Test the Node model."""

    def test_create_node(self):
        """Test creating a node."""
        node = Node.objects.create(name="TestNode")
        assert node.name == "TestNode"
        assert node.created_at

    def test_node_str_representation(self):
        """Test the string representation of a node."""
        node = Node.objects.create(name="TestNode")
        assert str(node) == "TestNode"


class ConnectionModelTest(TestCase):
    """Test the Connection model."""

    def setUp(self):
        """Set up test data."""
        self.node1 = Node.objects.create(name="Node1")
        self.node2 = Node.objects.create(name="Node2")

    def test_create_connection(self):
        """Test creating a connection."""
        connection = Connection.objects.create(from_node=self.node1, to_node=self.node2)
        assert connection.from_node == self.node1
        assert connection.to_node == self.node2
        assert connection.created_at

    def test_connection_str_representation(self):
        """Test the string representation of a connection."""
        connection = Connection.objects.create(from_node=self.node1, to_node=self.node2)
        assert str(connection) == "Node1 -> Node2"


class CreateNodeAPITest(APITestCase):
    """Test the create node API."""

    def setUp(self):
        """Set up the test environment."""
        self.url = reverse("api:nodes:create_node")

    def test_create_node_success(self):
        """Test successful node creation."""
        data = {"name": "TestNode"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "TestNode"
        assert Node.objects.filter(name="TestNode").exists()

    def test_create_node_duplicate_name(self):
        """Test creating a node with duplicate name."""
        Node.objects.create(name="ExistingNode")
        data = {"name": "ExistingNode"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_create_node_empty_name(self):
        """Test creating a node with empty name."""
        data = {"name": ""}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data


class ConnectNodesAPITest(APITestCase):
    """Test the connect nodes API."""

    def setUp(self):
        """Set up the test environment."""
        self.url = reverse("api:nodes:connect_nodes")
        self.node1 = Node.objects.create(name="Node1")
        self.node2 = Node.objects.create(name="Node2")

    def test_connect_nodes_success(self):
        """Test successful node connection."""
        data = {"from_node": "Node1", "to_node": "Node2"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Connection.objects.filter(
            from_node=self.node1,
            to_node=self.node2,
        ).exists()

    def test_connect_same_node(self):
        """Test connecting a node to itself."""
        data = {"from_node": "Node1", "to_node": "Node1"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_connect_nonexistent_node(self):
        """Test connecting nonexistent nodes."""
        data = {"from_node": "NonExistent", "to_node": "Node2"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_connect_duplicate_connection(self):
        """Test creating duplicate connection."""
        Connection.objects.create(from_node=self.node1, to_node=self.node2)
        data = {"from_node": "Node1", "to_node": "Node2"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class ListNodesAPITest(APITestCase):
    """Test the list nodes API."""

    def setUp(self):
        """Set up the test environment."""
        self.url = reverse("api:nodes:list_nodes")

    def test_list_empty_nodes(self):
        """Test listing when no nodes exist."""
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert len(response.data["results"]) == 0

    def test_list_nodes(self):
        """Test listing existing nodes."""
        Node.objects.create(name="Node1")
        Node.objects.create(name="Node2")
        response = self.client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == TWO_NODES
        assert len(response.data["results"]) == TWO_NODES
        names = [node["name"] for node in response.data["results"]]
        assert "Node1" in names
        assert "Node2" in names

    def test_list_nodes_pagination(self):
        """Test pagination with more than default page size."""
        for i in range(TWENTY_FIVE_NODES):
            Node.objects.create(name=f"Node{i:02d}")

        # Test first page
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == TWENTY_FIVE_NODES
        assert len(response.data["results"]) == TWENTY_NODES
        assert response.data["next"] is not None
        assert response.data["previous"] is None

        # Test second page
        response = self.client.get(self.url + "?page=2")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == TWENTY_FIVE_NODES
        assert len(response.data["results"]) == FIVE_NODES
        assert response.data["next"] is None
        assert response.data["previous"] is not None

    def test_list_nodes_custom_page_size(self):
        """Test custom page size parameter."""
        # Create 10 nodes
        for i in range(TEN_NODES):
            Node.objects.create(name=f"Node{i:02d}")

        # Request with page_size=5
        response = self.client.get(self.url + "?page_size=5")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == TEN_NODES
        assert len(response.data["results"]) == FIVE_NODES
        assert response.data["next"] is not None


class FindPathAPITest(APITestCase):
    """Test the synchronous find path API."""

    def setUp(self):
        """Set up the test environment."""
        self.url = reverse("api:nodes:find_path")

        # Create test nodes and connections
        self.node_a = Node.objects.create(name="NodeA")
        self.node_b = Node.objects.create(name="NodeB")
        self.node_c = Node.objects.create(name="NodeC")
        self.isolated_node = Node.objects.create(name="IsolatedNode")

        # Create connections: A -> B -> C (IsolatedNode has no connections)
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        Connection.objects.create(from_node=self.node_b, to_node=self.node_c)

    def test_find_path_success(self):
        """Test successful path finding."""
        data = {"from_node": "NodeA", "to_node": "NodeC"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["from_node"] == "NodeA"
        assert response.data["to_node"] == "NodeC"
        assert response.data["path"] == ["NodeA", "NodeB", "NodeC"]

    def test_find_path_no_path(self):
        """Test path finding when no path exists."""
        data = {"from_node": "NodeA", "to_node": "IsolatedNode"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["path"] is None

    def test_find_path_same_node(self):
        """Test path finding with same source and destination."""
        data = {"from_node": "NodeA", "to_node": "NodeA"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_find_path_invalid_node(self):
        """Test path finding with invalid node."""
        data = {"from_node": "NonExistent", "to_node": "NodeC"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class AsyncFindPathAPITest(APITestCase):
    """Test the async find path API endpoints."""

    def setUp(self):
        """Set up the test environment."""
        self.async_find_path_url = reverse("api:nodes:async_find_path")
        self.get_async_result_url = reverse("api:nodes:get_async_path_result")

        # Create test nodes and connections
        self.node_a = Node.objects.create(name="NodeA")
        self.node_b = Node.objects.create(name="NodeB")
        self.node_c = Node.objects.create(name="NodeC")

        # Create connections: A -> B -> C
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        Connection.objects.create(from_node=self.node_b, to_node=self.node_c)

    @patch("nodes.api.views.simple_find_path_task")
    def test_async_find_path_success(self, mock_task):
        """Test successful async path finding task creation."""
        # Mock the Celery task
        mock_task_result = MagicMock()
        mock_task_result.id = "async-task-id-123"
        mock_task.apply_async.return_value = mock_task_result

        data = {"from_node": "NodeA", "to_node": "NodeC"}
        response = self.client.post(self.async_find_path_url, data, format="json")

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.data["task_id"] == "async-task-id-123"
        assert response.data["status"] == "PENDING"
        assert response.data["algorithm"] == "simple_async"
        assert response.data["estimated_time"] == "5 seconds"
        mock_task.apply_async.assert_called_once_with(
            args=["NodeA", "NodeC"],
            countdown=5,
        )


class SimpleFindPathTaskTest(TestCase):
    """Test the simple_find_path_task directly."""

    def setUp(self):
        """Set up test data."""
        self.node_a = Node.objects.create(name="NodeA")
        self.node_b = Node.objects.create(name="NodeB")
        self.node_c = Node.objects.create(name="NodeC")
        self.isolated_node = Node.objects.create(name="IsolatedNode")

        # Create connections: A -> B -> C
        Connection.objects.create(from_node=self.node_a, to_node=self.node_b)
        Connection.objects.create(from_node=self.node_b, to_node=self.node_c)

    @patch("nodes.tasks.requests.post")
    def test_simple_find_path_task_success(self, mock_post):
        """Test successful simple path finding task."""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "path": ["NodeA", "NodeB", "NodeC"],
            "from_node": "NodeA",
            "to_node": "NodeC",
        }
        mock_post.return_value = mock_response

        result = simple_find_path_task("NodeA", "NodeC")

        assert result["status"] == "SUCCESS"
        assert result["from_node"] == "NodeA"
        assert result["to_node"] == "NodeC"
        assert result["path"] == ["NodeA", "NodeB", "NodeC"]
        mock_post.assert_called_once()

    @patch("nodes.tasks.requests.post")
    def test_simple_find_path_task_no_path(self, mock_post):
        """Test simple path finding task when no path exists."""
        # Mock API response with no path
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "path": None,
            "from_node": "NodeA",
            "to_node": "IsolatedNode",
        }
        mock_post.return_value = mock_response

        result = simple_find_path_task("NodeA", "IsolatedNode")

        assert result["status"] == "SUCCESS"
        assert result["from_node"] == "NodeA"
        assert result["to_node"] == "IsolatedNode"
        assert result["path"] is None
        mock_post.assert_called_once()

    @patch("nodes.tasks.requests.post")
    def test_simple_find_path_task_api_error(self, mock_post):
        """Test simple path finding task when API call fails."""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        result = simple_find_path_task("NodeA", "NodeC")

        assert result["status"] == "ERROR"
        assert result["from_node"] == "NodeA"
        assert result["to_node"] == "NodeC"
        assert result["path"] is None
        assert "API call failed" in result["error"]
        mock_post.assert_called_once()
