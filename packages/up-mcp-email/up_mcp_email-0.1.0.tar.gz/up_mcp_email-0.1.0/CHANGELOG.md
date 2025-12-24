# Changelog - up-mcp-email

Fork de [mcp-email-server](https://github.com/ai-zerolab/mcp-email-server) con mejoras para ultraPRO.

## [Unreleased]

### Added
- Sistema de permisos CRUDLEX por cuenta (CREATE, READ, UPDATE, DELETE, LIST, EXPORT, EXECUTE)
- `update_account_permissions` tool - modificar permisos de cuentas
- `check_unread` tool - resumen de emails no leídos por categoría
- `mark_as_read` tool - marcar emails como leídos sin obtener contenido
- `mark_as_unread` tool - marcar emails como no leídos
- `list_flagged` tool - listar emails con flag, agrupados por keyword
- `set_flag` tool - agregar flags/keywords a emails
- `remove_flag` tool - quitar flags/keywords de emails
- `update_email_account` tool - actualizar password y/o full_name de una cuenta
- Campos `flags` y `keywords` en metadata de emails
- Auto-detección Markdown → HTML en `send_email`
- Tamaño de emails (`size_bytes`, `size_human`) en `check_unread` y `list_emails_metadata`
- Tiempo de ejecución y remitente en respuesta de `send_email`
- `get_emails_content` usa PEEK (no marca como leído automáticamente)

### Fixed
- Encoding correcto de nombres con caracteres especiales en header From
- TimeoutError en conexiones IMAP ahora muestra mensajes descriptivos (nueva clase `IMAPConnectionError`)

### Docs
- Security audit document
