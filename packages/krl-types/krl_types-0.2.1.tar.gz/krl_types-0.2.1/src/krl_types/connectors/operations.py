# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Connector operation types for runtime execution."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConnectorFieldType(str, Enum):
    """Field data types supported by connectors."""
    
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    ARRAY = "array"
    OBJECT = "object"
    UUID = "uuid"
    URL = "url"


class ConnectorField(BaseModel):
    """Schema field definition for connector data."""
    
    name: str = Field(..., description="Field name")
    field_type: ConnectorFieldType = Field(..., description="Data type")
    description: Optional[str] = Field(default=None, description="Field description")
    required: bool = Field(default=False, description="Is field required")
    nullable: bool = Field(default=True, description="Can field be null")
    default: Optional[Any] = Field(default=None, description="Default value")
    example: Optional[Any] = Field(default=None, description="Example value")


class ConnectorSchema(BaseModel):
    """Schema definition for connector input/output."""
    
    name: str = Field(..., description="Schema name")
    description: Optional[str] = Field(default=None, description="Schema description")
    fields: list[ConnectorField] = Field(
        default_factory=list,
        description="Schema fields"
    )
    version: str = Field(default="1.0.0", description="Schema version")


class ConnectorRequest(BaseModel):
    """
    Request payload for connector operations.
    
    This is the canonical type for ALL connector API calls.
    """
    
    # Request identity
    request_id: UUID = Field(
        default_factory=uuid4,
        description="Unique request identifier"
    )
    
    # Target connector
    connector_slug: str = Field(..., description="Target connector slug")
    
    # Operation
    operation: str = Field(
        default="query",
        description="Operation type (query, list, describe, etc.)"
    )
    
    # Query parameters
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Operation parameters"
    )
    
    # Pagination
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=100, ge=1, le=1000, description="Results per page")
    
    # Filtering
    filters: dict[str, Any] = Field(
        default_factory=dict,
        description="Filter conditions"
    )
    
    # Date range (common for time-series data)
    start_date: Optional[str] = Field(
        default=None,
        description="Start date (YYYY-MM-DD)"
    )
    end_date: Optional[str] = Field(
        default=None,
        description="End date (YYYY-MM-DD)"
    )
    
    # Output options
    format: str = Field(
        default="json",
        description="Response format (json, csv, parquet)"
    )
    include_metadata: bool = Field(
        default=True,
        description="Include connector metadata in response"
    )
    
    # Authentication context (populated by backend)
    user_id: Optional[UUID] = Field(
        default=None,
        description="Requesting user ID"
    )
    api_key_id: Optional[UUID] = Field(
        default=None,
        description="API key used for request"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConnectorResultStatus(str, Enum):
    """Status of connector operation result."""
    
    SUCCESS = "success"
    PARTIAL = "partial"       # Some data returned, but with warnings
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    TIMEOUT = "timeout"


class ConnectorResult(BaseModel):
    """
    Result payload from connector operations.
    
    This is the canonical type for ALL connector API responses.
    """
    
    # Request reference
    request_id: UUID = Field(..., description="Original request ID")
    connector_slug: str = Field(..., description="Connector that processed request")
    
    # Status
    status: ConnectorResultStatus = Field(..., description="Operation status")
    
    # Data payload
    data: Optional[list[dict[str, Any]]] = Field(
        default=None,
        description="Result data rows"
    )
    
    # Pagination info
    total_count: Optional[int] = Field(
        default=None,
        description="Total available records"
    )
    page: int = Field(default=1, description="Current page")
    page_size: int = Field(default=100, description="Results per page")
    has_more: bool = Field(default=False, description="More results available")
    
    # Schema (if requested)
    result_schema: Optional[ConnectorSchema] = Field(
        default=None,
        description="Data schema",
        alias="schema"
    )
    
    # Error handling
    error_code: Optional[str] = Field(
        default=None,
        description="Error code if status is error"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Human-readable error message"
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of error messages"
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of warning messages"
    )
    
    # Performance metrics
    execution_time_ms: int = Field(
        default=0,
        description="Execution time in milliseconds"
    )
    cache_hit: bool = Field(
        default=False,
        description="Whether result was served from cache"
    )
    
    # Rate limit info
    rate_limit_remaining: Optional[int] = Field(
        default=None,
        description="Remaining requests in current window"
    )
    rate_limit_reset: Optional[datetime] = Field(
        default=None,
        description="When rate limit resets"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
