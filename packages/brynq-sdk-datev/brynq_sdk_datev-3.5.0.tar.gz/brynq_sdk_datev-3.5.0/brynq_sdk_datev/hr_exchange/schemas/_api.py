# API models for HR Exchange
# This file contains API-related models like Job, Error, Resource, RestHook, etc.

from pydantic import BaseModel, ConfigDict, Field
from typing import Annotated, List
from datetime import datetime
from uuid import UUID
from ._enums import Severity, ResourceType, InnermostResourceType


class AdditionalError(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: str
    severity: Severity
    description: str | None = None
    help_uri: str | None = None
    path: str | None = None
    affected_fields: List[str] | None = None


class Error(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    error: str
    error_description: str | None = None
    error_uri: str | None = None
    request_id: str | None = None
    additional_messages: List[AdditionalError] | None = None


class ErrorMessage5xx(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    error_description: str | None = None
    request_id: str | None = None


class Job(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    id: UUID | None = None
    state: str
    time_stamp: datetime | None = None
    time_stamp_updated: datetime | None = None
    errors: List[Error] | None = None
    notify_url: str | None = None
    notify_authorization_header: Annotated[
        str | None, Field(max_length=100, min_length=0)
    ] = None


class ExchangeObject(BaseModel):
    pass
    model_config = ConfigDict(
        extra='allow',
    )


class JobResult(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    httpStatus: str | None = None  # HttpStatus | None = None  # Will reference enum later
    errors: List[Error] | None = None
    exchangeObjects: List[ExchangeObject] | None = None

    def __init__(self, **data):
        super().__init__(**data)
        # Find the resource list in the response data
        for key, value in data.items():
            if key != "errors" and isinstance(value, list) and value:
                self.exchangeObjects = value
                break


class Resource(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    path: str | None = None
    resourceType: ResourceType | None = None
    innermostResourceType: InnermostResourceType | None = None
    innermostReferenceDate: str | None = None
    innerResourceName: str | None = None
    resource_name: str | None = None
    id: str | None = None
    reference_date: str | None = None
    sub_resource: "Resource | None" = None  # Self-reference


class RestHookResourceInfo(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    resource: str | None = None
    resource_id: str | None = None
    server_url: str | None = None
    http_method: str | None = None
    additional_info: str | None = None


class RestHook(BaseModel):
    model_config = ConfigDict(
        extra='allow',
    )
    client_url: str
    authorization_header: Annotated[str | None, Field(max_length=100, min_length=0)] = (
        None
    )
    time_stamp: str | None = None
    event_resource: RestHookResourceInfo | None = None


# Rebuild models to resolve forward references
Resource.model_rebuild()
