# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["NotificationGetSchemasResponse"]


class NotificationGetSchemasResponse(BaseModel):
    """Response containing JSON schemas for all WebSocket message types."""

    auth_result_message: Dict[str, object] = FieldInfo(alias="AuthResultMessage")

    connection_closed_message: Dict[str, object] = FieldInfo(alias="ConnectionClosedMessage")

    contact_accepted_message: Dict[str, object] = FieldInfo(alias="ContactAcceptedMessage")

    notification_message: Dict[str, object] = FieldInfo(alias="NotificationMessage")

    pong_message: Dict[str, object] = FieldInfo(alias="PongMessage")

    task_update_message: Dict[str, object] = FieldInfo(alias="TaskUpdateMessage")

    workspace_share_message: Dict[str, object] = FieldInfo(alias="WorkspaceShareMessage")
