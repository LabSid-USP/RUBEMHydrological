# Migration Guide: RUBEM Hydrological v1.x to v2.0

This guide helps you migrate code, configurations, and workflows from RUBEM Hydrological v1.x to v2.0.

## Table of Contents

- [Overview](#overview)
- [Breaking Changes](#breaking-changes)
- [Step-by-Step Migration](#step-by-step-migration)
- [Code Migration](#code-migration)
- [Configuration Migration](#configuration-migration)
- [Testing Migration](#testing-migration)
- [Common Issues](#common-issues)

## Overview

Version 2.0 introduces significant improvements but requires some migration effort:

- **Python 3.9 → 3.13**: Modern Python features
- **QGIS 3 → 4.2**: The plugin targets QGIS 4 and PyQt6
- **ConfigParser → Pydantic**: Type-safe configuration
- **print → logging**: Structured logging
- **unittest → pytest**: Modern testing

## Breaking Changes

### 1. Version Requirements

**Before (v1.x)**:
```
Python >= 3.9
QGIS >= 3.0
```

**After (v2.0)**:
```
Python >= 3.13
QGIS >= 4.0
```

**Action**: Ensure your QGIS installation uses Python 3.13+

### 2. Import Changes

**Before**:
```python
from plugin.core import RUBEMHydrological
```

**After**:
```python
from plugin.core_refactored import RUBEMHydrological
# or just use plugin.core after migration is complete
```

### 3. Exception Handling

**Before**:
```python
try:
    validate_config(config)
except ValueError as e:
    print(f"Error: {e}")
```

**After**:
```python
from plugin.exceptions import ValidationError
from plugin.logging import get_logger

logger = get_logger(__name__)

try:
    validate_config(config)
except ValidationError as e:
    logger.error(f"Validation failed: {e}", exc_info=True)
```

### 4. Configuration Loading

**Before**:
```python
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
start_date = config.get("SIM_TIME", "start")
```

**After**:
```python
from plugin.models import RUBEMConfig

config = RUBEMConfig.from_ini_file("config.ini")
start_date = config.sim_time.start
```

### 5. Logging

**Before**:
```python
print("Processing started")
print(f"Error: {error_msg}")
```

**After**:
```python
from plugin.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing started")
logger.error(f"Error: {error_msg}")
```

## Step-by-Step Migration

### For Plugin Users

1. **Backup Your Data**
   ```bash
   # Backup project files and configurations
   cp -r ~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/rubem_hydrological \
        ~/rubem_backup_$(date +%Y%m%d)
   ```

2. **Update QGIS**
   - Install QGIS 4.2
   - Verify Python version: Open QGIS Python Console and run:
     ```python
     import sys
     print(sys.version)
     ```
   - Should show Python 3.13 or later

3. **Install New Version**
   - Remove old plugin via Plugin Manager
   - Install v2.0 from Plugin Repository or ZIP
   - Restart QGIS

4. **Migrate Configurations** (optional)
   - Project files are JSON. INI projects are not loaded.
   - Optionally convert to `.toml` for new features:
     ```python
     from plugin.models import RUBEMConfig
     
     config = RUBEMConfig.from_ini_file("old_config.ini")
     config.to_toml_file("new_config.toml")
     ```

### For Plugin Developers

1. **Update Development Environment**
   ```bash
   # Install Python 3.13
   # (method depends on your OS)
   
   # Install Poetry
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Clone repository
   git clone https://github.com/LabSid-USP/RUBEMHydrological.git
   cd RUBEMHydrological
   git checkout development
   
   # Install dependencies
   poetry install --with dev,docs
   
   # Setup pre-commit hooks
   poetry run pre-commit install
   ```

2. **Migrate Your Code**
   
   Use the migration script:
   ```bash
   # Dry run to see what would change
   python scripts/migrate_code.py plugin/ --dry-run
   
   # Actually migrate
   python scripts/migrate_code.py plugin/
   ```
   
   Then review and fix TODO comments.

3. **Update Imports**
   ```bash
   # Find all files that need import updates
   grep -r "from plugin.core import" plugin/
   
   # Update manually or with sed
   find plugin/ -name "*.py" -exec sed -i \
     's/from plugin.core import/from plugin.core_refactored import/g' {} \;
   ```

4. **Add Type Hints**
   ```python
   # Before
   def calculate_runoff(precip, infiltration):
       return precip - infiltration
   
   # After
   def calculate_runoff(precip: float, infiltration: float) -> float:
       """Calculate runoff from precipitation and infiltration.
       
       Args:
           precip: Precipitation amount in mm.
           infiltration: Infiltration amount in mm.
           
       Returns:
           Runoff amount in mm.
       """
       return max(0.0, precip - infiltration)
   ```

5. **Update Tests**
   ```python
   # Before (unittest)
   import unittest
   
   class TestRunoff(unittest.TestCase):
       def test_basic(self):
           result = calculate_runoff(100, 30)
           self.assertEqual(result, 70)
   
   # After (pytest)
   import pytest
   
   @pytest.mark.unit
   def test_calculate_runoff():
       """Test basic runoff calculation."""
       result = calculate_runoff(100.0, 30.0)
       assert result == 70.0
   ```

6. **Run Quality Checks**
   ```bash
   # Format code
   poetry run black plugin/
   
   # Lint code
   poetry run ruff check --fix plugin/
   
   # Type check
   poetry run mypy plugin/
   
   # Run tests
   poetry run pytest
   ```

## Code Migration

### Pattern 1: Print to Logger

**Before**:
```python
def process_data(input_file):
    print(f"Processing {input_file}")
    try:
        data = load_data(input_file)
        print(f"Loaded {len(data)} records")
    except Exception as e:
        print(f"Error: {e}")
        return None
    return data
```

**After**:
```python
from plugin.logging import get_logger
from plugin.exceptions import FileOperationError

logger = get_logger(__name__)

def process_data(input_file: Path) -> list[Any] | None:
    """Process data from input file.
    
    Args:
        input_file: Path to input file.
        
    Returns:
        Loaded data or None if error occurred.
        
    Raises:
        FileOperationError: If file cannot be loaded.
    """
    logger.info(f"Processing {input_file}")
    try:
        data = load_data(input_file)
        logger.debug(f"Loaded {len(data)} records")
    except Exception as e:
        logger.error(f"Failed to process {input_file}: {e}", exc_info=True)
        raise FileOperationError(
            f"Cannot load data from {input_file}",
            details={"file": str(input_file), "error": str(e)}
        ) from e
    return data
```

### Pattern 2: Config Access

**Before**:
```python
config = configparser.ConfigParser()
config.read("config.ini")

start_date = config.get("SIM_TIME", "start")
end_date = config.get("SIM_TIME", "end")
input_dir = config.get("DIRECTORIES", "input")

# Manual validation
try:
    datetime.strptime(start_date, "%Y-%m-%d")
except ValueError:
    raise ValueError("Invalid start date")
```

**After**:
```python
from plugin.models import RUBEMConfig

# Load and validate automatically
config = RUBEMConfig.from_ini_file("config.ini")

# Type-safe access
start_date = config.sim_time.start  # datetime object
end_date = config.sim_time.end      # datetime object
input_dir = config.directories.input  # Path object

# Validation already done by Pydantic
assert start_date < end_date  # Guaranteed by validator
```

### Pattern 3: Exception Handling

**Before**:
```python
def validate_raster(raster_path):
    if not os.path.exists(raster_path):
        raise ValueError(f"Raster not found: {raster_path}")
    
    try:
        layer = QgsRasterLayer(raster_path)
        if not layer.isValid():
            raise Exception("Invalid raster")
    except Exception as e:
        raise Exception(f"Raster error: {e}")
```

**After**:
```python
from pathlib import Path
from plugin.exceptions import FileOperationError, RasterOperationError
from plugin.logging import get_logger

logger = get_logger(__name__)

def validate_raster(raster_path: Path) -> None:
    """Validate raster file.
    
    Args:
        raster_path: Path to raster file.
        
    Raises:
        FileOperationError: If raster file not found.
        RasterOperationError: If raster is invalid.
    """
    if not raster_path.exists():
        raise FileOperationError(
            f"Raster not found: {raster_path}",
            details={"file": str(raster_path)}
        )
    
    try:
        layer = QgsRasterLayer(str(raster_path))
        if not layer.isValid():
            raise RasterOperationError(
                "Invalid raster layer",
                details={
                    "file": str(raster_path),
                    "error": layer.error().message()
                }
            )
    except Exception as e:
        logger.error(f"Raster validation failed: {e}", exc_info=True)
        raise RasterOperationError(
            f"Cannot validate raster: {raster_path}",
            details={"file": str(raster_path), "error": str(e)}
        ) from e
```

## Configuration Migration

### INI to TOML

**Before (`config.ini`)**:
```ini
[SIM_TIME]
start = 2020-01-01
end = 2020-12-31

[DIRECTORIES]
input = /path/to/input
output = /path/to/output

[CALIBRATION]
alpha = 0.5
beta = 1.5
```

**After (`config.toml`)**:
```toml
[sim_time]
start = "2020-01-01"
end = "2020-12-31"

[directories]
input = "/path/to/input"
output = "/path/to/output"

[calibration]
alpha = 0.5
beta = 1.5
lambda_factor = 0.3
kc = 1.0
field_capacity = 0.35
wilting_point = 0.15
```

**Migration Script**:
```python
from plugin.models import RUBEMConfig

# Load old format
config = RUBEMConfig.from_ini_file("config.ini")

# Save new format
config.to_toml_file("config.toml")
```

## Testing Migration

### unittest to pytest

**Before**:
```python
# test/unit/test_utils.py
import unittest
from plugin.utils import calculate_something

class TestUtils(unittest.TestCase):
    def setUp(self):
        self.test_value = 42
    
    def test_calculation(self):
        result = calculate_something(self.test_value)
        self.assertEqual(result, 84)
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
```

**After**:
```python
# test/unit/test_utils.py
import pytest
from plugin.utils import calculate_something

@pytest.fixture
def test_value():
    """Fixture providing test value."""
    return 42

@pytest.mark.unit
def test_calculation(test_value):
    """Test calculation function."""
    result = calculate_something(test_value)
    assert result == 84
```

## Common Issues

### Issue 1: Import Errors

**Problem**:
```
ImportError: cannot import name 'RUBEMHydrological' from 'plugin.core'
```

**Solution**:
```python
# Update import
from plugin.core_refactored import RUBEMHydrological
# Or wait for full migration and use:
from plugin.core import RUBEMHydrological
```

### Issue 2: Type Errors

**Problem**:
```
TypeError: expected str, got Path
```

**Solution**:
```python
# Convert Path to str when needed
path = Path("/some/path")
some_old_function(str(path))  # Convert to string
```

### Issue 3: Config Access

**Problem**:
```
KeyError: 'SIM_TIME'
```

**Solution**:
```python
# Old way
config["SIM_TIME"]["start"]

# New way
config.sim_time.start
```

### Issue 4: Missing Dependencies

**Problem**:
```
ModuleNotFoundError: No module named 'pydantic'
```

**Solution**:
```bash
# Install dependencies
poetry install

# Or with pip in QGIS Python
python3 -m pip install pydantic pydantic-settings
```

## Getting Help

If you encounter issues during migration:

1. **Check Documentation**: Read `DEVELOPMENT.md` and this guide
2. **Search Issues**: Look in [GitHub Issues](https://github.com/LabSid-USP/RUBEMHydrological/issues)
3. **Ask Community**: Create a new issue with:
   - Error message
   - Code snippet
   - QGIS and Python versions
4. **Email**: rubem.hydrological@labsid.eng.br

## Checklist

Use this checklist to track your migration:

- [ ] Updated QGIS to 4.2
- [ ] Verified Python 3.13+ in QGIS
- [ ] Backed up old plugin and data
- [ ] Installed new plugin version
- [ ] Updated import statements
- [ ] Replaced print with logger
- [ ] Added type hints
- [ ] Updated exception handling
- [ ] Migrated configurations (if needed)
- [ ] Updated tests to pytest
- [ ] Ran linting (ruff)
- [ ] Ran type checking (mypy)
- [ ] Ran test suite
- [ ] Updated documentation
- [ ] Tested in QGIS

## Timeline

Recommended migration timeline:

- **Week 1**: Update environment and dependencies
- **Week 2**: Migrate core code (imports, logging, exceptions)
- **Week 3**: Add type hints and update tests
- **Week 4**: Quality checks and testing
- **Week 5**: Documentation and cleanup

For large codebases, allocate more time accordingly.
