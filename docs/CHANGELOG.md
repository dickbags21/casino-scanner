# Changelog

All notable changes to the Casino Scanner project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Terminal interface in dashboard
- Command palette (Ctrl+U/Ctrl+K)
- Enhanced browser plugin with instance management
- Keyboard shortcuts throughout dashboard
- Node-RED automation integration
- Webhook endpoints for automation triggers
- Comprehensive .gitignore
- Architecture documentation
- Project cleanup and organization

### Changed
- Consolidated entry points (deprecated main.py)
- Moved unused scripts to archive/
- Organized documentation into docs/ folder
- Improved project structure

### Fixed
- Browser plugin instance management
- Terminal command execution
- Command palette navigation

## [1.0.0] - 2025-01-XX

### Added
- Initial web dashboard release
- FastAPI backend with REST API
- WebSocket support for real-time updates
- Plugin system with 4 plugins (Browser, Shodan, Account Creation, Mobile App)
- SQLite database for scan history
- Target management system
- Vulnerability tracking
- Dark mode support
- Chart visualizations
- Export functionality

### Changed
- Migrated from CLI-only to web-based interface
- Unified multiple scanner tools into plugin architecture

## [0.9.0] - Pre-release

### Added
- Browser automation scanner
- Shodan integration
- Account creation vulnerability scanner
- Mobile app scanner
- Continuous scanning system
- Target discovery automation
- Vulnerability classification
- Alert system

