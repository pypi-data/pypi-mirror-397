# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Shared Type Definitions

Canonical type definitions used across the KRL Analytics Platform.
This package ensures type consistency between client SDK and server API.

Usage:
    from krl_types.billing import Tier, Money, UsageRecord
    from krl_types.auth import User, Session, APIKey
    from krl_types.models import ModelMetadata, ModelExecutionRequest
    from krl_types.connectors import ConnectorMetadata, ConnectorRequest
"""

__version__ = "0.2.0"

# Re-export commonly used types at package root
from krl_types.billing import (
    # Enums
    Tier,
    CustomerSegment,
    ContractType,
    ContractStatus,
    PaymentTerms,
    CreditType,
    UsageMetricType,
    HealthCategory,
    ChurnRisk,
    PricingStrategy,
    ValueDriver,
    # Currency
    Currency,
    Money,
    # Models
    UsageRecord,
    TierPricing,
    BillingPeriod,
)

from krl_types.auth import (
    # Models
    User,
    Session,
    APIKey,
    LicenseValidation,
    Permission,
    UserTier,
    # Enums
    AuthProvider,
    TokenType,
    PermissionScope,
)

from krl_types.models import (
    # Metadata
    ModelMetadata,
    ModelCategory,
    ModelTier,
    ModelStatus,
    ModelLicense,
    # Execution
    ModelExecutionRequest,
    ModelExecutionResult,
    ModelExecutionStatus,
    ForecastResult,
)

from krl_types.connectors import (
    # Metadata
    ConnectorMetadata,
    ConnectorCategory,
    ConnectorTier,
    ConnectorStatus,
    RateLimitConfig,
    # Operations
    ConnectorRequest,
    ConnectorResult,
    ConnectorField,
    ConnectorSchema,
    ConnectorFieldType,
    ConnectorResultStatus,
)

__all__ = [
    # Version
    "__version__",
    # Billing Enums
    "Tier",
    "CustomerSegment",
    "ContractType",
    "ContractStatus",
    "PaymentTerms",
    "CreditType",
    "UsageMetricType",
    "HealthCategory",
    "ChurnRisk",
    "PricingStrategy",
    "ValueDriver",
    # Currency
    "Currency",
    "Money",
    # Billing Models
    "UsageRecord",
    "TierPricing",
    "BillingPeriod",
    # Auth Enums
    "AuthProvider",
    "TokenType",
    "PermissionScope",
    # Auth Models
    "User",
    "Session",
    "APIKey",
    "LicenseValidation",
    "Permission",
    "UserTier",
    # Model Enums
    "ModelCategory",
    "ModelTier",
    "ModelStatus",
    "ModelLicense",
    "ModelExecutionStatus",
    # Model Types
    "ModelMetadata",
    "ModelExecutionRequest",
    "ModelExecutionResult",
    "ForecastResult",
    # Connector Enums
    "ConnectorCategory",
    "ConnectorTier",
    "ConnectorStatus",
    "ConnectorFieldType",
    "ConnectorResultStatus",
    # Connector Types
    "ConnectorMetadata",
    "RateLimitConfig",
    "ConnectorRequest",
    "ConnectorResult",
    "ConnectorField",
    "ConnectorSchema",
]
