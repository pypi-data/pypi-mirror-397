# Changelog

All notable changes to pyWATS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0b2] - 2025-12-15

### Changed

- **Architecture Refactoring** - Internal API separation
  - All internal endpoint implementations now in separate `_internal` files
  - New `AssetRepositoryInternal` and `AssetServiceInternal` for file operations
  - New `ProductionRepositoryInternal` and `ProductionServiceInternal` for MES operations
  - Public repositories delegate to internal repositories for internal endpoints
  - Added `api.asset_internal` for asset file operations (upload, download, list, delete)
  - Added `api.production_internal` for MES unit phases

### Fixed

- CompOp export path handling for None values
- TestInstanceConfig field mapping for process_code/test_operation

## [0.1.0b1] - 2025-12-14

### Added

- **pyWATS API Library** (`pywats`)
  - Product management (get, create, update products and revisions)
  - Asset management (equipment tracking, calibration, maintenance)
  - Report submission and querying (UUT/UUR reports in WSJF format)
  - Production/serial number management (units, batches, assemblies)
  - RootCause ticket system (issue tracking and resolution)
  - Software distribution (package management, releases)
  - Statistics and analytics endpoints
  - Station concept for multi-station deployments

- **pyWATS Client Application** (`pywats_client`)
  - Desktop GUI mode (PySide6/Qt)
  - Headless mode for servers and embedded systems (Raspberry Pi)
  - Connection management with encrypted token storage
  - Converter framework for custom file format processing
  - Report queue with offline support
  - HTTP control API for remote management

- **Developer Features**
  - Comprehensive type hints throughout
  - Pydantic models for data validation
  - Structured logging with debug mode
  - Async-ready architecture

### Requirements

- Python 3.8 or later
- **WATS Server 2025.3.9.824 or later**

### Notes

This is a **beta release**. The API is stabilizing but may have breaking changes
before the 1.0 release. Please report issues on GitHub.

---

## Version History

| Version | Date | Status |
|---------|------|--------|
| 0.1.0b2 | 2025-12-15 | Beta - Architecture refactoring |
| 0.1.0b1 | 2025-12-14 | Beta - Initial public release |
