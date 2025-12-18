# Changelog

All notable changes to the EnkaliPrime Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-17

### Added

- Initial release of the EnkaliPrime Python SDK
- `EnkaliPrimeClient` class for interacting with the EnkaliPrime Chat API
- Support for synchronous and asynchronous operations
- Streaming response support with callbacks
- Session management (create, end, get)
- Conversation history management
- Full type hints and PEP 561 compliance
- Data models:
  - `ChatMessage`
  - `ChatSession`
  - `ResolvedConnection`
  - `ChatApiConfig`
  - `ChatRequest`
- Custom exceptions:
  - `EnkaliPrimeError`
  - `ConnectionError`
  - `AuthenticationError`
  - `APIError`
  - `StreamingError`
  - `ValidationError`
  - `SessionError`
- Context manager support for resource cleanup
- Comprehensive test suite
- Examples for:
  - Basic usage
  - Streaming responses
  - Async operations
  - Interactive CLI chat
  - FastAPI integration
- Documentation with API reference and usage examples

### Security

- Secure API key handling
- HTTPS-only communication
- No sensitive data logging

---

## [Unreleased]

### Planned

- Retry logic with exponential backoff
- Webhook support for push notifications
- Built-in rate limiting
- Local caching for conversation history
- More framework integrations (Django, Flask blueprints)

