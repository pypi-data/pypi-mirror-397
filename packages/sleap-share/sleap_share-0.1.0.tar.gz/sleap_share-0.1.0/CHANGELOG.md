# Changelog

All notable changes to the `sleap-share` Python client will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2024-12-19

### Added

- Initial release of the `sleap-share` Python client
- **CLI Commands**
  - `sleap-share login` - Device authorization flow with browser authentication
  - `sleap-share logout` - Clear stored credentials
  - `sleap-share whoami` - Show current authenticated user
  - `sleap-share upload <file>` - Upload .slp files with progress bar
  - `sleap-share download <shortcode>` - Download files by shortcode or URL
  - `sleap-share list` - List your uploaded files in a table
  - `sleap-share info <shortcode>` - Show file metadata (with `--json` option)
  - `sleap-share preview <shortcode>` - Download preview image
  - `sleap-share delete <shortcode>` - Delete files you own
  - `sleap-share version` - Show version information
- **Python API**
  - `sleap_share.upload()` - Upload files programmatically
  - `sleap_share.download()` - Download files programmatically
  - `sleap_share.get_info()` - Get basic file information
  - `sleap_share.get_metadata()` - Get full metadata including SLP statistics
  - `sleap_share.get_preview()` - Download preview images
  - `sleap_share.get_urls()` - Get all URLs for a shortcode
  - `sleap_share.get_download_url()` - Get direct download URL
  - `sleap_share.get_preview_url()` - Get preview image URL
  - `sleap_share.open()` - Get URL for lazy loading with HTTP range requests
  - `sleap_share.Client` - Full-featured client class for authenticated operations
- **Authentication**
  - OAuth 2.0 Device Authorization Grant for CLI login
  - Secure token storage via system keyring (macOS Keychain, Windows Credential Manager, Linux Secret Service)
  - File-based fallback with secure permissions (0600)
- **Environment Support**
  - Target production (`slp.sh`) or staging (`staging.slp.sh`) environments
  - Configure via `--env` flag or `SLEAP_SHARE_ENV` environment variable
- **Lazy Loading**
  - All download URLs support HTTP range requests
  - Compatible with h5py ros3 driver, fsspec, and sleap-io for streaming access
  - Access file contents without downloading the entire file

### Dependencies

- `httpx` - Modern HTTP client with streaming support
- `typer` - CLI framework with type hints
- `rich` - Terminal output with progress bars and tables
- `platformdirs` - Cross-platform configuration directories
- `keyring` (optional) - Secure credential storage
- `fsspec` (optional) - Lazy loading support

[Unreleased]: https://github.com/talmolab/sleap-share/compare/client-v0.1.0...HEAD
[0.1.0]: https://github.com/talmolab/sleap-share/releases/tag/client-v0.1.0
