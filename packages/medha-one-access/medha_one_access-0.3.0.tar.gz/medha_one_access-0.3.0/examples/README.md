# MedhaOne Access Control - Examples

This directory contains example code demonstrating different usage patterns for the MedhaOne Access Control library.

## Examples Overview

### 1. Basic Usage (`basic_usage.py`)

Demonstrates fundamental operations:
- Creating users and user groups
- Creating resources and resource groups  
- Setting up access rules
- Checking permissions
- Resolving user access

**Run with:**
```bash
python examples/basic_usage.py
```

### 2. FastAPI Integration (`fastapi_integration.py`)

Shows how to integrate the library with FastAPI for web APIs:
- Creating a FastAPI application with access control
- REST API endpoints for managing users, resources, and rules
- Access checking endpoints
- Health monitoring

**Run with:**
```bash
python examples/fastapi_integration.py
```

Then visit http://localhost:8000/docs for interactive API documentation.

### 3. CLI Usage (`cli_usage.py`)  

Demonstrates command-line interface usage:
- Database initialization
- Data import/export
- Access checking via CLI
- Expression validation

**Run with:**
```bash
python examples/cli_usage.py
```

### 4. Advanced Patterns (`advanced_patterns.py`)

Illustrates complex access control scenarios:
- Hierarchical organizational structures
- Complex user/resource expressions
- Time-based access constraints  
- BODMAS resolution methodology
- Audit trail analysis

**Run with:**
```bash
python examples/advanced_patterns.py
```

## Prerequisites

Before running the examples, ensure you have installed the library:

```bash
# Install from local directory
pip install -e .

# Or install with optional dependencies
pip install -e ".[api,cli]"
```

## Database Setup

The examples use SQLite databases by default for simplicity. For production usage, configure a PostgreSQL database:

```bash
export DATABASE_URL="postgresql://user:password@localhost/dbname"
```

## Common Patterns Demonstrated

### User and Resource Expressions

```python
# Simple inclusion
expression = "user1 + user2 + user3"

# Complex grouping
expression = "managers + developers - contractors"
```

### Time Constraints

```python
time_constraints = {
    "dateRanges": [
        {"startDate": "2024-01-01", "endDate": "2024-12-31"}
    ],
    "timeWindows": [
        {"startTime": "09:00", "endTime": "17:00"}
    ],
    "daysOfWeek": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
}
```

### BODMAS Resolution

The library uses a 4-step BODMAS methodology:
1. [UserGroup × ResourceGroup] - Most general rules
2. [UserGroup × Individual Resource] - Group to specific resource
3. [Individual User × ResourceGroup] - Specific user to group  
4. [Individual User × Individual Resource] - Most specific rules

Later steps can override earlier ones, providing fine-grained control.

## Next Steps

After running these examples, explore:
- The [API documentation](../docs/) for detailed reference
- The [test suite](../tests/) for additional usage patterns
- The [CLI reference](../docs/cli.md) for command-line usage

## Support

For questions or issues with these examples, please check:
- The main [README](../README.md) 
- The [documentation](../docs/)
- Open an issue on the project repository