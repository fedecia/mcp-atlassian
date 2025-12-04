"""
Common Confluence entity models.
This module provides Pydantic models for common Confluence entities like users
and attachments.
"""

import logging
import warnings
from typing import Any

from ..base import ApiModel
from ..constants import (
    UNASSIGNED,
)

logger = logging.getLogger(__name__)


class ConfluenceUser(ApiModel):
    """
    Model representing a Confluence user.
    """

    account_id: str | None = None
    username: str | None = None  # Server: often the AD/LDAP username
    display_name: str = UNASSIGNED
    email: str | None = None
    profile_picture: str | None = None
    is_active: bool = True
    locale: str | None = None

    @property
    def name(self) -> str:
        """
        Alias for display_name to maintain compatibility with tests.

        Deprecated: Use display_name instead.
        """
        warnings.warn(
            "The 'name' property is deprecated. Use 'display_name' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.display_name

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ConfluenceUser":
        """
        Create a ConfluenceUser from a Confluence API response.

        Args:
            data: The user data from the Confluence API

        Returns:
            A ConfluenceUser instance
        """
        if not data:
            return cls()

        # Debug: log all keys to find email field
        logger.debug(f"ConfluenceUser raw data keys: {list(data.keys())}")

        profile_pic = None
        if pic_data := data.get("profilePicture"):
            # Use the full path to the profile picture
            profile_pic = pic_data.get("path")

        # Try multiple possible email field names (Cloud vs Server)
        email = data.get("email") or data.get("emailAddress")

        # For Server: try to extract from username if it looks like an email
        if not email:
            username = data.get("username", "")
            if "@" in username:
                email = username

        # Get username (Server uses 'username', Cloud uses 'accountId')
        username = data.get("username") or data.get("name")

        return cls(
            account_id=data.get("accountId"),
            username=username,
            display_name=data.get("displayName", UNASSIGNED),
            email=email,
            profile_picture=profile_pic,
            is_active=data.get("accountStatus") == "active",
            locale=data.get("locale"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        return {
            "display_name": self.display_name,
            "username": self.username,
            "email": self.email,
            "profile_picture": self.profile_picture,
        }


class ConfluenceAttachment(ApiModel):
    """
    Model representing a Confluence attachment.
    """

    id: str | None = None
    type: str | None = None
    status: str | None = None
    title: str | None = None
    media_type: str | None = None
    file_size: int | None = None

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "ConfluenceAttachment":
        """
        Create a ConfluenceAttachment from a Confluence API response.

        Args:
            data: The attachment data from the Confluence API

        Returns:
            A ConfluenceAttachment instance
        """
        if not data:
            return cls()

        return cls(
            id=data.get("id"),
            type=data.get("type"),
            status=data.get("status"),
            title=data.get("title"),
            media_type=data.get("extensions", {}).get("mediaType"),
            file_size=data.get("extensions", {}).get("fileSize"),
        )

    def to_simplified_dict(self) -> dict[str, Any]:
        """Convert to simplified dictionary for API response."""
        return {
            "id": self.id,
            "type": self.type,
            "status": self.status,
            "title": self.title,
            "media_type": self.media_type,
            "file_size": self.file_size,
        }
