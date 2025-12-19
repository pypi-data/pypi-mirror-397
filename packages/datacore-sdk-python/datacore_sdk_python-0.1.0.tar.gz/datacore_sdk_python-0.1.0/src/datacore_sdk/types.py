from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Mapping, MutableMapping, Optional


@dataclass
class Project:
    id: str
    name: str
    description: str | None = None

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "Project":
        return Project(
            id=str(data.get("id") or data.get("project_id") or ""),
            name=str(data.get("name") or ""),
            description=data.get("description"),
        )


class TypeOfParamEnum(IntEnum):
    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_2 = 2
    VALUE_3 = 3
    VALUE_4 = 4
    VALUE_5 = 5
    VALUE_6 = 6
    VALUE_7 = 7
    VALUE_8 = 8
    VALUE_9 = 9
    VALUE_10 = 10
    VALUE_11 = 11
    VALUE_12 = 12
    VALUE_13 = 13
    VALUE_14 = 14
    VALUE_15 = 15
    VALUE_16 = 16
    VALUE_17 = 17
    VALUE_18 = 18
    VALUE_19 = 19


@dataclass
class FilterParam:
    param: Optional[str] = None
    value: Any = None
    type: Optional[TypeOfParamEnum] = None

    def to_dict(self) -> dict[str, Any]:
        data: MutableMapping[str, Any] = {}
        if self.param is not None:
            data["param"] = self.param
        if self.value is not None:
            data["value"] = self.value
        if self.type is not None:
            data["type"] = int(self.type)
        return dict(data)


@dataclass
class DatacoreProject:
    # Fields based on DatacoreProjectDTO
    createdBy: Optional[str] = None
    createDate: Optional[str] = None  # ISO date-time
    modifiedDate: Optional[str] = None  # ISO date-time
    modifiedBy: Optional[str] = None
    disabled: Optional[bool] = None
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    geoposition: Optional[str] = None
    crs: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    attributes: Optional[str] = None
    active: Optional[bool] = None

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> "DatacoreProject":
        return DatacoreProject(
            createdBy=data.get("createdBy"),
            createDate=data.get("createDate"),
            modifiedDate=data.get("modifiedDate"),
            modifiedBy=data.get("modifiedBy"),
            disabled=data.get("disabled"),
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description"),
            geoposition=data.get("geoposition"),
            crs=data.get("crs"),
            status=data.get("status"),
            message=data.get("message"),
            attributes=data.get("attributes"),
            active=data.get("active"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "createdBy": self.createdBy,
            "createDate": self.createDate,
            "modifiedDate": self.modifiedDate,
            "modifiedBy": self.modifiedBy,
            "disabled": self.disabled,
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "geoposition": self.geoposition,
            "crs": self.crs,
            "status": self.status,
            "message": self.message,
            "attributes": self.attributes,
            "active": self.active,
        }
