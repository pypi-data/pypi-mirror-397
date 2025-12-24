import time
from datetime import datetime
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from mcp_email_server.config import (
    AccountAttributes,
    EmailSettings,
    ProviderSettings,
    get_settings,
    store_settings,
)
from mcp_email_server.emails.dispatcher import dispatch_handler
from mcp_email_server.permissions import Permission, format_permissions, require_permission
from mcp_email_server.emails.models import (
    AttachmentDownloadResponse,
    CategoryUnread,
    EmailContentBatchResponse,
    EmailMetadataPageResponse,
    EmailSizeInfo,
    UnreadResponse,
    format_size,
)

mcp = FastMCP("email")


def _check_permission(account_name: str, required: Permission, operation: str) -> None:
    """Check if account has required permission, raise PermissionError if not."""
    settings = get_settings()
    account = settings.get_account(account_name)
    if not account:
        raise ValueError(f"Account '{account_name}' not found")
    if isinstance(account, EmailSettings):
        require_permission(account.permissions, required, operation, account_name)


@mcp.resource("email://{account_name}")
async def get_account(account_name: str) -> EmailSettings | ProviderSettings | None:
    settings = get_settings()
    return settings.get_account(account_name, masked=True)


@mcp.tool(description="List all configured email accounts with masked credentials.")
async def list_available_accounts() -> list[AccountAttributes]:
    settings = get_settings()
    return [account.masked() for account in settings.get_accounts()]


@mcp.tool(description="Add a new email account configuration to the settings.")
async def add_email_account(email: EmailSettings) -> str:
    start_time = time.time()
    settings = get_settings()
    settings.add_email(email)
    settings.store()
    elapsed_ms = int((time.time() - start_time) * 1000)
    return f"Successfully added email account '{email.account_name}' ({elapsed_ms}ms)"


@mcp.tool(
    description="Update an existing email account's password and/or display name. At least one of password or full_name must be provided."
)
async def update_email_account(
    account_name: Annotated[str, Field(description="The name of the email account to update.")],
    password: Annotated[
        str | None,
        Field(default=None, description="New password (App Password for Gmail). Updates both IMAP and SMTP."),
    ] = None,
    full_name: Annotated[
        str | None,
        Field(default=None, description="New display name for the account."),
    ] = None,
) -> str:
    if password is None and full_name is None:
        raise ValueError("At least one of 'password' or 'full_name' must be provided")

    settings = get_settings()
    if not settings.update_account(account_name, password=password, full_name=full_name):
        raise ValueError(f"Account '{account_name}' not found")

    settings.store()

    updated_fields = []
    if password is not None:
        updated_fields.append("password")
    if full_name is not None:
        updated_fields.append(f"full_name='{full_name}'")

    return f"Account '{account_name}' updated: {', '.join(updated_fields)}"


@mcp.tool(
    description="List email metadata (email_id, subject, sender, recipients, date) without body content. Returns email_id for use with get_emails_content."
)
async def list_emails_metadata(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    page: Annotated[
        int,
        Field(default=1, description="The page number to retrieve (starting from 1)."),
    ] = 1,
    page_size: Annotated[int, Field(default=10, description="The number of emails to retrieve per page.")] = 10,
    before: Annotated[
        datetime | None,
        Field(default=None, description="Retrieve emails before this datetime (UTC)."),
    ] = None,
    since: Annotated[
        datetime | None,
        Field(default=None, description="Retrieve emails since this datetime (UTC)."),
    ] = None,
    subject: Annotated[str | None, Field(default=None, description="Filter emails by subject.")] = None,
    from_address: Annotated[str | None, Field(default=None, description="Filter emails by sender address.")] = None,
    to_address: Annotated[
        str | None,
        Field(default=None, description="Filter emails by recipient address."),
    ] = None,
    order: Annotated[
        Literal["asc", "desc"],
        Field(default=None, description="Order emails by field. `asc` or `desc`."),
    ] = "desc",
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox to retrieve emails from.")] = "INBOX",
) -> EmailMetadataPageResponse:
    _check_permission(account_name, Permission.LIST, "list emails")
    handler = dispatch_handler(account_name)

    return await handler.get_emails_metadata(
        page=page,
        page_size=page_size,
        before=before,
        since=since,
        subject=subject,
        from_address=from_address,
        to_address=to_address,
        order=order,
        mailbox=mailbox,
    )


