import email.utils
import mimetypes
import re
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.parser import BytesParser
from email.policy import default
from pathlib import Path
from typing import Any

import aioimaplib
import aiosmtplib
import markdown

from mcp_email_server.config import EmailServer, EmailSettings
from mcp_email_server.emails import EmailHandler
from mcp_email_server.emails.models import (
    AttachmentDownloadResponse,
    EmailBodyResponse,
    EmailContentBatchResponse,
    EmailMetadata,
    EmailMetadataPageResponse,
)
from mcp_email_server.log import logger

# Regex patterns for content detection
FRONTMATTER_PATTERN = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
HTML_TAG_PATTERN = re.compile(r"<(p|div|br|h[1-6]|ul|ol|li|table|tr|td|th|span|a|img|strong|em)\b", re.IGNORECASE)
MARKDOWN_PATTERNS = [
    re.compile(r"^#{1,6}\s+", re.MULTILINE),  # Headers
    re.compile(r"\*\*[^*]+\*\*"),  # Bold
    re.compile(r"\*[^*]+\*"),  # Italic
    re.compile(r"^\s*[-*+]\s+", re.MULTILINE),  # Unordered lists
    re.compile(r"^\s*\d+\.\s+", re.MULTILINE),  # Ordered lists
    re.compile(r"\[.+?\]\(.+?\)"),  # Links
    re.compile(r"```"),  # Code blocks
    re.compile(r"`[^`]+`"),  # Inline code
    re.compile(r"^\|.+\|$", re.MULTILINE),  # Tables
]


def parse_frontmatter(body: str) -> tuple[dict[str, str], str]:
    """Extract YAML frontmatter from body. Returns (metadata, body_without_frontmatter)."""
    match = FRONTMATTER_PATTERN.match(body)
    if not match:
        return {}, body

    frontmatter_content = match.group(1)
    body_without_frontmatter = body[match.end():]

    # Simple YAML parsing (key: value pairs only)
    metadata = {}
    for line in frontmatter_content.split("\n"):
        line = line.strip()
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip().lower()] = value.strip().strip("\"'")

    return metadata, body_without_frontmatter


def detect_content_type(body: str) -> str:
    """Detect if body is 'html', 'markdown', or 'plain'."""
    # Check for HTML first
    if HTML_TAG_PATTERN.search(body):
        return "html"

    # Check for Markdown patterns
    markdown_matches = sum(1 for pattern in MARKDOWN_PATTERNS if pattern.search(body))
    if markdown_matches >= 2:  # At least 2 markdown patterns to be confident
        return "markdown"

    return "plain"


def convert_markdown_to_html(body: str) -> str:
    """Convert Markdown to HTML with common extensions."""
    md = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br"])
    return md.convert(body)


def strip_html_tags(html: str) -> str:
    """Remove HTML tags for plain text version."""
    clean = re.sub(r"<[^>]+>", "", html)
    return re.sub(r"\n\s*\n", "\n\n", clean).strip()


class IMAPConnectionError(Exception):
    """Custom exception for IMAP connection errors with descriptive messages."""

    pass


# Apple Mail color flags mapping
# $MailFlagBit0 = 1, $MailFlagBit1 = 2, $MailFlagBit2 = 4
APPLE_MAIL_COLORS = {
    1: "Red",
    2: "Orange",
    3: "Yellow",
    4: "Green",
    5: "Blue",
    6: "Purple",
    7: "Gray",
}


def _convert_mail_flag_bits_to_color(keywords: list[str]) -> tuple[list[str], str | None]:
    """Convert $MailFlagBit* keywords to Apple Mail color name.

    Returns:
        Tuple of (remaining_keywords, color_name or None)
    """
    bit_value = 0
    remaining = []

    for kw in keywords:
        if kw == "$MailFlagBit0":
            bit_value |= 1
        elif kw == "$MailFlagBit1":
            bit_value |= 2
        elif kw == "$MailFlagBit2":
            bit_value |= 4
        else:
            remaining.append(kw)

    color = APPLE_MAIL_COLORS.get(bit_value) if bit_value > 0 else None
    return remaining, color


