# ----------------------------------------------------------------------
# Copyright 2025 KR-Labs. All rights reserved.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
"""
KRL Types - Model Domain Types

Canonical type definitions for model metadata, categories, and execution
across the KRL Analytics Platform.

Usage:
    from krl_types.models import ModelMetadata, ModelCategory, ModelTier
    from krl_types.models import ModelExecutionRequest, ModelExecutionResult
"""

from krl_types.models.metadata import (
    ModelMetadata,
    ModelCategory,
    ModelTier,
    ModelStatus,
    ModelLicense,
)
from krl_types.models.execution import (
    ModelExecutionRequest,
    ModelExecutionResult,
    ModelExecutionStatus,
    ForecastResult,
)

__all__ = [
    # Metadata
    "ModelMetadata",
    "ModelCategory",
    "ModelTier",
    "ModelStatus",
    "ModelLicense",
    # Execution
    "ModelExecutionRequest",
    "ModelExecutionResult",
    "ModelExecutionStatus",
    "ForecastResult",
]