@mcp.tool(
    description="Get the full content (including body) of one or more emails by their email_id. Use list_emails_metadata first to get the email_id. This operation does NOT mark emails as read."
)
async def get_emails_content(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(
            description="List of email_id to retrieve (obtained from list_emails_metadata). Can be a single email_id or multiple email_ids."
        ),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox to retrieve emails from.")] = "INBOX",
) -> EmailContentBatchResponse:
    _check_permission(account_name, Permission.READ, "read email content")
    handler = dispatch_handler(account_name)
    return await handler.get_emails_content(email_ids, mailbox)


@mcp.tool(
    description="Send an email using the specified account. Supports replying to emails with proper threading when in_reply_to is provided.",
)
async def send_email(
    account_name: Annotated[str, Field(description="The name of the email account to send from.")],
    recipients: Annotated[list[str], Field(description="A list of recipient email addresses.")],
    subject: Annotated[str, Field(description="The subject of the email.")],
    body: Annotated[str, Field(description="The body of the email.")],
    cc: Annotated[
        list[str] | None,
        Field(default=None, description="A list of CC email addresses."),
    ] = None,
    bcc: Annotated[
        list[str] | None,
        Field(default=None, description="A list of BCC email addresses."),
    ] = None,
    html: Annotated[
        bool,
        Field(default=False, description="Whether to send the email as HTML (True) or plain text (False)."),
    ] = False,
    attachments: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="A list of absolute file paths to attach to the email. Supports common file types (documents, images, archives, etc.).",
        ),
    ] = None,
    in_reply_to: Annotated[
        str | None,
        Field(
            default=None,
            description="Message-ID of the email being replied to. Enables proper threading in email clients.",
        ),
    ] = None,
    references: Annotated[
        str | None,
        Field(
            default=None,
            description="Space-separated Message-IDs for the thread chain. Usually includes in_reply_to plus ancestors.",
        ),
    ] = None,
) -> str:
    _check_permission(account_name, Permission.EXECUTE, "send email")
    start_time = time.time()
    settings = get_settings()
    account = settings.get_account(account_name)
    sender_email = account.email_address if account else account_name

    handler = dispatch_handler(account_name)
    await handler.send_email(
        recipients,
        subject,
        body,
        cc,
        bcc,
        html,
        attachments,
        in_reply_to,
        references,
    )

    elapsed_ms = int((time.time() - start_time) * 1000)
    recipient_str = ", ".join(recipients)
    attachment_info = f" with {len(attachments)} attachment(s)" if attachments else ""
    return f"Email sent from {sender_email} to {recipient_str}{attachment_info} ({elapsed_ms}ms)"


@mcp.tool(
    description="Delete one or more emails by their email_id. Use list_emails_metadata first to get the email_id."
)
async def delete_emails(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(description="List of email_id to delete (obtained from list_emails_metadata)."),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox to delete emails from.")] = "INBOX",
) -> str:
    _check_permission(account_name, Permission.DELETE, "delete emails")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    deleted_ids, failed_ids = await handler.delete_emails(email_ids, mailbox)

    elapsed_ms = int((time.time() - start_time) * 1000)
    result = f"Successfully deleted {len(deleted_ids)} email(s)"
    if failed_ids:
        result += f", failed to delete {len(failed_ids)} email(s): {', '.join(failed_ids)}"
    return f"{result} ({elapsed_ms}ms)"


