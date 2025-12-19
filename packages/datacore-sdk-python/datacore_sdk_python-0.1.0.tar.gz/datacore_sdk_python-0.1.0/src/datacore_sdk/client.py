from __future__ import annotations

from typing import Optional

from .endpoints.projects import ProjectsClient
from .http import AuthConfig, HttpClient


class DataCoreClient:
    """Top-level SDK client composing endpoint sub-clients.

    Parameters:
        base_url: API base URL (e.g., https://api.datacore.example.com)
        api_key: API key to be sent as 'x-api-key' header (mutually exclusive with bearer_token)
        bearer_token: Bearer token to be sent as 'Authorization: Bearer <token>' (mutually exclusive with api_key)
        timeout: default request timeout in seconds
    """

    def __init__(
        self,
        *,
        base_url: str,
        api_key: Optional[str] = None,
        bearer_token: Optional[str] = None,
        timeout: float | None = 30.0,
    ):
        self._http = HttpClient(
            base_url=base_url,
            auth=AuthConfig(api_key=api_key, bearer_token=bearer_token),
            timeout=timeout,
        )

        # Sub-clients
        self.projects = ProjectsClient(self._http)

    # Example of a high-level orchestration method that performs multiple API calls
    def create_dune_project(self, *, name: str, description: Optional[str] = None) -> dict:
        """Create a Dune project.

        Placeholder flow:
        - Create a project
        - Potentially set defaults or trigger background tasks (pseudo-steps)

        Returns a simple dict summary for now. Adapt to your domain.
        """
        project = self.projects.create(name=name, description=description)

        # Placeholder for additional steps, e.g. initializing resources, permissions, etc.
        # self.some_client.configure(project.id, ...)

        return {
            "project_id": project.id,
            "name": project.name,
            "description": project.description,
            "status": "created",
        }
