# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Model execution types."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModelExecutionStatus(str, Enum):
    """Status of a model execution job."""
    
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class ModelExecutionRequest(BaseModel):
    """
    Request to execute a model.
    
    Used by clients to submit model execution jobs.
    """
    
    model_id: UUID = Field(..., description="Model to execute")
    
    # Input data
    data: dict[str, Any] = Field(
        ...,
        description="Input data for the model"
    )
    parameters: Optional[dict[str, Any]] = Field(
        default=None,
        description="Model parameters/hyperparameters"
    )
    
    # Execution options
    async_execution: bool = Field(
        default=False,
        description="Run asynchronously (returns job ID)"
    )
    timeout_seconds: int = Field(
        default=300,
        description="Maximum execution time"
    )
    
    # Data source (optional - for connector integration)
    connector_id: Optional[str] = Field(
        default=None,
        description="Data connector to use for input"
    )
    connector_query: Optional[dict[str, Any]] = Field(
        default=None,
        description="Query for the data connector"
    )
    
    # Metadata
    request_id: Optional[UUID] = Field(
        default=None,
        description="Client-provided request ID for tracking"
    )
    callback_url: Optional[str] = Field(
        default=None,
        description="Webhook URL for async completion"
    )


class ForecastResult(BaseModel):
    """
    Forecast/prediction result from a model.
    
    Standard output format for time series and forecasting models.
    """
    
    # Predictions
    point_forecast: list[float] = Field(
        ...,
        description="Point predictions"
    )
    lower_bound: Optional[list[float]] = Field(
        default=None,
        description="Lower confidence interval"
    )
    upper_bound: Optional[list[float]] = Field(
        default=None,
        description="Upper confidence interval"
    )
    confidence_level: float = Field(
        default=0.95,
        description="Confidence level for intervals"
    )
    
    # Metadata
    horizon: int = Field(..., description="Forecast horizon")
    timestamps: Optional[list[str]] = Field(
        default=None,
        description="Timestamps for predictions"
    )
    
    # Model diagnostics
    residuals: Optional[list[float]] = Field(
        default=None,
        description="In-sample residuals"
    )
    fitted_values: Optional[list[float]] = Field(
        default=None,
        description="In-sample fitted values"
    )


class ModelExecutionResult(BaseModel):
    """
    Result of a model execution.
    
    Returned by the backend after model execution completes.
    """
    
    # Identity
    execution_id: UUID = Field(..., description="Unique execution ID")
    model_id: UUID = Field(..., description="Model that was executed")
    request_id: Optional[UUID] = Field(
        default=None,
        description="Client-provided request ID"
    )
    
    # Status
    status: ModelExecutionStatus = Field(..., description="Execution status")
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(
        default=None,
        description="When execution started"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="When execution completed"
    )
    duration_ms: Optional[int] = Field(
        default=None,
        description="Execution duration in milliseconds"
    )
    
    # Results
    result: Optional[dict[str, Any]] = Field(
        default=None,
        description="Model output (format varies by model)"
    )
    forecast: Optional[ForecastResult] = Field(
        default=None,
        description="Forecast result (for time series models)"
    )
    
    # Errors
    error_code: Optional[str] = Field(
        default=None,
        description="Error code if failed"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    error_details: Optional[dict[str, Any]] = Field(
        default=None,
        description="Additional error context"
    )
    
    # Resource usage
    tcu_consumed: int = Field(
        default=0,
        description="TCU consumed by this execution"
    )
    memory_mb: Optional[int] = Field(
        default=None,
        description="Peak memory usage"
    )
    
    # Interpretation (AI-generated)
    interpretation: Optional[str] = Field(
        default=None,
        description="AI-generated result interpretation"
    )
    recommendations: Optional[list[str]] = Field(
        default=None,
        description="Follow-up recommendations"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
