# Quick Start Guide - RUBEM Hydrological v2.0

## 🚀 5-Minute Setup

### For Plugin Users

```bash
# 1. Ensure QGIS 4.2 is installed
qgis --version  # Should show 4.2 or later

# 2. Verify Python version
# Open QGIS Python Console and run:
import sys; print(sys.version)  # Should show 3.13+

# 3. Install plugin via QGIS Plugin Manager
# Or download from: https://github.com/LabSid-USP/RUBEMHydrological/releases
```

### For Developers

```bash
# 1. Clone repository
git clone https://github.com/LabSid-USP/RUBEMHydrological.git
cd RUBEMHydrological

# 2. Install dependencies
poetry install --with dev,docs

# 3. Setup pre-commit hooks
poetry run pre-commit install

# 4. Run tests
# Needs a QGIS-importable interpreter (see AGENTS.md). Example with system QGIS:
QT_QPA_PLATFORM=offscreen PYTEST_QT_API=pyqt6 \
  python -m pytest test/unit -m unit -p no:pytest_qgis -p no:pytestqt -v

# 5. Check code quality
poetry run ruff check .
poetry run black --check .
poetry run mypy plugin/

# Done! Start coding 🎉
```

## 📖 Quick Examples

### Load Configuration

```python
from plugin.models import RUBEMConfig

# Load from TOML (recommended)
config = RUBEMConfig.from_toml_file("config.toml")

# Access with type safety
print(f"Period: {config.sim_time.start} to {config.sim_time.end}")
print(f"Alpha: {config.calibration.alpha}")
```

### Use Logging

```python
from plugin.logging import get_logger

logger = get_logger(__name__)

logger.info("Processing started")
logger.error("Error occurred", exc_info=True)
```

### Handle Errors

```python
from plugin.exceptions import ValidationError

try:
    validate_config(config)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    print(f"Details: {e.details}")
```

## 📚 Documentation

- **Full Documentation**: https://rubem-hydrological.readthedocs.io
- **Development Guide**: [DEVELOPMENT.md](DEVELOPMENT.md)
- **Migration Guide**: [MIGRATION.md](MIGRATION.md)
- **API Examples**: [examples/api_examples.py](examples/api_examples.py)

## 🔧 Common Commands

```bash
# Format code
poetry run black .

# Lint code
poetry run ruff check --fix .

# Type check
poetry run mypy plugin/

# Unit tests (fakes; disable GUI plugins)
QT_QPA_PLATFORM=offscreen PYTEST_QT_API=pyqt6 \
  python -m pytest test/unit -m unit -p no:pytest_qgis -p no:pytestqt -v

# Integration / dialog GUI tests
QT_QPA_PLATFORM=offscreen PYTEST_QT_API=pyqt6 \
  python -m pytest test/integration -m integration -v

# Build documentation
cd doc && poetry run python -m sphinx -b html source build/html

# Build plugin package
python scripts/build_plugin.py
```

## 🐛 Troubleshooting

### Issue: Import errors in IDE

**Solution**: Configure your IDE to use Poetry environment
```bash
poetry env info  # Get path to virtual environment
# Point your IDE Python interpreter to this path
```

### Issue: Pre-commit hooks failing

**Solution**: Run formatters manually first
```bash
poetry run black .
poetry run ruff check --fix .
git add -u
git commit -m "fix: format code"
```

### Issue: Tests not finding QGIS modules

**Solution**: Unit tests don't need QGIS. For integration tests:
```bash
# Run tests inside QGIS Python environment
# Or use the Docker container with QGIS
docker run --rm -v "$PWD":/work -w /work -e QT_QPA_PLATFORM=offscreen \
  -e PYTEST_QT_API=pyqt6 -e PYTHONPATH=/work:/usr/share/qgis/python \
  qgis/qgis:4.2 bash -lc \
  'python3 -m venv --system-site-packages /tmp/v && /tmp/v/bin/pip install "pytest>=8.3,<9" "pytest-qt>=4.5,<5" "pytest-qgis==5.0.2" "pydantic>=2.11,<3" humanize "python-dateutil>=2" && /tmp/v/bin/python -m pytest test/integration -m integration'
```

## 🎯 What's New in v2.0

✅ Python 3.13+ support  
✅ QGIS 4.2 compatibility  
✅ Type hints everywhere  
✅ Pydantic configuration  
✅ Structured logging  
✅ Custom exceptions  
✅ Pytest test suite  
✅ CI/CD pipeline  
✅ Pre-commit hooks  
✅ Comprehensive docs  

## 📞 Get Help

- **Issues**: https://github.com/LabSid-USP/RUBEMHydrological/issues
- **Email**: rubem.hydrological@labsid.eng.br
- **Docs**: https://rubem-hydrological.readthedocs.io

## 🎉 Ready to Contribute?

Read [CONTRIBUTING.md](CONTRIBUTING.md) and start with:
1. Pick an issue labeled "good first issue"
2. Fork the repository
3. Create a feature branch
4. Make your changes
5. Run tests and linting
6. Submit a pull request

Happy coding! 🚀