@mcp.tool(
    description="Download an email attachment and save it to the specified path. This feature must be explicitly enabled in settings (enable_attachment_download=true) due to security considerations.",
)
async def download_attachment(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_id: Annotated[
        str, Field(description="The email ID (obtained from list_emails_metadata or get_emails_content).")
    ],
    attachment_name: Annotated[
        str, Field(description="The name of the attachment to download (as shown in the attachments list).")
    ],
    save_path: Annotated[str, Field(description="The absolute path where the attachment should be saved.")],
) -> AttachmentDownloadResponse:
    _check_permission(account_name, Permission.EXPORT, "download attachment")
    settings = get_settings()
    if not settings.enable_attachment_download:
        msg = (
            "Attachment download is disabled. Set 'enable_attachment_download=true' in settings to enable this feature."
        )
        raise PermissionError(msg)

    handler = dispatch_handler(account_name)
    return await handler.download_attachment(email_id, attachment_name, save_path)


@mcp.tool(
    description="Check for unread emails. Returns count of unread and total emails, plus IDs and sizes of most recent unread.",
)
async def check_unread(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    max_ids: Annotated[
        int, Field(default=20, description="Maximum number of unread email IDs to return per category.")
    ] = 20,
) -> UnreadResponse:
    _check_permission(account_name, Permission.LIST, "check unread")
    handler = dispatch_handler(account_name)
    result = await handler.get_unread(max_ids)

    # Convert dict to CategoryUnread models
    by_category = {}
    for cat, data in result["by_category"].items():
        emails_with_size = None
        if "emails" in data and data["emails"]:
            emails_with_size = [
                EmailSizeInfo(
                    email_id=e["email_id"],
                    size_bytes=e["size_bytes"],
                    size_human=format_size(e["size_bytes"]),
                )
                for e in data["emails"]
            ]
        by_category[cat] = CategoryUnread(
            unread_count=data["unread_count"],
            email_ids=data["email_ids"],
            emails=emails_with_size,
            has_more=data["has_more"],
        )

    return UnreadResponse(
        total_unread=result["total_unread"],
        total_count=result["total_count"],
        by_category=by_category,
    )


@mcp.tool(
    description="Mark one or more emails as read without fetching their content.",
)
async def mark_as_read(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(description="List of email_id to mark as read (obtained from check_unread or list_emails_metadata)."),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox containing the emails.")] = "INBOX",
) -> str:
    _check_permission(account_name, Permission.UPDATE, "mark as read")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    marked_ids, failed_ids = await handler.mark_as_read(email_ids, mailbox)

    elapsed_ms = int((time.time() - start_time) * 1000)
    result = f"Marked {len(marked_ids)} email(s) as read"
    if failed_ids:
        result += f", failed to mark {len(failed_ids)} email(s): {', '.join(failed_ids)}"
    return f"{result} ({elapsed_ms}ms)"


@mcp.tool(
    description="Mark one or more emails as unread.",
)
async def mark_as_unread(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(description="List of email_id to mark as unread (obtained from list_emails_metadata)."),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox containing the emails.")] = "INBOX",
) -> str:
    _check_permission(account_name, Permission.UPDATE, "mark as unread")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    marked_ids, failed_ids = await handler.mark_as_unread(email_ids, mailbox)

    elapsed_ms = int((time.time() - start_time) * 1000)
    result = f"Marked {len(marked_ids)} email(s) as unread"
    if failed_ids:
        result += f", failed to mark {len(failed_ids)} email(s): {', '.join(failed_ids)}"
    return f"{result} ({elapsed_ms}ms)"


