# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-12-17

### Changed
- Synchronized SDK with latest Bridge API changes
- Removed deprecated endpoints: `chats_archive`, `chats_unarchive`, `chats_unread`
- Removed standalone `send_list` endpoint (now handled via `send_message` with type 'list')
- Updated documentation: translated `README.md` and `QUICK_START.md` to English
- Enhanced `README.md` with comprehensive examples covering all endpoints
- Added complete example suite mirroring `noti-sdk-js` structure

### Added
- Complete example files organized by category (sessions, profile, chatting, status, chats, contacts)
- Examples for all message types: file, voice, video, poll, location, contact-vcard, list, link-preview, forward
- Examples for all status types: text, image, voice, video, delete
- Examples for all chat operations: get message, delete message, unpin message, overview POST
- Examples for contact operations: get about, block, unblock
- Section in README linking to examples directory

### Fixed
- SDK now matches Bridge API implementation exactly
- `send_list` functionality properly integrated into `send_message` endpoint
- All examples are now in English and reflect the latest API changes

## [1.0.0] - 2025-12-17

### Added
- Initial release
- Complete Python SDK for NotiBuzz Bridge
- Support for all Bridge endpoints:
  - Sessions management
  - Profile management
  - Chatting (text, image, file, voice, video, poll, location, contact, forward, list)
  - Status/Stories (text, image, voice, video, delete)
  - Chats management (overview, messages, read, edit, pin, unpin)
  - Contacts management
- Bulk messaging support with anti-ban controls
- Async message queuing
- Campaign control (stop, resume, availability check)
- Comprehensive documentation
- Examples for common use cases
- Automatic suppression of urllib3 OpenSSL warnings (macOS compatibility)

### Features
- Full Python support with type hints
- Clean and intuitive API
- Async/await support (via async_ parameter)
- Error handling with requests exceptions
- Request/response type safety
- Environment variable configuration support
