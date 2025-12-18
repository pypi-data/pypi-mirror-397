# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Model metadata types and enums."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ModelCategory(str, Enum):
    """Model categories in the KRL Model Zoo."""
    
    # Time Series
    TIME_SERIES = "time_series"
    FORECASTING = "forecasting"
    VOLATILITY = "volatility"
    
    # Econometrics
    ECONOMETRICS = "econometrics"
    CAUSAL_INFERENCE = "causal_inference"
    POLICY_ANALYSIS = "policy_analysis"
    
    # Machine Learning
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"
    
    # Spatial/Network
    GEOSPATIAL = "geospatial"
    NETWORK_ANALYSIS = "network_analysis"
    
    # Domain Specific
    HEALTH = "health"
    ENVIRONMENT = "environment"
    SOCIAL = "social"
    ECONOMIC = "economic"
    
    # NLP
    NLP = "nlp"
    TEXT_ANALYSIS = "text_analysis"
    
    # Other
    UTILITY = "utility"
    EXPERIMENTAL = "experimental"


class ModelTier(str, Enum):
    """Access tier for models (maps to billing tiers)."""
    
    COMMUNITY = "community"       # Free tier - 12 models
    PROFESSIONAL = "professional"  # Pro tier - 64 models
    ENTERPRISE = "enterprise"      # Enterprise tier - 126 models


class ModelStatus(str, Enum):
    """Model lifecycle status."""
    
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ModelLicense(str, Enum):
    """License types for models."""
    
    APACHE_2_0 = "Apache-2.0"
    MIT = "MIT"
    PROPRIETARY = "proprietary"
    RESEARCH_ONLY = "research_only"


class ModelMetadata(BaseModel):
    """
    Canonical model metadata for the KRL Analytics Platform.
    
    This is the SINGLE SOURCE OF TRUTH for model metadata.
    All model registries, backends, and frontends MUST use this type.
    
    Attributes:
        id: Unique model identifier
        name: Human-readable model name
        slug: URL-safe identifier (e.g., "arima-garch")
        version: Semantic version string
        category: Primary model category
        tier: Access tier (community/professional/enterprise)
        
        description: Brief model description
        long_description: Detailed documentation (markdown)
        
        author: Model author/organization
        created_at: Creation timestamp
        updated_at: Last update timestamp
        
        tags: Categorization tags for search/filter
        status: Lifecycle status
        license: License type
        
        input_schema: JSON Schema for model inputs
        output_schema: JSON Schema for model outputs
        parameters_schema: JSON Schema for model parameters
        
        tcu_cost: Compute cost in TCU (Technical Compute Units)
        estimated_runtime_ms: Typical execution time
        
        documentation_url: Link to full documentation
        source_url: Link to source code (if open source)
    """
    
    # Identity
    id: UUID = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Human-readable model name")
    slug: str = Field(..., description="URL-safe identifier")
    version: str = Field(default="1.0.0", description="Semantic version")
    
    # Classification
    category: ModelCategory = Field(..., description="Primary category")
    tier: ModelTier = Field(
        default=ModelTier.COMMUNITY,
        description="Required access tier"
    )
    
    # Documentation
    description: str = Field(..., description="Brief description")
    long_description: Optional[str] = Field(
        default=None,
        description="Detailed documentation (markdown)"
    )
    
    # Provenance
    author: str = Field(default="KR-Labs", description="Author/organization")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Categorization
    tags: list[str] = Field(
        default_factory=list,
        description="Search/filter tags"
    )
    status: ModelStatus = Field(
        default=ModelStatus.ACTIVE,
        description="Lifecycle status"
    )
    license: ModelLicense = Field(
        default=ModelLicense.APACHE_2_0,
        description="License type"
    )
    
    # Schemas (JSON Schema format)
    input_schema: Optional[dict] = Field(
        default=None,
        description="JSON Schema for inputs"
    )
    output_schema: Optional[dict] = Field(
        default=None,
        description="JSON Schema for outputs"
    )
    parameters_schema: Optional[dict] = Field(
        default=None,
        description="JSON Schema for parameters"
    )
    
    # Performance
    tcu_cost: int = Field(
        default=1,
        description="Compute cost in TCU"
    )
    estimated_runtime_ms: Optional[int] = Field(
        default=None,
        description="Typical execution time"
    )
    
    # Links
    documentation_url: Optional[str] = Field(
        default=None,
        description="Full documentation URL"
    )
    source_url: Optional[str] = Field(
        default=None,
        description="Source code URL"
    )
    
    # Usage statistics (read-only, populated by backend)
    execution_count: int = Field(
        default=0,
        description="Total executions"
    )
    average_rating: Optional[float] = Field(
        default=None,
        description="User rating (1-5)"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
