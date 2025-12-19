from __future__ import annotations

from typing import Any, Iterable, List, Mapping, Optional

from ..http import HttpClient
from ..types import DatacoreProject, FilterParam


class ProjectsClient:
    """Client for DatacoreProjects API endpoints.

    Implements operations based on the provided OpenAPI:
    - GET  /api/tff/v1/DatacoreProjects
    - POST /api/tff/v1/DatacoreProjects
    - PUT  /api/tff/v1/DatacoreProjects
    - DELETE /api/tff/v1/DatacoreProjects (bulk by IDs in body)
    - POST /api/tff/v1/DatacoreProjects/deactivate (bulk)
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def create(
        self,
        *,
        dto: Optional[DatacoreProject] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **extra: Any,
    ) -> DatacoreProject:
        """Create a Datacore project.

        You can pass a full `dto` or provide common fields like `name`/`description`.
        Additional keyword arguments are forwarded into the JSON payload.
        """
        payload: Mapping[str, Any]
        if dto is not None:
            payload = dto.to_dict()
        else:
            body: dict[str, Any] = {"name": name, "description": description}
            body.update(extra)
            payload = body
        data = self._http.post("/api/tff/v1/DatacoreProjects", json=payload)
        if isinstance(data, dict):
            return DatacoreProject.from_dict(data)
        return DatacoreProject()

    def update(self, *, dto: DatacoreProject) -> DatacoreProject:
        """Update an existing Datacore project.

        The API expects the full DTO in the request body.
        """
        data = self._http.put("/api/tff/v1/DatacoreProjects", json=dto.to_dict())
        if isinstance(data, dict):
            return DatacoreProject.from_dict(data)
        return DatacoreProject()

    def list(
        self,
        *,
        filters: Optional[List[FilterParam]] = None,
        page_number: int | None = 1,
        page_size: int | None = 10,
    ) -> List[DatacoreProject]:
        params: dict[str, Any] = {}
        if filters:
            params["filter"] = [f.to_dict() for f in filters]
        if page_number is not None:
            params["pageNumber"] = page_number
        if page_size is not None:
            params["pageSize"] = page_size
        data = self._http.get("/api/tff/v1/DatacoreProjects", params=params)
        print(data)
        # if isinstance(data, list):
        #     return [DatacoreProject.from_dict(item) for item in data]
        # items: Iterable[Any] = data.get("items", []) if isinstance(data, dict) else []
        # return [DatacoreProject.from_dict(item) for item in items]
        items: Iterable[Any] = (
            data.get("data", data.get("items", []))
            if isinstance(data, dict)
            else []
        )
        return [DatacoreProject.from_dict(item) for item in items]

    def delete_bulk(self, *, ids: List[str]) -> Any:
        """Delete multiple Datacore projects by IDs.

        Returns the raw API response body.
        """
        return self._http.delete("/api/tff/v1/DatacoreProjects", json=ids)

    def deactivate_bulk(self, *, ids: List[str]) -> Any:
        """Deactivate multiple Datacore projects by IDs.

        Returns the raw API response body.
        """
        return self._http.post("/api/tff/v1/DatacoreProjects/deactivate", json=ids)
