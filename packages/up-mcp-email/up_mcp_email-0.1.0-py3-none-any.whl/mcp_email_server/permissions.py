"""CRUDLEX permission system for email accounts.

CRUDLEX is a permission model extending CRUD:
- Create: Create drafts
- Read: Read email content
- Update: Modify metadata (read/unread, folders, tags)
- Delete: Delete emails
- List: List emails (metadata without content)
- Export: Download attachments
- eXecute: Send emails (actions with external effects)
"""

from enum import Flag, auto


class Permission(Flag):
    """CRUDLEX permission flags for email operations."""

    NONE = 0

    # Core CRUD
    CREATE = auto()  # Create drafts (future)
    READ = auto()  # Read email content
    UPDATE = auto()  # Modify metadata (read/unread, folders, tags)
    DELETE = auto()  # Delete emails

    # Extended LEX
    LIST = auto()  # List emails (metadata without content)
    EXPORT = auto()  # Download attachments
    EXECUTE = auto()  # Send emails

    # Common combinations
    FULL = CREATE | READ | UPDATE | DELETE | LIST | EXPORT | EXECUTE
    READONLY = LIST | READ
    NO_SEND = CREATE | READ | UPDATE | DELETE | LIST | EXPORT  # All except EXECUTE
    NO_DELETE = CREATE | READ | UPDATE | LIST | EXPORT | EXECUTE  # All except DELETE
    SAFE = LIST | READ | UPDATE  # List, read, manage metadata only


def parse_permissions(value: str | int | Permission | None) -> Permission:
    """Parse permissions from various formats.

    Accepts:
    - Permission enum directly
    - Integer (bitwise flags)
    - String with pipe-separated names: "READ|LIST|UPDATE"
    - String with common aliases: "FULL", "READONLY", "SAFE"
    - None (defaults to FULL for backwards compatibility)
    """
    if value is None:
        return Permission.FULL

    if isinstance(value, Permission):
        return value

    if isinstance(value, int):
        return Permission(value)

    if isinstance(value, str):
        value = value.strip().upper()

        # Check for predefined aliases
        if hasattr(Permission, value):
            return getattr(Permission, value)

        # Parse pipe-separated permissions
        result = Permission.NONE
        for name in value.split("|"):
            name = name.strip()
            if name and hasattr(Permission, name):
                result |= getattr(Permission, name)
        return result

    raise ValueError(f"Cannot parse permissions from: {value!r}")


def format_permissions(perms: Permission) -> str:
    """Format permissions as pipe-separated string in CRUDLEX order."""
    if perms == Permission.NONE:
        return "NONE"
    if perms == Permission.FULL:
        return "FULL"

    # CRUDLEX order
    crudlex_order = ["CREATE", "READ", "UPDATE", "DELETE", "LIST", "EXPORT", "EXECUTE"]
    names = []
    for name in crudlex_order:
        p = getattr(Permission, name)
        if p in perms:
            names.append(name)
    return "|".join(names)


def check_permission(current: Permission, required: Permission) -> bool:
    """Check if current permissions include all required permissions."""
    return (current & required) == required


def require_permission(current: Permission, required: Permission, operation: str, account: str) -> None:
    """Raise PermissionError if required permission is not present."""
    if not check_permission(current, required):
        missing = required & ~current
        raise PermissionError(
            f"Account '{account}' lacks {format_permissions(missing)} permission for: {operation}"
        )