class EmailClient:
    def __init__(self, email_server: EmailServer, sender: str | None = None):
        self.email_server = email_server
        self.sender = sender or email_server.user_name

        self.imap_class = aioimaplib.IMAP4_SSL if self.email_server.use_ssl else aioimaplib.IMAP4

        self.smtp_use_tls = self.email_server.use_ssl
        self.smtp_start_tls = self.email_server.start_ssl

    async def _imap_connect_and_login(self, imap, server: EmailServer | None = None) -> None:
        """Connect and login to IMAP server with descriptive error handling.

        Args:
            imap: The IMAP client instance
            server: Optional server config. Uses self.email_server if not provided.

        Raises:
            IMAPConnectionError: With descriptive message on connection/login failure.
        """
        server = server or self.email_server
        host = server.host
        port = server.port
        user = server.user_name

        try:
            await imap._client_task
        except TimeoutError as e:
            msg = f"Connection timeout to IMAP server {host}:{port}"
            logger.error(msg)
            raise IMAPConnectionError(msg) from e
        except OSError as e:
            msg = f"Cannot connect to IMAP server {host}:{port}: {e or 'Connection refused'}"
            logger.error(msg)
            raise IMAPConnectionError(msg) from e

        try:
            await imap.wait_hello_from_server()
        except TimeoutError as e:
            msg = f"Timeout waiting for IMAP server {host}:{port} greeting"
            logger.error(msg)
            raise IMAPConnectionError(msg) from e

        try:
            response = await imap.login(user, server.password)
            # aioimaplib returns Response with result='NO' on auth failure, not exception
            if response.result != "OK":
                error_lines = [line.decode() if isinstance(line, bytes) else str(line) for line in response.lines]
                error_detail = " ".join(error_lines) or "Authentication failed"
                msg = f"Login failed for {user} on {host}:{port}: {error_detail}"
                logger.error(msg)
                raise IMAPConnectionError(msg)
        except TimeoutError as e:
            msg = f"Login timeout for {user} on IMAP server {host}:{port}"
            logger.error(msg)
            raise IMAPConnectionError(msg) from e
        except IMAPConnectionError:
            raise
        except Exception as e:
            error_detail = str(e) if str(e) else "Authentication failed"
            msg = f"Login failed for {user} on {host}:{port}: {error_detail}"
            logger.error(msg)
            raise IMAPConnectionError(msg) from e

    def _parse_email_data(self, raw_email: bytes, email_id: str | None = None) -> dict[str, Any]:  # noqa: C901
        """Parse raw email data into a structured dictionary."""
        parser = BytesParser(policy=default)
        email_message = parser.parsebytes(raw_email)

        # Extract email parts
        subject = email_message.get("Subject", "")
        sender = email_message.get("From", "")
        date_str = email_message.get("Date", "")

        # Extract Message-ID for reply threading
        message_id = email_message.get("Message-ID")

        # Extract recipients
        to_addresses = []
        to_header = email_message.get("To", "")
        if to_header:
            # Simple parsing - split by comma and strip whitespace
            to_addresses = [addr.strip() for addr in to_header.split(",")]

        # Also check CC recipients
        cc_header = email_message.get("Cc", "")
        if cc_header:
            to_addresses.extend([addr.strip() for addr in cc_header.split(",")])

        # Parse date
        try:
            date_tuple = email.utils.parsedate_tz(date_str)
            date = (
                datetime.fromtimestamp(email.utils.mktime_tz(date_tuple), tz=timezone.utc)
                if date_tuple
                else datetime.now(timezone.utc)
            )
        except Exception:
            date = datetime.now(timezone.utc)

        # Get body content
        body = ""
        attachments = []

        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition", ""))

                # Handle attachments
                if "attachment" in content_disposition:
                    filename = part.get_filename()
                    if filename:
                        attachments.append(filename)
                # Handle text parts
                elif content_type == "text/plain":
                    body_part = part.get_payload(decode=True)
                    if body_part:
                        charset = part.get_content_charset("utf-8")
                        try:
                            body += body_part.decode(charset)
                        except UnicodeDecodeError:
                            body += body_part.decode("utf-8", errors="replace")
        else:
            # Handle plain text emails
            payload = email_message.get_payload(decode=True)
            if payload:
                charset = email_message.get_content_charset("utf-8")
                try:
                    body = payload.decode(charset)
                except UnicodeDecodeError:
                    body = payload.decode("utf-8", errors="replace")
        # TODO: Allow retrieving full email body
        if body and len(body) > 20000:
            body = body[:20000] + "...[TRUNCATED]"
        return {
            "email_id": email_id or "",
            "message_id": message_id,
            "subject": subject,
            "from": sender,
            "to": to_addresses,
            "body": body,
            "date": date,
            "attachments": attachments,
        }

    @staticmethod
    def _build_search_criteria(
        before: datetime | None = None,
        since: datetime | None = None,
        subject: str | None = None,
        body: str | None = None,
        text: str | None = None,
        from_address: str | None = None,
        to_address: str | None = None,
    ):
        search_criteria = []
        if before:
            search_criteria.extend(["BEFORE", before.strftime("%d-%b-%Y").upper()])
        if since:
            search_criteria.extend(["SINCE", since.strftime("%d-%b-%Y").upper()])
        if subject:
            search_criteria.extend(["SUBJECT", subject])
        if body:
            search_criteria.extend(["BODY", body])
        if text:
            search_criteria.extend(["TEXT", text])
        if from_address:
            search_criteria.extend(["FROM", from_address])
        if to_address:
            search_criteria.extend(["TO", to_address])

        # If no specific criteria, search for ALL
        if not search_criteria:
            search_criteria = ["ALL"]

        return search_criteria

    async def get_email_count(
        self,
        before: datetime | None = None,
        since: datetime | None = None,
        subject: str | None = None,
        from_address: str | None = None,
        to_address: str | None = None,
        mailbox: str = "INBOX",
    ) -> int:
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)
            search_criteria = self._build_search_criteria(
                before, since, subject, from_address=from_address, to_address=to_address
            )
            logger.info(f"Count: Search criteria: {search_criteria}")
            # Search for messages and count them - use UID SEARCH for consistency
            _, messages = await imap.uid_search(*search_criteria)
            return len(messages[0].split())
        finally:
            # Ensure we logout properly
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    # Gmail categories to check
    GMAIL_CATEGORIES = [
        "INBOX",
        "CATEGORY_SOCIAL",
        "CATEGORY_PROMOTIONS",
        "CATEGORY_UPDATES",
        "CATEGORY_FORUMS",
    ]

    def _is_gmail(self) -> bool:
        """Check if this is a Gmail account."""
        return "gmail" in self.email_server.host.lower()

    async def _get_unread_for_mailbox(
        self,
        imap,
        mailbox: str,
        max_ids: int,
    ) -> dict[str, Any]:
        """Get unread info for a single mailbox."""
        try:
            result = await imap.select(mailbox)
            status = result[0] if isinstance(result, tuple) else result
            if str(status).upper() != "OK":
                return {"unread_count": 0, "email_ids": [], "emails": [], "has_more": False}

            _, unseen_messages = await imap.uid_search("UNSEEN")
            unseen_ids = []
            if unseen_messages and unseen_messages[0]:
                unseen_ids = [uid.decode("utf-8") for uid in unseen_messages[0].split()]

            unread_count = len(unseen_ids)
            recent_ids = list(reversed(unseen_ids))[:max_ids]
            has_more = unread_count > max_ids

            # Fetch sizes for recent emails
            emails_with_size = []
            for email_id in recent_ids:
                try:
                    _, data = await imap.uid("fetch", email_id, "RFC822.SIZE")
                    size_bytes = 0
                    if data:
                        for item in data:
                            if isinstance(item, bytes) and b"RFC822.SIZE" in item:
                                match = re.search(rb"RFC822\.SIZE\s+(\d+)", item)
                                if match:
                                    size_bytes = int(match.group(1))
                                break
                    emails_with_size.append({"email_id": email_id, "size_bytes": size_bytes})
                except Exception as e:
                    logger.warning(f"Failed to get size for email {email_id}: {e}")
                    emails_with_size.append({"email_id": email_id, "size_bytes": 0})

            return {
                "unread_count": unread_count,
                "email_ids": recent_ids,
                "emails": emails_with_size,
                "has_more": has_more,
            }
        except Exception as e:
            logger.warning(f"Failed to get unread for mailbox {mailbox}: {e}")
            return {"unread_count": 0, "email_ids": [], "emails": [], "has_more": False}

    async def get_unread(
        self,
        max_ids: int = 20,
    ) -> dict[str, Any]:
        """Get unread emails count and IDs, with category breakdown for Gmail."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        try:
            await self._imap_connect_and_login(imap)

            # Get total count from INBOX
            await imap.select("INBOX")
            _, all_messages = await imap.uid_search("ALL")
            total_count = len(all_messages[0].split()) if all_messages and all_messages[0] else 0

            # Determine which categories to check
            categories = self.GMAIL_CATEGORIES if self._is_gmail() else ["INBOX"]

            # Get unread for each category
            by_category = {}
            total_unread = 0

            for category in categories:
                cat_result = await self._get_unread_for_mailbox(imap, category, max_ids)
                by_category[category] = cat_result
                total_unread += cat_result["unread_count"]

            return {
                "total_unread": total_unread,
                "total_count": total_count,
                "by_category": by_category,
            }
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def mark_as_read(
        self,
        email_ids: list[str],
        mailbox: str = "INBOX",
    ) -> tuple[list[str], list[str]]:
        """Mark emails as read. Returns (marked_ids, failed_ids)."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        marked_ids = []
        failed_ids = []

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            for email_id in email_ids:
                try:
                    await imap.uid("store", email_id, "+FLAGS", r"(\Seen)")
                    marked_ids.append(email_id)
                except Exception as e:
                    logger.error(f"Failed to mark email {email_id} as read: {e}")
                    failed_ids.append(email_id)

            return marked_ids, failed_ids
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def mark_as_unread(
        self,
        email_ids: list[str],
        mailbox: str = "INBOX",
    ) -> tuple[list[str], list[str]]:
        """Mark emails as unread. Returns (marked_ids, failed_ids)."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        marked_ids = []
        failed_ids = []

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            for email_id in email_ids:
                try:
                    await imap.uid("store", email_id, "-FLAGS", r"(\Seen)")
                    marked_ids.append(email_id)
                except Exception as e:
                    logger.error(f"Failed to mark email {email_id} as unread: {e}")
                    failed_ids.append(email_id)

            return marked_ids, failed_ids
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def get_flagged_emails(
        self,
        keyword: str | None = None,
        mailbox: str = "INBOX",
    ) -> dict[str, Any]:
        """Get flagged emails, optionally filtered by keyword. Returns counts and email IDs."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            # Search for FLAGGED emails
            _, messages = await imap.uid_search("FLAGGED")

            if not messages or not messages[0]:
                return {"total_flagged": 0, "by_keyword": {}, "email_ids": []}

            email_ids = [uid.decode("utf-8") for uid in messages[0].split()]

            # Batch fetch FLAGS in chunks (some servers have limits on command length)
            by_keyword: dict[str, list[str]] = {}
            no_keyword: list[str] = []
            email_flags: dict[str, list[str]] = {}

            # Process in chunks of 50 to avoid command length limits
            chunk_size = 50
            for i in range(0, len(email_ids), chunk_size):
                chunk = email_ids[i : i + chunk_size]
                ids_str = ",".join(chunk)

                try:
                    _, flags_data = await imap.uid("fetch", ids_str, "(FLAGS)")

                    if flags_data:
                        for item in flags_data:
                            if isinstance(item, bytes) and b"FLAGS" in item:
                                # Extract UID and FLAGS - try multiple patterns
                                uid_match = re.search(rb"UID\s+(\d+)", item)
                                if not uid_match:
                                    # Try alternative pattern: sequence number at start
                                    uid_match = re.search(rb"^(\d+)\s+\(", item)
                                flags_match = re.search(rb"FLAGS\s*\(([^)]*)\)", item)

                                if uid_match and flags_match:
                                    uid = uid_match.group(1).decode("utf-8")
                                    flags_str = flags_match.group(1).decode("utf-8")
                                    keywords = []
                                    for flag in flags_str.split():
                                        if not flag.startswith("\\") and flag not in ("Recent",):
                                            keywords.append(flag)
                                    email_flags[uid] = keywords
                except Exception as e:
                    logger.warning(f"Failed to fetch FLAGS for chunk: {e}")

            # Categorize by keyword, converting Apple Mail flag bits to colors
            for email_id in email_ids:
                raw_keywords = email_flags.get(email_id, [])
                if raw_keywords:
                    # Convert $MailFlagBit* to color name
                    keywords, color = _convert_mail_flag_bits_to_color(raw_keywords)

                    # Add color as a keyword if present
                    if color:
                        if color not in by_keyword:
                            by_keyword[color] = []
                        by_keyword[color].append(email_id)

                    # Add remaining keywords (excluding $Forwarded/Forwarded duplicates)
                    seen_forwarded = False
                    for kw in keywords:
                        # Skip duplicate Forwarded variants
                        if kw in ("$Forwarded", "Forwarded"):
                            if seen_forwarded:
                                continue
                            seen_forwarded = True
                            kw = "Forwarded"  # Normalize
                        if kw not in by_keyword:
                            by_keyword[kw] = []
                        by_keyword[kw].append(email_id)

                    # If no keywords and no color, mark as no keyword
                    if not keywords and not color:
                        no_keyword.append(email_id)
                else:
                    no_keyword.append(email_id)

            if no_keyword:
                by_keyword["(no keyword)"] = no_keyword

            # If filtering by keyword, return only those
            if keyword:
                filtered_ids = by_keyword.get(keyword, [])
                return {
                    "total_flagged": len(filtered_ids),
                    "keyword": keyword,
                    "email_ids": filtered_ids,
                }

            return {
                "total_flagged": len(email_ids),
                "by_keyword": {k: {"count": len(v), "email_ids": v} for k, v in by_keyword.items()},
                "email_ids": email_ids,
            }
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def set_flags(
        self,
        email_ids: list[str],
        flags: list[str],
        mailbox: str = "INBOX",
    ) -> tuple[list[str], list[str]]:
        """Add flags/keywords to emails. Returns (success_ids, failed_ids)."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        success_ids = []
        failed_ids = []

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            # Build flags string - system flags need backslash, keywords don't
            flag_string = "(" + " ".join(flags) + ")"

            for email_id in email_ids:
                try:
                    await imap.uid("store", email_id, "+FLAGS", flag_string)
                    success_ids.append(email_id)
                except Exception as e:
                    logger.error(f"Failed to set flags on {email_id}: {e}")
                    failed_ids.append(email_id)

            return success_ids, failed_ids
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def remove_flags(
        self,
        email_ids: list[str],
        flags: list[str],
        mailbox: str = "INBOX",
    ) -> tuple[list[str], list[str]]:
        """Remove flags/keywords from emails. Returns (success_ids, failed_ids)."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        success_ids = []
        failed_ids = []

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            flag_string = "(" + " ".join(flags) + ")"

            for email_id in email_ids:
                try:
                    await imap.uid("store", email_id, "-FLAGS", flag_string)
                    success_ids.append(email_id)
                except Exception as e:
                    logger.error(f"Failed to remove flags from {email_id}: {e}")
                    failed_ids.append(email_id)

            return success_ids, failed_ids
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def get_emails_metadata_stream(  # noqa: C901
        self,
        page: int = 1,
        page_size: int = 10,
        before: datetime | None = None,
        since: datetime | None = None,
        subject: str | None = None,
        from_address: str | None = None,
        to_address: str | None = None,
        order: str = "desc",
        mailbox: str = "INBOX",
    ) -> AsyncGenerator[dict[str, Any], None]:
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        try:
            await self._imap_connect_and_login(imap)
            try:
                await imap.id(name="mcp-email-server", version="1.0.0")
            except Exception as e:
                logger.warning(f"IMAP ID command failed: {e!s}")
            await imap.select(mailbox)

            search_criteria = self._build_search_criteria(
                before, since, subject, from_address=from_address, to_address=to_address
            )
            logger.info(f"Get metadata: Search criteria: {search_criteria}")

            # Search for messages - use UID SEARCH for better compatibility
            _, messages = await imap.uid_search(*search_criteria)

            # Handle empty or None responses
            if not messages or not messages[0]:
                logger.warning("No messages returned from search")
                email_ids = []
            else:
                email_ids = messages[0].split()
                logger.info(f"Found {len(email_ids)} email IDs")
            start = (page - 1) * page_size
            end = start + page_size

            if order == "desc":
                email_ids.reverse()

            # Fetch each message's metadata only
            for _, email_id in enumerate(email_ids[start:end]):
                try:
                    # Convert email_id from bytes to string
                    email_id_str = email_id.decode("utf-8")

                    # Fetch headers, size, and flags
                    _, data = await imap.uid("fetch", email_id_str, "(BODY.PEEK[HEADER] RFC822.SIZE FLAGS)")

                    if not data:
                        logger.error(f"Failed to fetch headers for UID {email_id_str}")
                        continue

                    # Parse RFC822.SIZE and FLAGS from response
                    size_bytes = None
                    flags = []
                    keywords = []
                    for item in data:
                        if isinstance(item, bytes):
                            # Parse size
                            if b"RFC822.SIZE" in item:
                                match = re.search(rb"RFC822\.SIZE\s+(\d+)", item)
                                if match:
                                    size_bytes = int(match.group(1))
                            # Parse flags
                            if b"FLAGS" in item:
                                flags_match = re.search(rb"FLAGS\s*\(([^)]*)\)", item)
                                if flags_match:
                                    flags_str = flags_match.group(1).decode("utf-8")
                                    for flag in flags_str.split():
                                        if flag.startswith("\\"):
                                            flags.append(flag)
                                        elif flag and flag not in ("Recent",):
                                            keywords.append(flag)

                    # Find the email headers in the response
                    raw_headers = None
                    if len(data) > 1 and isinstance(data[1], bytearray):
                        raw_headers = bytes(data[1])
                    else:
                        # Search through all items for header content
                        for item in data:
                            if isinstance(item, bytes | bytearray) and len(item) > 10:
                                # Skip IMAP protocol responses
                                if isinstance(item, bytes) and b"FETCH" in item:
                                    continue
                                # This is likely the header content
                                raw_headers = bytes(item) if isinstance(item, bytearray) else item
                                break

                    if raw_headers:
                        try:
                            # Parse headers only
                            parser = BytesParser(policy=default)
                            email_message = parser.parsebytes(raw_headers)

                            # Extract metadata
                            subject = email_message.get("Subject", "")
                            sender = email_message.get("From", "")
                            date_str = email_message.get("Date", "")

                            # Extract recipients
                            to_addresses = []
                            to_header = email_message.get("To", "")
                            if to_header:
                                to_addresses = [addr.strip() for addr in to_header.split(",")]

                            cc_header = email_message.get("Cc", "")
                            if cc_header:
                                to_addresses.extend([addr.strip() for addr in cc_header.split(",")])

                            # Parse date
                            try:
                                date_tuple = email.utils.parsedate_tz(date_str)
                                date = (
                                    datetime.fromtimestamp(email.utils.mktime_tz(date_tuple), tz=timezone.utc)
                                    if date_tuple
                                    else datetime.now(timezone.utc)
                                )
                            except Exception:
                                date = datetime.now(timezone.utc)

                            # For metadata, we don't fetch attachments to save bandwidth
                            # We'll mark it as unknown for now
                            metadata = {
                                "email_id": email_id_str,
                                "subject": subject,
                                "from": sender,
                                "to": to_addresses,
                                "date": date,
                                "attachments": [],  # We don't fetch attachment info for metadata
                                "size_bytes": size_bytes,
                                "flags": flags if flags else None,
                                "keywords": keywords if keywords else None,
                            }
                            yield metadata
                        except Exception as e:
                            # Log error but continue with other emails
                            logger.error(f"Error parsing email metadata: {e!s}")
                    else:
                        logger.error(f"Could not find header data in response for email ID: {email_id_str}")
                except Exception as e:
                    logger.error(f"Error fetching email metadata {email_id}: {e!s}")
        finally:
            # Ensure we logout properly
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    def _check_email_content(self, data: list) -> bool:
        """Check if the fetched data contains actual email content."""
        for item in data:
            if isinstance(item, bytes) and b"FETCH (" in item and b"RFC822" not in item and b"BODY" not in item:
                # This is just metadata, not actual content
                continue
            elif isinstance(item, bytes | bytearray) and len(item) > 100:
                # This looks like email content
                return True
        return False

    def _extract_raw_email(self, data: list) -> bytes | None:
        """Extract raw email bytes from IMAP response data."""
        # The email content is typically at index 1 as a bytearray
        if len(data) > 1 and isinstance(data[1], bytearray):
            return bytes(data[1])

        # Search through all items for email content
        for item in data:
            if isinstance(item, bytes | bytearray) and len(item) > 100:
                # Skip IMAP protocol responses
                if isinstance(item, bytes) and b"FETCH" in item:
                    continue
                # This is likely the email content
                return bytes(item) if isinstance(item, bytearray) else item
        return None

    async def _fetch_email_with_formats(self, imap, email_id: str) -> list | None:
        """Try different fetch formats to get email data. Uses PEEK to avoid marking as read."""
        fetch_formats = ["BODY.PEEK[]", "(BODY.PEEK[])", "RFC822", "BODY[]"]

        for fetch_format in fetch_formats:
            try:
                _, data = await imap.uid("fetch", email_id, fetch_format)

                if data and len(data) > 0 and self._check_email_content(data):
                    return data

            except Exception as e:
                logger.debug(f"Fetch format {fetch_format} failed: {e}")

        return None

    async def get_email_body_by_id(self, email_id: str, mailbox: str = "INBOX") -> dict[str, Any] | None:
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        try:
            await self._imap_connect_and_login(imap)
            try:
                await imap.id(name="mcp-email-server", version="1.0.0")
            except Exception as e:
                logger.warning(f"IMAP ID command failed: {e!s}")
            await imap.select(mailbox)

            # Fetch the specific email by UID
            data = await self._fetch_email_with_formats(imap, email_id)
            if not data:
                logger.error(f"Failed to fetch UID {email_id} with any format")
                return None

            # Fetch FLAGS separately
            flags = []
            keywords = []
            try:
                _, flags_data = await imap.uid("fetch", email_id, "(FLAGS)")
                if flags_data:
                    for item in flags_data:
                        if isinstance(item, bytes) and b"FLAGS" in item:
                            flags_match = re.search(rb"FLAGS\s*\(([^)]*)\)", item)
                            if flags_match:
                                flags_str = flags_match.group(1).decode("utf-8")
                                for flag in flags_str.split():
                                    if flag.startswith("\\"):
                                        flags.append(flag)
                                    elif flag and flag not in ("Recent",):
                                        keywords.append(flag)
            except Exception as e:
                logger.debug(f"Failed to fetch FLAGS for {email_id}: {e}")

            # Extract raw email data
            raw_email = self._extract_raw_email(data)
            if not raw_email:
                logger.error(f"Could not find email data in response for email ID: {email_id}")
                return None

            # Parse the email
            try:
                result = self._parse_email_data(raw_email, email_id)
                if result:
                    result["flags"] = flags if flags else None
                    result["keywords"] = keywords if keywords else None
                return result
            except Exception as e:
                logger.error(f"Error parsing email: {e!s}")
                return None

        finally:
            # Ensure we logout properly
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    async def download_attachment(
        self,
        email_id: str,
        attachment_name: str,
        save_path: str,
    ) -> dict[str, Any]:
        """Download a specific attachment from an email and save it to disk."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        try:
            await self._imap_connect_and_login(imap)
            try:
                await imap.id(name="mcp-email-server", version="1.0.0")
            except Exception as e:
                logger.warning(f"IMAP ID command failed: {e!s}")
            await imap.select("INBOX")

            data = await self._fetch_email_with_formats(imap, email_id)
            if not data:
                msg = f"Failed to fetch email with UID {email_id}"
                logger.error(msg)
                raise ValueError(msg)

            raw_email = self._extract_raw_email(data)
            if not raw_email:
                msg = f"Could not find email data for email ID: {email_id}"
                logger.error(msg)
                raise ValueError(msg)

            parser = BytesParser(policy=default)
            email_message = parser.parsebytes(raw_email)

            # Find the attachment
            attachment_data = None
            mime_type = None

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_disposition = str(part.get("Content-Disposition", ""))
                    if "attachment" in content_disposition:
                        filename = part.get_filename()
                        if filename == attachment_name:
                            attachment_data = part.get_payload(decode=True)
                            mime_type = part.get_content_type()
                            break

            if attachment_data is None:
                msg = f"Attachment '{attachment_name}' not found in email {email_id}"
                logger.error(msg)
                raise ValueError(msg)

            # Save to disk
            save_file = Path(save_path)
            save_file.parent.mkdir(parents=True, exist_ok=True)
            save_file.write_bytes(attachment_data)

            logger.info(f"Attachment '{attachment_name}' saved to {save_path}")

            return {
                "email_id": email_id,
                "attachment_name": attachment_name,
                "mime_type": mime_type or "application/octet-stream",
                "size": len(attachment_data),
                "saved_path": str(save_file.resolve()),
            }

        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

    def _validate_attachment(self, file_path: str) -> Path:
        """Validate attachment file path."""
        path = Path(file_path)
        if not path.exists():
            msg = f"Attachment file not found: {file_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)

        if not path.is_file():
            msg = f"Attachment path is not a file: {file_path}"
            logger.error(msg)
            raise ValueError(msg)

        return path

    def _create_attachment_part(self, path: Path) -> MIMEApplication:
        """Create MIME attachment part from file."""
        with open(path, "rb") as f:
            file_data = f.read()

        mime_type, _ = mimetypes.guess_type(str(path))
        if mime_type is None:
            mime_type = "application/octet-stream"

        attachment_part = MIMEApplication(file_data, _subtype=mime_type.split("/")[1])
        attachment_part.add_header(
            "Content-Disposition",
            "attachment",
            filename=path.name,
        )
        logger.info(f"Attached file: {path.name} ({mime_type})")
        return attachment_part

    def _create_message_with_attachments(self, body: str, html: bool, attachments: list[str]) -> MIMEMultipart:
        """Create multipart message with attachments."""
        msg = MIMEMultipart()
        content_type = "html" if html else "plain"
        text_part = MIMEText(body, content_type, "utf-8")
        msg.attach(text_part)

        for file_path in attachments:
            try:
                path = self._validate_attachment(file_path)
                attachment_part = self._create_attachment_part(path)
                msg.attach(attachment_part)
            except Exception as e:
                logger.error(f"Failed to attach file {file_path}: {e}")
                raise

        return msg

    def _create_multipart_message(self, plain_text: str, html_content: str) -> MIMEMultipart:
        """Create a multipart/alternative message with plain text and HTML versions."""
        msg = MIMEMultipart("alternative")
        msg.attach(MIMEText(plain_text, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))
        return msg

    async def send_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        html: bool = False,
        attachments: list[str] | None = None,
        in_reply_to: str | None = None,
        references: str | None = None,
    ):
        # Parse frontmatter if present
        metadata, body_content = parse_frontmatter(body)

        # Use title from frontmatter if subject not provided
        if not subject and "title" in metadata:
            subject = metadata["title"]

        # Detect content type and prepare body
        if html:
            # Explicit HTML mode - use as-is
            plain_text = strip_html_tags(body_content)
            html_content = body_content
            use_multipart = True
        else:
            # Auto-detect content type
            content_type = detect_content_type(body_content)
            if content_type == "markdown":
                plain_text = body_content
                html_content = convert_markdown_to_html(body_content)
                use_multipart = True
            elif content_type == "html":
                plain_text = strip_html_tags(body_content)
                html_content = body_content
                use_multipart = True
            else:
                # Plain text
                plain_text = body_content
                html_content = None
                use_multipart = False

        # Create message
        if attachments:
            # For attachments, create mixed multipart with body as first part
            msg = MIMEMultipart("mixed")
            if use_multipart:
                body_part = self._create_multipart_message(plain_text, html_content)
            else:
                body_part = MIMEText(plain_text, "plain", "utf-8")
            msg.attach(body_part)
            # Add attachments
            for file_path in attachments:
                path = self._validate_attachment(file_path)
                attachment_part = self._create_attachment_part(path)
                msg.attach(attachment_part)
        elif use_multipart:
            msg = self._create_multipart_message(plain_text, html_content)
        else:
            msg = MIMEText(plain_text, "plain", "utf-8")

        # Handle subject with special characters
        if any(ord(c) > 127 for c in subject):
            msg["Subject"] = Header(subject, "utf-8")
        else:
            msg["Subject"] = subject

        # Handle sender name with special characters
        sender_name, sender_email = email.utils.parseaddr(self.sender)
        if sender_name and any(ord(c) > 127 for c in sender_name):
            sender_name = Header(sender_name, "utf-8").encode()
        msg["From"] = email.utils.formataddr((sender_name, sender_email))

        msg["To"] = ", ".join(recipients)

        # Add CC header if provided (visible to recipients)
        if cc:
            msg["Cc"] = ", ".join(cc)

        # Set threading headers for replies
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        # Note: BCC recipients are not added to headers (they remain hidden)
        # but will be included in the actual recipients for SMTP delivery

        async with aiosmtplib.SMTP(
            hostname=self.email_server.host,
            port=self.email_server.port,
            start_tls=self.smtp_start_tls,
            use_tls=self.smtp_use_tls,
        ) as smtp:
            await smtp.login(self.email_server.user_name, self.email_server.password)

            # Create a combined list of all recipients for delivery
            all_recipients = recipients.copy()
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)

            await smtp.send_message(msg, recipients=all_recipients)

        # Return the message for potential saving to Sent folder
        return msg

    async def append_to_sent(
        self,
        msg: MIMEText | MIMEMultipart,
        incoming_server: EmailServer,
        sent_folder_name: str | None = None,
    ) -> bool:
        """Append a sent message to the IMAP Sent folder.

        Args:
            msg: The email message that was sent
            incoming_server: IMAP server configuration for accessing Sent folder
            sent_folder_name: Override folder name, or None for auto-detection

        Returns:
            True if successfully saved, False otherwise
        """
        imap_class = aioimaplib.IMAP4_SSL if incoming_server.use_ssl else aioimaplib.IMAP4
        imap = imap_class(incoming_server.host, incoming_server.port)

        # Common Sent folder names across different providers
        sent_folder_candidates = [
            sent_folder_name,  # User-specified override (if provided)
            "Sent",
            "INBOX.Sent",
            "Sent Items",
            "Sent Mail",
            "[Gmail]/Sent Mail",
            "INBOX/Sent",
        ]
        # Filter out None values
        sent_folder_candidates = [f for f in sent_folder_candidates if f]

        try:
            await self._imap_connect_and_login(imap, incoming_server)

            # Try to find and use the Sent folder
            for folder in sent_folder_candidates:
                try:
                    logger.debug(f"Trying Sent folder: '{folder}'")
                    # Try to select the folder to verify it exists
                    result = await imap.select(folder)
                    logger.debug(f"Select result for '{folder}': {result}")

                    # aioimaplib returns (status, data) where status is a string like 'OK' or 'NO'
                    status = result[0] if isinstance(result, tuple) else result
                    if str(status).upper() == "OK":
                        # Folder exists, append the message
                        msg_bytes = msg.as_bytes()
                        logger.debug(f"Appending message to '{folder}'")
                        # aioimaplib.append signature: (message_bytes, mailbox, flags, date)
                        append_result = await imap.append(
                            msg_bytes,
                            mailbox=folder,
                            flags=r"(\Seen)",
                        )
                        logger.debug(f"Append result: {append_result}")
                        append_status = append_result[0] if isinstance(append_result, tuple) else append_result
                        if str(append_status).upper() == "OK":
                            logger.info(f"Saved sent email to '{folder}'")
                            return True
                        else:
                            logger.warning(f"Failed to append to '{folder}': {append_status}")
                    else:
                        logger.debug(f"Folder '{folder}' select returned: {status}")
                except Exception as e:
                    logger.debug(f"Folder '{folder}' not available: {e}")
                    continue

            logger.warning("Could not find a valid Sent folder to save the message")
            return False

        except Exception as e:
            logger.error(f"Error saving to Sent folder: {e}")
            return False
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.debug(f"Error during logout: {e}")

    async def delete_emails(self, email_ids: list[str], mailbox: str = "INBOX") -> tuple[list[str], list[str]]:
        """Delete emails by their UIDs. Returns (deleted_ids, failed_ids)."""
        imap = self.imap_class(self.email_server.host, self.email_server.port)
        deleted_ids = []
        failed_ids = []

        try:
            await self._imap_connect_and_login(imap)
            await imap.select(mailbox)

            for email_id in email_ids:
                try:
                    await imap.uid("store", email_id, "+FLAGS", r"(\Deleted)")
                    deleted_ids.append(email_id)
                except Exception as e:
                    logger.error(f"Failed to delete email {email_id}: {e}")
                    failed_ids.append(email_id)

            await imap.expunge()
        finally:
            try:
                await imap.logout()
            except Exception as e:
                logger.info(f"Error during logout: {e}")

        return deleted_ids, failed_ids


class ClassicEmailHandler(EmailHandler):
    def __init__(self, email_settings: EmailSettings):
        self.email_settings = email_settings
        self.incoming_client = EmailClient(email_settings.incoming)
        self.outgoing_client = EmailClient(
            email_settings.outgoing,
            sender=f"{email_settings.full_name} <{email_settings.email_address}>",
        )
        self.save_to_sent = email_settings.save_to_sent
        self.sent_folder_name = email_settings.sent_folder_name

    async def get_emails_metadata(
        self,
        page: int = 1,
        page_size: int = 10,
        before: datetime | None = None,
        since: datetime | None = None,
        subject: str | None = None,
        from_address: str | None = None,
        to_address: str | None = None,
        order: str = "desc",
        mailbox: str = "INBOX",
    ) -> EmailMetadataPageResponse:
        emails = []
        async for email_data in self.incoming_client.get_emails_metadata_stream(
            page, page_size, before, since, subject, from_address, to_address, order, mailbox
        ):
            emails.append(EmailMetadata.from_email(email_data))
        total = await self.incoming_client.get_email_count(
            before, since, subject, from_address=from_address, to_address=to_address, mailbox=mailbox
        )
        return EmailMetadataPageResponse(
            page=page,
            page_size=page_size,
            before=before,
            since=since,
            subject=subject,
            emails=emails,
            total=total,
        )

    async def get_emails_content(self, email_ids: list[str], mailbox: str = "INBOX") -> EmailContentBatchResponse:
        """Batch retrieve email body content"""
        emails = []
        failed_ids = []

        for email_id in email_ids:
            try:
                email_data = await self.incoming_client.get_email_body_by_id(email_id, mailbox)
                if email_data:
                    emails.append(
                        EmailBodyResponse(
                            email_id=email_data["email_id"],
                            message_id=email_data.get("message_id"),
                            subject=email_data["subject"],
                            sender=email_data["from"],
                            recipients=email_data["to"],
                            date=email_data["date"],
                            body=email_data["body"],
                            attachments=email_data["attachments"],
                            flags=email_data.get("flags"),
                            keywords=email_data.get("keywords"),
                        )
                    )
                else:
                    failed_ids.append(email_id)
            except Exception as e:
                logger.error(f"Failed to retrieve email {email_id}: {e}")
                failed_ids.append(email_id)

        return EmailContentBatchResponse(
            emails=emails,
            requested_count=len(email_ids),
            retrieved_count=len(emails),
            failed_ids=failed_ids,
        )

    async def send_email(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        html: bool = False,
        attachments: list[str] | None = None,
        in_reply_to: str | None = None,
        references: str | None = None,
    ) -> None:
        msg = await self.outgoing_client.send_email(
            recipients, subject, body, cc, bcc, html, attachments, in_reply_to, references
        )

        # Save to Sent folder if enabled
        if self.save_to_sent and msg:
            await self.outgoing_client.append_to_sent(
                msg,
                self.email_settings.incoming,
                self.sent_folder_name,
            )

    async def delete_emails(self, email_ids: list[str], mailbox: str = "INBOX") -> tuple[list[str], list[str]]:
        """Delete emails by their UIDs. Returns (deleted_ids, failed_ids)."""
        return await self.incoming_client.delete_emails(email_ids, mailbox)

    async def download_attachment(
        self,
        email_id: str,
        attachment_name: str,
        save_path: str,
    ) -> AttachmentDownloadResponse:
        """Download an email attachment and save it to the specified path."""
        result = await self.incoming_client.download_attachment(email_id, attachment_name, save_path)
        return AttachmentDownloadResponse(
            email_id=result["email_id"],
            attachment_name=result["attachment_name"],
            mime_type=result["mime_type"],
            size=result["size"],
            saved_path=result["saved_path"],
        )

    async def get_unread(self, max_ids: int = 20) -> dict:
        """Get unread emails count and IDs with category breakdown."""
        return await self.incoming_client.get_unread(max_ids)

    async def mark_as_read(self, email_ids: list[str], mailbox: str = "INBOX") -> tuple[list[str], list[str]]:
        """Mark emails as read. Returns (marked_ids, failed_ids)."""
        return await self.incoming_client.mark_as_read(email_ids, mailbox)

    async def mark_as_unread(self, email_ids: list[str], mailbox: str = "INBOX") -> tuple[list[str], list[str]]:
        """Mark emails as unread. Returns (marked_ids, failed_ids)."""
        return await self.incoming_client.mark_as_unread(email_ids, mailbox)

    async def get_flagged_emails(self, keyword: str | None = None, mailbox: str = "INBOX") -> dict[str, Any]:
        """Get flagged emails, optionally filtered by keyword."""
        return await self.incoming_client.get_flagged_emails(keyword, mailbox)

    async def set_flags(
        self, email_ids: list[str], flags: list[str], mailbox: str = "INBOX"
    ) -> tuple[list[str], list[str]]:
        """Add flags/keywords to emails. Returns (success_ids, failed_ids)."""
        return await self.incoming_client.set_flags(email_ids, flags, mailbox)

    async def remove_flags(
        self, email_ids: list[str], flags: list[str], mailbox: str = "INBOX"
    ) -> tuple[list[str], list[str]]:
        """Remove flags/keywords from emails. Returns (success_ids, failed_ids)."""
        return await self.incoming_client.remove_flags(email_ids, flags, mailbox)
