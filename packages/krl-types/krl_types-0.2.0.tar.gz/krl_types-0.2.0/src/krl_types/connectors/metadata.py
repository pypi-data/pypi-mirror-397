# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""Connector metadata types and enums."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class ConnectorCategory(str, Enum):
    """Data source categories for connectors."""
    
    # Economic/Financial
    ECONOMIC = "economic"
    FINANCIAL = "financial"
    MARKET = "market"
    
    # Government
    CENSUS = "census"
    FEDERAL = "federal"
    STATE_LOCAL = "state_local"
    
    # Social
    SOCIAL = "social"
    EDUCATION = "education"
    HEALTH = "health"
    LABOR = "labor"
    
    # Environment
    ENVIRONMENT = "environment"
    CLIMATE = "climate"
    ENERGY = "energy"
    
    # Research/Academic
    RESEARCH = "research"
    ACADEMIC = "academic"
    
    # Industry
    REAL_ESTATE = "real_estate"
    HOUSING = "housing"
    AGRICULTURE = "agriculture"
    TRANSPORTATION = "transportation"
    
    # International
    INTERNATIONAL = "international"
    DEVELOPMENT = "development"
    
    # Other
    UTILITY = "utility"
    CUSTOM = "custom"


class ConnectorTier(str, Enum):
    """Access tier for connectors (maps to billing tiers)."""
    
    COMMUNITY = "community"       # Free tier - 12 connectors
    PROFESSIONAL = "professional"  # Pro tier - 49 connectors
    ENTERPRISE = "enterprise"      # Enterprise tier - 76 connectors


class ConnectorStatus(str, Enum):
    """Connector availability status."""
    
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    MAINTENANCE = "maintenance"
    BETA = "beta"
    DISABLED = "disabled"


class RateLimitConfig(BaseModel):
    """Rate limiting configuration for a connector."""
    
    requests_per_minute: int = Field(
        default=60,
        description="Maximum requests per minute"
    )
    requests_per_day: int = Field(
        default=1000,
        description="Maximum requests per day"
    )
    burst_limit: int = Field(
        default=10,
        description="Maximum burst requests"
    )
    retry_after_seconds: int = Field(
        default=60,
        description="Recommended retry delay after rate limit"
    )


class ConnectorMetadata(BaseModel):
    """
    Canonical connector metadata for the KRL Analytics Platform.
    
    This is the SINGLE SOURCE OF TRUTH for connector metadata.
    All connector registries, backends, and frontends MUST use this type.
    
    Attributes:
        id: Unique connector identifier
        name: Human-readable connector name
        slug: URL-safe identifier (e.g., "fred-basic")
        version: Connector version
        
        category: Primary data category
        tier: Access tier (community/professional/enterprise)
        
        description: Brief description
        long_description: Detailed documentation (markdown)
        
        provider: Data provider name (e.g., "Federal Reserve")
        provider_url: Provider website
        documentation_url: Full documentation URL
        
        requires_api_key: Whether an API key is needed
        requires_license: Whether a KRL license is required
        
        rate_limit: Rate limiting configuration
        
        tags: Search/filter tags
        status: Availability status
        
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    # Identity
    id: UUID = Field(..., description="Unique connector identifier")
    name: str = Field(..., description="Human-readable name")
    slug: str = Field(..., description="URL-safe identifier")
    version: str = Field(default="1.0.0", description="Connector version")
    
    # Classification
    category: ConnectorCategory = Field(..., description="Data category")
    tier: ConnectorTier = Field(
        default=ConnectorTier.COMMUNITY,
        description="Required access tier"
    )
    
    # Documentation
    description: str = Field(..., description="Brief description")
    long_description: Optional[str] = Field(
        default=None,
        description="Detailed documentation (markdown)"
    )
    
    # Provider info
    provider: str = Field(..., description="Data provider name")
    provider_url: Optional[str] = Field(
        default=None,
        description="Provider website"
    )
    documentation_url: Optional[str] = Field(
        default=None,
        description="Full documentation URL"
    )
    
    # Access requirements
    requires_api_key: bool = Field(
        default=False,
        description="Whether an API key is needed"
    )
    api_key_url: Optional[str] = Field(
        default=None,
        description="URL to obtain API key"
    )
    requires_license: bool = Field(
        default=False,
        description="Whether a KRL license is required"
    )
    
    # Rate limiting
    rate_limit: RateLimitConfig = Field(
        default_factory=RateLimitConfig,
        description="Rate limiting configuration"
    )
    
    # Categorization
    tags: list[str] = Field(
        default_factory=list,
        description="Search/filter tags"
    )
    status: ConnectorStatus = Field(
        default=ConnectorStatus.ACTIVE,
        description="Availability status"
    )
    
    # Capabilities
    supports_streaming: bool = Field(
        default=False,
        description="Supports streaming responses"
    )
    supports_pagination: bool = Field(
        default=True,
        description="Supports paginated responses"
    )
    supports_schema_discovery: bool = Field(
        default=True,
        description="Supports schema introspection"
    )
    
    # Data characteristics
    data_refresh_frequency: Optional[str] = Field(
        default=None,
        description="How often source data updates (e.g., 'daily', 'monthly')"
    )
    historical_data_available: bool = Field(
        default=True,
        description="Whether historical data is available"
    )
    earliest_data_date: Optional[str] = Field(
        default=None,
        description="Earliest available data date"
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Usage statistics (read-only, populated by backend)
    usage_count: int = Field(
        default=0,
        description="Total API calls"
    )
    average_response_time_ms: Optional[int] = Field(
        default=None,
        description="Average response time"
    )

    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        }
