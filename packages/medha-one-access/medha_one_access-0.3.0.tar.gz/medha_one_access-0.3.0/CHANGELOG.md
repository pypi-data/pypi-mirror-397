# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-12-16

### Added
- **Fully Configurable Library**: Expanded `LibraryConfig` with 40+ configurable parameters
- **Custom Environment Prefix**: Configure `env_prefix` to use any prefix for environment variables (default: `MEDHA_`)
- **Custom API Prefix**: Configure `api_prefix` to mount routes under any path (default: `/access`)
- **YAML/JSON Configuration**: Load configuration from YAML or JSON files using `LibraryConfig.from_file()`
- **Combined Configuration**: Use `LibraryConfig.from_env_or_file()` to load from file with environment overrides
- **Configurable Cache Settings**: Full control over cache sizes and TTLs for global, expression, and user access caches
- **Configurable Background Tasks**: Control worker count, queue size, timeouts, and cleanup settings
- **Configurable Database Pool**: Set pool size, overflow, recycle time, pre-ping, JIT, and timeouts
- **CacheManager**: New centralized cache management with `configure_caches()` function
- **Security Documentation**: Added `SECURITY.md` and `docs/security.md` with best practices
- **Troubleshooting Guide**: Added `docs/troubleshooting.md` for common issues
- **Configuration Reference**: Added `docs/configuration.md` with all parameters documented
- **Custom Config Examples**: New `examples/custom_config.py` with 8 configuration scenarios
- **Sample YAML Config**: Added `examples/config.example.yaml` template

### Changed
- **Controller Initialization**: Both `AccessController` and `AsyncAccessController` now use `from_config()` methods for components
- **Database Manager**: Uses config for all pool settings via `AsyncDatabaseManager.from_config()`
- **Task Manager**: Uses config for all worker settings via `AsyncBackgroundTaskManager.from_config()`
- **Cache System**: All caches now initialized via `configure_caches(config)`
- **Documentation**: Reorganized and sanitized all documentation for public use
- **README**: Updated with configuration section and improved examples

### Removed
- Internal documentation files (`EXECUTE_SETUP.md`, `GIT_SETUP_GUIDE.md`, `INSTALLATION_TESTS.md`, `PUBLISH.md`, `ANALYSIS.md`, `PROJECT_SUMMARY.md`)
- Internal/private Git repository installation instructions
- Hardcoded configuration values throughout the codebase

### Technical Details
- All hardcoded values in `cache.py` replaced with config parameters
- All hardcoded values in `background_tasks.py` replaced with config parameters
- All hardcoded values in `database.py` replaced with config parameters
- Controller properly wires config to all components on initialization
- Backward compatible - existing code using defaults continues to work

### Migration
- **No Breaking Changes**: All existing code continues to work with default values
- **Optional Upgrade**: Use new configuration parameters for customization
- **Environment Variables**: Existing `MEDHA_*` variables still work as default
- **New Feature**: Add `yaml` optional dependency for YAML config support: `pip install medha-one-access[yaml]`

## [0.2.2] - 2025-08-26

### Fixed
- **Expression Validation**: Added support for additional common characters in entity names:
  - Colons `:` (e.g., `"Entity: Test"`)
  - Commas `,` (e.g., `"Entity, Demo"`) 
  - Apostrophes `'` (e.g., `"FD's Snapshot"`)
- **Character Validation**: Updated allowed character set for comprehensive entity name support

### Changed
- **Validation Regex**: Enhanced pattern to: `r"[^a-zA-Z0-9_+\-|.\s@&#\"():,']"`
- **Error Messages**: Updated to include colons, commas, and apostrophes in allowed characters list

## [0.2.1] - 2025-08-26

### Fixed
- **Expression Validation**: Added support for parentheses `()` in entity names (e.g., `"Manpower Budget (Input to Finance) FY26"`)
- **Character Validation**: Updated allowed character set to include parentheses for entity names with brackets

### Changed
- **Validation Regex**: Updated validation pattern to allow parentheses: `r'[^a-zA-Z0-9_+\-|.\s@&#"()]'`
- **Error Messages**: Updated validation error messages to include parentheses in allowed characters list

## [0.2.0] - 2025-08-26

