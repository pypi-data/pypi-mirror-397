# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Connector Domain Types

Canonical type definitions for data connectors across the KRL Analytics Platform.

Usage:
    from krl_types.connectors import ConnectorMetadata, ConnectorCategory, ConnectorTier
    from krl_types.connectors import ConnectorRequest, ConnectorResult
"""

from krl_types.connectors.metadata import (
    ConnectorMetadata,
    ConnectorCategory,
    ConnectorTier,
    ConnectorStatus,
    RateLimitConfig,
)
from krl_types.connectors.operations import (
    ConnectorRequest,
    ConnectorResult,
    ConnectorResultStatus,
    ConnectorField,
    ConnectorFieldType,
    ConnectorSchema,
)

__all__ = [
    # Metadata
    "ConnectorMetadata",
    "ConnectorCategory",
    "ConnectorTier",
    "ConnectorStatus",
    "RateLimitConfig",
    # Operations
    "ConnectorRequest",
    "ConnectorResult",
    "ConnectorResultStatus",
    "ConnectorField",
    "ConnectorFieldType",
    "ConnectorSchema",
]
