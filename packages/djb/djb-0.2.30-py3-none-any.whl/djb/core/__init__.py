"""
djb.core - Exception hierarchy.

Exception hierarchy:
    DjbError (base)
    ├── ImproperlyConfigured - Invalid configuration
    ├── ProjectNotFound - Project directory not found
    ├── SecretsError - Secrets-related errors
    │   ├── SecretsKeyNotFound - Age key file missing
    │   ├── SecretsDecryptionFailed - Decryption failed
    │   └── SecretsFileNotFound - Secrets file missing
    └── DeploymentError - Deployment-related errors
        ├── HerokuAuthError - Heroku authentication failed
        └── HerokuPushError - Heroku push failed
"""

from __future__ import annotations

from djb.core.exceptions import (
    DeploymentError,
    DjbError,
    HerokuAuthError,
    HerokuPushError,
    ImproperlyConfigured,
    ProjectNotFound,
    SecretsDecryptionFailed,
    SecretsError,
    SecretsFileNotFound,
    SecretsKeyNotFound,
)

__all__ = [
    # Base
    "DjbError",
    "ImproperlyConfigured",
    "ProjectNotFound",
    # Secrets
    "SecretsDecryptionFailed",
    "SecretsError",
    "SecretsFileNotFound",
    "SecretsKeyNotFound",
    # Deployment
    "DeploymentError",
    "HerokuAuthError",
    "HerokuPushError",
]