### Added
- **Quoted Entity Support**: Added support for quoted entities in expressions to handle entity names with hyphens and special characters
- **Enhanced Expression Validation**: Added validation for properly matched quotes in expressions

### Fixed
- **Critical Expression Parsing Bug**: Fixed major bug where entity IDs containing hyphens (e.g., `user-service-api`) were incorrectly parsed as mathematical operations
- **Expression Validation**: Updated validation to allow quotes in expressions while maintaining security

### Changed
- **Expression Parser**: Updated core expression parsing regex to support quoted entities: `"entity-with-hyphens"`
- **Backward Compatibility**: Maintained 100% compatibility with existing unquoted expressions

### Technical Details
- Updated `ExpressionParser.parse_expression()` regex pattern to: `r'([+-]?)(".*?"|[^+-]+)'`
- Added automatic quote stripping in token processing
- Enhanced `validate_expression()` to check for unmatched quotes
- Updated allowed character validation to include quote characters

### Migration
- **No Breaking Changes**: All existing expressions continue to work unchanged
- **New Feature**: Entities with special characters can now be quoted for proper parsing
- **Examples**: 
  - Old (broken): `user-service-api+admin-panel` 
  - New (working): `"user-service-api"+"admin-panel"`
  - Still works: `simpleuser+basicgroup`

## [0.1.1] - 2025-08-25

### Fixed
- **Pagination Defaults**: Fixed hardcoded 100-record limits in all list methods (list_users, list_artifacts, list_access_rules)
- **User Group Resolution**: Fixed `get_usergroup_members` method to use correct `resolve_user_expression` method instead of non-existent `resolve_expression`
- **Query Optimization**: Updated all list methods to support optional limit parameter for unlimited record loading

### Changed
- **list_users()**: Changed limit parameter from `int = 100` to `Optional[int] = None`
- **list_artifacts()**: Changed limit parameter from `int = 100` to `Optional[int] = None` 
- **list_access_rules()**: Changed limit parameter from `int = 100` to `Optional[int] = None`
- **Query Logic**: Added conditional query execution to apply limit only when specified

## [0.1.0] - 2025-08-19

### Added
- Initial release of Access Control Library
- BODMAS-based access resolution engine with 4-step priority system
- Expression-based user and resource grouping with + (include) and - (exclude) operators
- Time-based access constraints (date ranges, time windows, day-of-week restrictions)
- Comprehensive audit trails for access decisions
- SQLAlchemy models and Pydantic schemas for all entities
- Database management with Alembic migrations
- AccessController class providing clean Python API
- CLI tools for database management, data import/export, and access checking
- FastAPI integration module for optional web APIs
- Complete test suite with fixtures and examples
- Type hints and py.typed marker for full typing support
- Support for PostgreSQL and SQLite databases
- Hierarchical organization structures
- Context managers for database sessions
- Expression validation and error handling

### Supported Features
- **User Management**: Create individual users and user groups with expressions
- **Resource Management**: Create individual resources and resource groups with expressions
- **Access Rules**: Define flexible access rules with user/resource expressions and permissions
- **Time Constraints**: Apply temporal restrictions to access rules
- **BODMAS Resolution**: Mathematical precedence-based access resolution
- **Audit Trails**: Detailed logging of access resolution steps
- **CLI Interface**: Command-line tools for all operations
- **REST API**: Optional FastAPI integration for web services
- **Database Support**: PostgreSQL (recommended) and SQLite
- **Migration Support**: Alembic-based database schema management

### Technical Specifications
- Python 3.8+ support
- SQLAlchemy 2.0+ with async support
- Pydantic v2 for data validation
- FastAPI for optional web API
- Click for CLI interface
- Comprehensive test coverage
- Type hints throughout
- Modern Python packaging (pyproject.toml)

## [Unreleased]

### Planned Features
- Redis caching for improved performance
- Webhook notifications for access events
- LDAP/Active Directory integration
- Role-based access control (RBAC) helpers
- Attribute-based access control (ABAC) extensions
- GraphQL API support
- Performance optimizations and query optimization
- Additional database backend support (MySQL, MongoDB)
- Docker containerization
- Kubernetes deployment examples