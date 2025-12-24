# up-mcp-email

IMAP and SMTP via MCP Server

## Origin

This is a fork of [mcp-email-server](https://github.com/ai-zerolab/mcp-email-server) by [ai-zerolab](https://github.com/ai-zerolab).

**Fork maintainer:** [ultraBASE.net](https://ultrabase.net)

A security audit was performed before integrating this codebase. See [SECURITY-AUDIT.md](SECURITY-AUDIT.md) for details.

## Fork Enhancements

Features added by ultraBASE to the original mcp-email-server:

| Feature | Description |
|---------|-------------|
| **CRUDLEX Permissions** | Granular per-account permissions (CREATE, READ, UPDATE, DELETE, LIST, EXPORT, EXECUTE) |
| **`check_unread`** | Summary of unread emails by category with size info |
| **`mark_as_read` / `mark_as_unread`** | Explicit read status control |
| **`list_flagged` / `set_flag` / `remove_flag`** | Email flags and keywords management |
| **`update_email_account`** | Update account password and display name |
| **PEEK mode** | `get_emails_content` doesn't mark emails as read |
| **Markdown auto-detection** | Auto-convert Markdown to HTML in `send_email` |
| **Email sizes** | `size_bytes` and `size_human` in metadata responses |
| **Elapsed time** | Execution time in `send_email` response |
| **Better error handling** | `IMAPConnectionError` with descriptive messages |

See [CHANGELOG.md](CHANGELOG.md) for full history.

---

## Installation

### Manual Installation

We recommend using [uv](https://github.com/astral-sh/uv) to manage your environment.

Clone this repository and install:

```bash
git clone https://github.com/ultraBASE/up-mcp-email.git
cd up-mcp-email
uv sync
```

Configure for your MCP client:

```json
{
  "mcpServers": {
    "up-mcp-email": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/up-mcp-email", "mcp-email-server", "stdio"]
    }
  }
}
```

### Environment Variable Configuration

You can configure the email server using environment variables, which is particularly useful for CI/CD environments. Environment variables take precedence over TOML configuration.

```json
{
  "mcpServers": {
    "up-mcp-email": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/up-mcp-email", "mcp-email-server", "stdio"],
      "env": {
        "MCP_EMAIL_SERVER_ACCOUNT_NAME": "work",
        "MCP_EMAIL_SERVER_FULL_NAME": "John Doe",
        "MCP_EMAIL_SERVER_EMAIL_ADDRESS": "john@example.com",
        "MCP_EMAIL_SERVER_USER_NAME": "john@example.com",
        "MCP_EMAIL_SERVER_PASSWORD": "your_password",
        "MCP_EMAIL_SERVER_IMAP_HOST": "imap.gmail.com",
        "MCP_EMAIL_SERVER_IMAP_PORT": "993",
        "MCP_EMAIL_SERVER_SMTP_HOST": "smtp.gmail.com",
        "MCP_EMAIL_SERVER_SMTP_PORT": "465"
      }
    }
  }
}
```

#### Available Environment Variables

| Variable                                      | Description                                      | Default       | Required |
| --------------------------------------------- | ------------------------------------------------ | ------------- | -------- |
| `MCP_EMAIL_SERVER_ACCOUNT_NAME`               | Account identifier                               | `"default"`   | No       |
| `MCP_EMAIL_SERVER_FULL_NAME`                  | Display name                                     | Email prefix  | No       |
| `MCP_EMAIL_SERVER_EMAIL_ADDRESS`              | Email address                                    | -             | Yes      |
| `MCP_EMAIL_SERVER_USER_NAME`                  | Login username                                   | Same as email | No       |
| `MCP_EMAIL_SERVER_PASSWORD`                   | Email password                                   | -             | Yes      |
| `MCP_EMAIL_SERVER_IMAP_HOST`                  | IMAP server host                                 | -             | Yes      |
| `MCP_EMAIL_SERVER_IMAP_PORT`                  | IMAP server port                                 | `993`         | No       |
| `MCP_EMAIL_SERVER_IMAP_SSL`                   | Enable IMAP SSL                                  | `true`        | No       |
| `MCP_EMAIL_SERVER_SMTP_HOST`                  | SMTP server host                                 | -             | Yes      |
| `MCP_EMAIL_SERVER_SMTP_PORT`                  | SMTP server port                                 | `465`         | No       |
| `MCP_EMAIL_SERVER_SMTP_SSL`                   | Enable SMTP SSL                                  | `true`        | No       |
| `MCP_EMAIL_SERVER_SMTP_START_SSL`             | Enable STARTTLS                                  | `false`       | No       |
| `MCP_EMAIL_SERVER_ENABLE_ATTACHMENT_DOWNLOAD` | Enable attachment download                       | `false`       | No       |
| `MCP_EMAIL_SERVER_SAVE_TO_SENT`               | Save sent emails to IMAP Sent folder             | `true`        | No       |
| `MCP_EMAIL_SERVER_SENT_FOLDER_NAME`           | Custom Sent folder name (auto-detect if not set) | -             | No       |

For separate IMAP/SMTP credentials:

- `MCP_EMAIL_SERVER_IMAP_USER_NAME` / `MCP_EMAIL_SERVER_IMAP_PASSWORD`
- `MCP_EMAIL_SERVER_SMTP_USER_NAME` / `MCP_EMAIL_SERVER_SMTP_PASSWORD`

### Enabling Attachment Downloads

By default, downloading email attachments is disabled for security reasons. To enable:

**Environment Variable:**

```json
{
  "env": {
    "MCP_EMAIL_SERVER_ENABLE_ATTACHMENT_DOWNLOAD": "true"
  }
}
```

**TOML Configuration** (`~/.config/zerolib/mcp_email_server/config.toml`):

```toml
enable_attachment_download = true

[[emails]]
# ... your email configuration
```

### Saving Sent Emails to IMAP Sent Folder

By default, sent emails are automatically saved to your IMAP Sent folder.

The server auto-detects common Sent folder names: `Sent`, `INBOX.Sent`, `Sent Items`, `Sent Mail`, `[Gmail]/Sent Mail`.

To specify a custom folder or disable:

```toml
[[emails]]
account_name = "work"
save_to_sent = true          # or false to disable
sent_folder_name = "INBOX.Sent"
```

---

## Usage

### Reading Emails Without Marking as Read

The `get_emails_content` tool fetches email content **without marking emails as read**. This gives you full control over read status:

```python
# Fetch emails - they remain unread
emails = await get_emails_content(account_name="work", email_ids=["123", "456"])

# Explicitly mark as read when you're done
await mark_as_read(account_name="work", email_ids=["123", "456"])

# Or mark back as unread if needed
await mark_as_unread(account_name="work", email_ids=["123"])
```

### Replying to Emails

To reply to an email with proper threading:

```python
emails = await get_emails_content(account_name="work", email_ids=["123"])
original = emails.emails[0]

await send_email(
    account_name="work",
    recipients=[original.sender],
    subject=f"Re: {original.subject}",
    body="Thank you for your email...",
    in_reply_to=original.message_id,
    references=original.message_id,
)
```

### Checking Unread Emails

```python
result = await check_unread(account_name="work")
# Returns: total_unread, total_count, and breakdown by category (INBOX, SOCIAL, PROMOTIONS, etc.)
# Each unread email includes size_bytes and size_human for context estimation
```

### Markdown Auto-Detection

When sending emails, Markdown content is automatically detected and converted to HTML:

```python
await send_email(
    account_name="work",
    recipients=["user@example.com"],
    subject="Update",
    body="# Hello\n\nThis is **bold** and this is *italic*.",
)
# Markdown is auto-detected and converted to HTML
```

### CRUDLEX Permissions

Each email account has granular permissions:

| Permission | Operations |
|------------|------------|
| **C**reate | Create drafts (future) |
| **R**ead | Read email content (`get_emails_content`) |
| **U**pdate | Modify metadata (`mark_as_read`, `mark_as_unread`) |
| **D**elete | Delete emails (`delete_emails`) |
| **L**ist | List emails (`list_emails_metadata`, `check_unread`) |
| **E**xport | Download attachments (`download_attachment`) |
| e**X**ecute | Send emails (`send_email`) |

```python
await update_account_permissions(
    account_name="work",
    permissions="CREATE|READ|UPDATE|LIST|EXPORT"  # No DELETE, no EXECUTE
)
```

**Permission aliases:** `FULL`, `READONLY`, `SAFE`, `NO_SEND`, `NO_DELETE`

### Email Flags and Keywords

```python
# List flagged emails
result = await list_flagged(account_name="work")
result = await list_flagged(account_name="work", keyword="Personal")

# Add flags/keywords
await set_flag(account_name="work", email_ids=["123"], flags=["\\Flagged"])
await set_flag(account_name="work", email_ids=["123"], flags=["Personal", "Alta"])

# Remove flags/keywords
await remove_flag(account_name="work", email_ids=["123"], flags=["\\Flagged"])
```

---

## Development

This project is managed using [uv](https://github.com/astral-sh/uv).

```bash
make install    # Install virtual environment and pre-commit hooks
uv run mcp-email-server   # Run for local development
make check      # Run linters/formatters
make test       # Run unit tests
```

---

## Upstream

- **Original repository:** https://github.com/ai-zerolab/mcp-email-server
- **Original documentation:** https://ai-zerolab.github.io/mcp-email-server/