@mcp.tool(
    description="Update CRUDLEX permissions for an email account. Permissions: CREATE, READ, UPDATE, DELETE, LIST, EXPORT, EXECUTE. Use pipe-separated values (e.g., 'READ|LIST|UPDATE') or aliases: FULL, READONLY, SAFE, NO_SEND, NO_DELETE.",
)
async def update_account_permissions(
    account_name: Annotated[str, Field(description="The name of the email account to update.")],
    permissions: Annotated[
        str,
        Field(
            description="New permissions. Use pipe-separated values like 'READ|LIST|UPDATE' or aliases: FULL (all), READONLY (LIST|READ), SAFE (LIST|READ|UPDATE), NO_SEND (all except EXECUTE), NO_DELETE (all except DELETE)."
        ),
    ],
) -> str:
    settings = get_settings()
    account = settings.get_account(account_name)
    if not account:
        raise ValueError(f"Account '{account_name}' not found")
    if not isinstance(account, EmailSettings):
        raise ValueError(f"Account '{account_name}' is not an email account")

    old_perms = format_permissions(account.permissions)
    if not settings.update_permissions(account_name, permissions):
        raise ValueError(f"Failed to update permissions for '{account_name}'")
    store_settings(settings)

    new_perms = format_permissions(settings.get_account(account_name).permissions)
    return f"Updated '{account_name}' permissions: {old_perms} -> {new_perms}"


@mcp.tool(
    description="List flagged emails with their keywords. Returns counts by keyword (e.g., Personal, Alta, HOLD) and email IDs.",
)
async def list_flagged(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    keyword: Annotated[
        str | None,
        Field(default=None, description="Filter by specific keyword (e.g., 'Personal', 'Alta'). If not specified, returns all flagged emails grouped by keyword."),
    ] = None,
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox to search.")] = "INBOX",
) -> dict:
    _check_permission(account_name, Permission.LIST, "list flagged emails")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    result = await handler.get_flagged_emails(keyword, mailbox)
    result["elapsed_ms"] = int((time.time() - start_time) * 1000)
    return result


@mcp.tool(
    description="Add a flag or keyword to one or more emails. Use '\\\\Flagged' for the standard flag, or custom keywords like 'Personal', 'Alta', 'HOLD'.",
)
async def set_flag(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(description="List of email_id to flag (obtained from list_emails_metadata)."),
    ],
    flags: Annotated[
        list[str],
        Field(description="Flags to add. Use '\\\\Flagged' for standard flag, or keywords like 'Personal', 'Alta'."),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox containing the emails.")] = "INBOX",
) -> str:
    _check_permission(account_name, Permission.UPDATE, "set flags")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    success_ids, failed_ids = await handler.set_flags(email_ids, flags, mailbox)

    elapsed_ms = int((time.time() - start_time) * 1000)
    result = f"Added flags to {len(success_ids)} email(s)"
    if failed_ids:
        result += f", failed on {len(failed_ids)} email(s): {', '.join(failed_ids)}"
    return f"{result} ({elapsed_ms}ms)"


@mcp.tool(
    description="Remove a flag or keyword from one or more emails. Use '\\\\Flagged' to unflag, or specify keywords to remove.",
)
async def remove_flag(
    account_name: Annotated[str, Field(description="The name of the email account.")],
    email_ids: Annotated[
        list[str],
        Field(description="List of email_id to unflag (obtained from list_emails_metadata)."),
    ],
    flags: Annotated[
        list[str],
        Field(description="Flags to remove. Use '\\\\Flagged' to remove standard flag, or keywords like 'Personal', 'Alta'."),
    ],
    mailbox: Annotated[str, Field(default="INBOX", description="The mailbox containing the emails.")] = "INBOX",
) -> str:
    _check_permission(account_name, Permission.UPDATE, "remove flags")
    start_time = time.time()
    handler = dispatch_handler(account_name)
    success_ids, failed_ids = await handler.remove_flags(email_ids, flags, mailbox)

    elapsed_ms = int((time.time() - start_time) * 1000)
    result = f"Removed flags from {len(success_ids)} email(s)"
    if failed_ids:
        result += f", failed on {len(failed_ids)} email(s): {', '.join(failed_ids)}"
    return f"{result} ({elapsed_ms}ms)"
