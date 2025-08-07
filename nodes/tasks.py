"""Tasks for the nodes app."""

import requests
from celery import shared_task
from django.conf import settings


@shared_task(bind=True)
def simple_find_path_task(self, from_node_name: str, to_node_name: str):
    """Simple Celery task that calls the find_path API and returns the path."""
    try:
        base_url = getattr(settings, "INTERNAL_API_BASE_URL", "http://django:8000")
        api_url = f"{base_url}/api/nodes/path/find/"

        response = requests.post(
            api_url,
            json={"from_node": from_node_name, "to_node": to_node_name},
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "path": result.get("path"),
                "from_node": from_node_name,
                "to_node": to_node_name,
                "status": "SUCCESS",
            }
        else:
            return {
                "path": None,
                "from_node": from_node_name,
                "to_node": to_node_name,
                "status": "ERROR",
                "error": f"API call failed with status {response.status_code}",
            }
    except Exception as e:
        return {
            "path": None,
            "from_node": from_node_name,
            "to_node": to_node_name,
            "status": "ERROR",
            "error": str(e),
        }
