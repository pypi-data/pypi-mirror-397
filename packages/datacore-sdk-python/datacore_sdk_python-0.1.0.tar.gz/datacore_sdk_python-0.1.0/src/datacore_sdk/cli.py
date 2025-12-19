from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Iterable, List, Optional
import uuid

from . import DataCoreClient
from .types import DatacoreProject, FilterParam, TypeOfParamEnum
from .exceptions import APIError


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _print(obj: Any) -> None:
    def _default(o: Any):
        if isinstance(o, DatacoreProject):
            return o.to_dict()
        return str(o)

    print(json.dumps(obj, default=_default, indent=2))


def _parse_bool(value: str) -> Optional[bool]:
    """Parse a tri-state boolean from string.

    Accepts: true/false/1/0/yes/no/on/off (case-insensitive).
    Returns True/False. Raises argparse.ArgumentTypeError on invalid value.
    """
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in {"true", "1", "yes", "y", "on"}:
        return True
    if s in {"false", "0", "no", "n", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")


def _build_client(args: argparse.Namespace) -> DataCoreClient:
    base_url = args.base_url or os.getenv("DATACORE_BASE_URL")
    api_key = args.api_key or os.getenv("DATACORE_API_KEY")
    bearer_token = args.bearer or os.getenv("DATACORE_BEARER_TOKEN")
    if not base_url:
        print("Missing base URL. Provide --base-url or set DATACORE_BASE_URL.", file=sys.stderr)
        sys.exit(2)
    # Validate auth inputs: exactly one of api_key or bearer_token must be provided
    if (api_key and bearer_token) or (not api_key and not bearer_token):
        print(
            "Provide exactly one credential: --api-key/DATACORE_API_KEY or --bearer/DATACORE_BEARER_TOKEN",
            file=sys.stderr,
        )
        sys.exit(2)
    return DataCoreClient(base_url=base_url, api_key=api_key, bearer_token=bearer_token, timeout=args.timeout)


def cmd_list(args: argparse.Namespace) -> int:
    client = _build_client(args)
    filters: Optional[List[FilterParam]] = None
    if args.filter:
        # Expect format key=value;type where type is optional int
        filters = []
        for f in args.filter:
            # examples: status=active, status=active;0
            part, *type_part = f.split(";")
            if "=" in part:
                key, value = part.split("=", 1)
            else:
                key, value = part, None
            type_val = None
            if type_part:
                try:
                    type_val = TypeOfParamEnum(int(type_part[0]))
                except Exception:
                    type_val = None
            filters.append(FilterParam(param=key, value=value, type=type_val))
    try:
        items = client.projects.list(filters=filters, page_number=args.page_number, page_size=args.page_size)
        _print([p.to_dict() for p in items])
        return 0
    except APIError as e:
        print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
        if e.details:
            _print(e.details)
        return 1


def cmd_create(args: argparse.Namespace) -> int:
    client = _build_client(args)
    dto: Optional[DatacoreProject] = None
    if args.json:
        data = _load_json(args.json)
        dto = DatacoreProject.from_dict(data)
        # Ensure an id is present; generate a new UUID if missing
        if not dto.id:
            dto.id = str(uuid.uuid4())
        try:
            created = client.projects.create(dto=dto)
        except APIError as e:
            print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
            if e.details:
                _print(e.details)
            return 1
        _print(created)
        return 0
    try:
        # Build DTO from inline flags (all properties supported)
        fields = [
            "createdBy",
            "createDate",
            "modifiedDate",
            "modifiedBy",
            "disabled",
            "id",
            "name",
            "description",
            "geoposition",
            "crs",
            "status",
            "message",
            "attributes",
            "active",
        ]
        payload: dict[str, Any] = {}
        for f in fields:
            val = getattr(args, f, None)
            if val is not None:
                payload[f] = val
        # Generate id if not provided
        if "id" not in payload or not payload.get("id"):
            payload["id"] = str(uuid.uuid4())
        dto = DatacoreProject.from_dict(payload) if payload else DatacoreProject()
        created = client.projects.create(dto=dto)
        _print(created)
        return 0
    except APIError as e:
        print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
        if e.details:
            _print(e.details)
        return 1


def cmd_update(args: argparse.Namespace) -> int:
    client = _build_client(args)
    if not args.json:
        print("--json is required for update (full DTO)", file=sys.stderr)
        return 2
    data = _load_json(args.json)
    dto = DatacoreProject.from_dict(data)
    try:
        updated = client.projects.update(dto=dto)
        _print(updated)
        return 0
    except APIError as e:
        print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
        if e.details:
            _print(e.details)
        return 1


def cmd_delete(args: argparse.Namespace) -> int:
    client = _build_client(args)
    if not args.ids:
        print("Provide at least one id with --ids", file=sys.stderr)
        return 2
    try:
        result = client.projects.delete_bulk(ids=args.ids)
        _print(result)
        return 0
    except APIError as e:
        print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
        if e.details:
            _print(e.details)
        return 1


def cmd_deactivate(args: argparse.Namespace) -> int:
    client = _build_client(args)
    if not args.ids:
        print("Provide at least one id with --ids", file=sys.stderr)
        return 2
    try:
        result = client.projects.deactivate_bulk(ids=args.ids)
        _print(result)
        return 0
    except APIError as e:
        print(f"API error: {e.status_code} {e.message}", file=sys.stderr)
        if e.details:
            _print(e.details)
        return 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="datacore-demo", description="CLI to exercise DataCore SDK (DatacoreProjects)")
    p.add_argument("--base-url", help="API base URL (or set DATACORE_BASE_URL)")
    p.add_argument("--api-key", help="API key (or set DATACORE_API_KEY)")
    p.add_argument(
        "--bearer",
        help="Bearer token (or set DATACORE_BEARER_TOKEN). Mutually exclusive with --api-key",
    )
    p.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds (default: 30)")

    sp = p.add_subparsers(dest="command", required=True)

    # list
    p_list = sp.add_parser("list", help="List Datacore projects")
    p_list.add_argument("--filter", action="append", help="Filter as key=value;type (type is optional int)")
    p_list.add_argument("--page-number", type=int, default=0)
    p_list.add_argument("--page-size", type=int, default=0)
    p_list.set_defaults(func=cmd_list)

    # create
    p_create = sp.add_parser("create", help="Create a Datacore project")
    # Full inline properties (use --json for full payload from file)
    p_create.add_argument("--created-by", dest="createdBy", help="Creator user")
    p_create.add_argument("--create-date", dest="createDate", help="Creation date (ISO 8601)")
    p_create.add_argument("--modified-date", dest="modifiedDate", help="Last modified date (ISO 8601)")
    p_create.add_argument("--modified-by", dest="modifiedBy", help="Last modifier user")
    p_create.add_argument("--disabled", dest="disabled", type=_parse_bool, help="Disabled flag (true/false)")
    p_create.add_argument("--id", dest="id", help="Project ID")
    p_create.add_argument("--name", dest="name", help="Project name")
    p_create.add_argument("--description", dest="description", help="Project description")
    p_create.add_argument("--geoposition", dest="geoposition", help="Geoposition")
    p_create.add_argument("--crs", dest="crs", help="CRS")
    p_create.add_argument("--status", dest="status", help="Status")
    p_create.add_argument("--message", dest="message", help="Message")
    p_create.add_argument("--attributes", dest="attributes", help="Attributes")
    p_create.add_argument("--active", dest="active", type=_parse_bool, help="Active flag (true/false)")
    p_create.add_argument("--json", help="Path to JSON file with full DatacoreProject DTO")
    p_create.set_defaults(func=cmd_create)

    # update
    p_update = sp.add_parser("update", help="Update a Datacore project (full DTO via --json)")
    p_update.add_argument("--json", required=True, help="Path to JSON file with full DatacoreProject DTO")
    p_update.set_defaults(func=cmd_update)

    # delete
    p_delete = sp.add_parser("delete", help="Delete projects in bulk")
    p_delete.add_argument("--ids", nargs="+", help="Project IDs to delete")
    p_delete.set_defaults(func=cmd_delete)

    # deactivate
    # p_deact = sp.add_parser("deactivate", help="Deactivate projects in bulk")
    # p_deact.add_argument("--ids", nargs="+", help="Project IDs to deactivate")
    # p_deact.set_defaults(func=cmd_deactivate)

    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
