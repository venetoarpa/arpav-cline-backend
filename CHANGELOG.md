# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [2.0.5] - 2026-03-19

### Changed
- Disabled admin search builder for most views - it did not work

#### Fixed
- Fixed timeseries handling of empty datasets


## [2.0.4] - 2026-03-19

### Added
- Production deployment configuration file now accepts the additional `env_http_client_timeout_seconds` parameter,
  which allows customizing the timeout (in seconds) for the HTTP client. The default value is 30.0
- Implemented custom filtering for the admin section that works with Observation measurements

### Changed
- Translations are now compiled during the docker build process


## [2.0.3] - 2025-08-07

### Changed
- Made coords query param for time series downloads longer


## [2.0.2] - 2025-08-06

### Fixed
- Added missing historical coverage download detail


## [2.0.1] - 2025-06-30

### Fixed
- Corrected error handling on WMS proxy when THREDDS responds with malformed HTTP responses


## [2.0.0] - 2025-06-24

### Changed
- Complete refactor of system internals in order to simplify codebase and ease administration


## [2.0.0-rc1] - 2024-12-17

### Added

- Initial project restructuring and features


## 1.0.0 - ?

### Added

- Previous version, developed by a different team


[Unreleased]: https://github.com/geobeyond/arpav-cline-backend/compare/v2.0.5...HEAD
[2.0.5]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.4...v2.0.5
[2.0.4]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.3...v2.0.4
[2.0.3]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.2...v2.0.3
[2.0.2]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.1...v2.0.2
[2.0.1]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.0...v2.0.1
[2.0.0]: https://github.com/geobeyond/arpav-cline-backend/compare/2.0.0-rc1...v2.0.0
[2.0.0-rc1]: https://github.com/geobeyond/arpav-cline-backend/compare/v1.0.0-rc1...main
