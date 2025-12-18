"""
FlowMason Instance Initialization.

Complete setup flow for new FlowMason instances/organizations.
"""

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from flowmason_studio.setup.core_packages import CorePackageInstaller

logger = logging.getLogger(__name__)


async def initialize_new_instance(
    organization_id: str,
    owner_email: str,
    packages_dir: Optional[str | Path] = None,
    create_default_pipelines: bool = True,
    send_welcome: bool = True,
) -> dict:
    """
    Complete setup for a new FlowMason instance.

    This function orchestrates all the steps needed to set up a new
    FlowMason organization:
    1. Create organization in database
    2. Create owner profile
    3. Install core packages
    4. Create default pipelines (optional)
    5. Send welcome email (optional)

    Args:
        organization_id: Unique identifier for the organization
        owner_email: Email address of the organization owner
        packages_dir: Optional custom packages directory
        create_default_pipelines: Whether to create starter pipelines
        send_welcome: Whether to send welcome email

    Returns:
        Dictionary with setup status and details
    """
    result: Dict[str, Any] = {
        "organization_id": organization_id,
        "owner_email": owner_email,
        "steps_completed": [],
        "issues": [],
    }

    # 1. Create organization in database
    try:
        await _create_organization(organization_id, owner_email)
        result["steps_completed"].append("create_organization")
        logger.info(f"Created organization: {organization_id}")
    except Exception as e:
        logger.error(f"Failed to create organization: {e}")
        result["issues"].append(f"create_organization: {e}")
        # Can't continue without organization
        return result

    # 2. Create owner profile
    try:
        await _create_owner_profile(owner_email, organization_id)
        result["steps_completed"].append("create_owner_profile")
        logger.info(f"Created owner profile: {owner_email}")
    except Exception as e:
        logger.error(f"Failed to create owner profile: {e}")
        result["issues"].append(f"create_owner_profile: {e}")

    # 3. Install core packages
    try:
        installer = CorePackageInstaller()
        installed = await installer.install_core_packages(
            organization_id=organization_id,
            target_packages_dir=packages_dir,
        )
        result["steps_completed"].append("install_core_packages")
        result["packages_installed"] = installed
        logger.info(f"Installed {len(installed)} core packages")
    except Exception as e:
        logger.error(f"Failed to install core packages: {e}")
        result["issues"].append(f"install_core_packages: {e}")

    # 4. Create default pipelines (optional)
    if create_default_pipelines:
        try:
            pipelines = await _create_default_pipelines(organization_id)
            result["steps_completed"].append("create_default_pipelines")
            result["default_pipelines"] = pipelines
            logger.info(f"Created {len(pipelines)} default pipelines")
        except Exception as e:
            logger.error(f"Failed to create default pipelines: {e}")
            result["issues"].append(f"create_default_pipelines: {e}")

    # 5. Send welcome email (optional)
    if send_welcome:
        try:
            await _send_welcome_email(owner_email, organization_id)
            result["steps_completed"].append("send_welcome_email")
            logger.info(f"Sent welcome email to {owner_email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email: {e}")
            result["issues"].append(f"send_welcome_email: {e}")

    result["success"] = len(result["issues"]) == 0
    logger.info(f"Instance initialized: {organization_id} (success={result['success']})")

    return result


async def _create_organization(organization_id: str, owner_email: str) -> dict:
    """
    Create organization record in database.

    This is a placeholder - actual implementation depends on database setup.
    """
    # TODO: Implement with actual database operations
    # Example:
    # from flowmason_studio.db.repositories import OrganizationRepository
    # repo = OrganizationRepository()
    # return await repo.create(organization_id=organization_id, owner_email=owner_email)

    return {
        "id": organization_id,
        "owner_email": owner_email,
        "created": True,
    }


async def _create_owner_profile(owner_email: str, organization_id: str) -> dict:
    """
    Create owner profile in database.

    This is a placeholder - actual implementation depends on auth setup.
    """
    # TODO: Implement with actual database operations
    # Example:
    # from flowmason_studio.db.repositories import UserRepository
    # repo = UserRepository()
    # return await repo.create(email=owner_email, organization_id=organization_id, role="owner")

    return {
        "email": owner_email,
        "organization_id": organization_id,
        "role": "owner",
        "created": True,
    }


async def _create_default_pipelines(organization_id: str) -> list:
    """
    Create starter pipelines for new organizations.

    These are example pipelines that demonstrate FlowMason capabilities.
    """
    # TODO: Implement with actual pipeline creation
    # Example pipelines:
    # - Simple Generator pipeline
    # - Generator -> Critic -> Improver loop
    # - HTTP webhook integration

    default_pipelines = [
        {
            "name": "Hello World",
            "description": "Simple text generation pipeline",
            "created": True,
        },
    ]

    return default_pipelines


async def _send_welcome_email(owner_email: str, organization_id: str) -> None:
    """
    Send welcome email to new organization owner.

    This is a placeholder - actual implementation depends on email service.
    """
    # TODO: Implement with actual email service
    # Example:
    # from flowmason_studio.services.email import EmailService
    # email = EmailService()
    # await email.send_welcome(owner_email, organization_id)

    logger.info(f"[MOCK] Would send welcome email to {owner_email}")
