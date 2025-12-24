from datetime import datetime
from typing import Any

from pydantic import BaseModel


def format_size(size_bytes: int) -> str:
    """Format bytes to human readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


class EmailMetadata(BaseModel):
    """Email metadata"""

    email_id: str
    message_id: str | None = None  # RFC 5322 Message-ID header for reply threading
    subject: str
    sender: str
    recipients: list[str]  # Recipient list
    date: datetime
    attachments: list[str]
    size_bytes: int | None = None
    size_human: str | None = None
    flags: list[str] | None = None  # IMAP flags (e.g., \Seen, \Flagged)
    keywords: list[str] | None = None  # Custom keywords (e.g., Personal, Alta, HOLD)

    @classmethod
    def from_email(cls, email: dict[str, Any]):
        size_bytes = email.get("size_bytes")
        return cls(
            email_id=email["email_id"],
            message_id=email.get("message_id"),
            subject=email["subject"],
            sender=email["from"],
            recipients=email.get("to", []),
            date=email["date"],
            attachments=email["attachments"],
            size_bytes=size_bytes,
            size_human=format_size(size_bytes) if size_bytes else None,
            flags=email.get("flags"),
            keywords=email.get("keywords"),
        )


class EmailMetadataPageResponse(BaseModel):
    """Paged email metadata response"""

    page: int
    page_size: int
    before: datetime | None
    since: datetime | None
    subject: str | None
    emails: list[EmailMetadata]
    total: int


class EmailBodyResponse(BaseModel):
    """Single email body response"""

    email_id: str  # IMAP UID of this email
    message_id: str | None = None  # RFC 5322 Message-ID header for reply threading
    subject: str
    sender: str
    recipients: list[str]
    date: datetime
    body: str
    attachments: list[str]
    flags: list[str] | None = None  # IMAP flags (e.g., \Seen, \Flagged)
    keywords: list[str] | None = None  # Custom keywords (e.g., Personal, Alta, HOLD)


class EmailContentBatchResponse(BaseModel):
    """Batch email content response for multiple emails"""

    emails: list[EmailBodyResponse]
    requested_count: int
    retrieved_count: int
    failed_ids: list[str]


class AttachmentDownloadResponse(BaseModel):
    """Attachment download response"""

    email_id: str
    attachment_name: str
    mime_type: str
    size: int
    saved_path: str


class EmailSizeInfo(BaseModel):
    """Email ID with size information"""

    email_id: str
    size_bytes: int
    size_human: str


class CategoryUnread(BaseModel):
    """Unread info for a single category/mailbox"""

    unread_count: int
    email_ids: list[str]  # Kept for backwards compatibility
    emails: list[EmailSizeInfo] | None = None  # New: includes size info
    has_more: bool


class UnreadResponse(BaseModel):
    """Unread emails check response with category breakdown"""

    total_unread: int
    total_count: int
    by_category: dict[str, CategoryUnread]
