# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-12-17

### Added

- Initial release
- `X402AsyncClient` - Async HTTP client with x402 v2 payment support
- `X402Client` - Sync HTTP client with x402 v2 payment support
- EIP-712 typed data signing for TransferWithAuthorization (EIP-3009)
- Support for reading payment requirements from `payment-required` header
- Debug mode for troubleshooting
- Full x402 v2 protocol compliance
