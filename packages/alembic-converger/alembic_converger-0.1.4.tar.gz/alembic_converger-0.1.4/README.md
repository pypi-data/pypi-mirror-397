# Alembic Converger

[![PyPI version](https://img.shields.io/pypi/v/alembic-converger.svg)](https://pypi.org/project/alembic-converger/)
[![Documentation Status](https://readthedocs.org/projects/alembic-converger/badge/?version=latest)](https://alembic-converger.readthedocs.io/en/latest/README.html)
[![Python Support](https://img.shields.io/pypi/pyversions/alembic-converger.svg)](https://pypi.org/project/alembic-converger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Safely converge Alembic migration graphs by automatically generating minimal merge migrations.**

Alembic Converger is a production-grade Python tool that detects and resolves multiple migration heads in your Alembic migration history. It creates graph-only merge migrations without modifying schema operations, ensuring safe convergence for teams working with parallel database migrations.

## The Problem

When multiple developers work on database migrations in parallel, or when merging feature branches, you often end up with **multiple heads** in your Alembic migration graph:

```
        [feature-1]  [feature-2]
              |           |
           rev-abc     rev-def
                \       /
                 \     /
                [main branch]
                    |
                  rev-123
```

Alembic requires a single linear path to `head`, and having multiple heads can cause:
- Failed deployments
- CI/CD pipeline failures
- Confusion about which migrations to apply

## Why Alembic Converger?

**Traditional approach:**
```bash
# Manual merge - error-prone and time-consuming
alembic merge -m "merge heads" rev-abc rev-def
# Did it create schema conflicts? Who knows! 😰
```

**With Alembic Converger:**
```bash
# Automatic, safe convergence
alembic-converger converge --from-revision rev-123
# ✓ Validates merge is graph-only
# ✓ Tests upgrade path automatically
# ✓ Fails fast on conflicts
```

## Safety Guarantees

🔒 **This tool is designed to be safe by default:**

1. **Never modifies existing migrations** - Only creates new merge migrations
2. **Never guesses developer intent** - Only performs graph-only merges
3. **Never auto-resolves schema conflicts** - Fails if merge contains operations
4. **Validates upgrade path** - Runs `alembic upgrade` after each merge
5. **Deterministic behavior** - Same input always produces same result
6. **Automatic rollback** - Deletes created merges on failure

## Installation

```bash
pip install alembic-converger
```

**Requirements:**
- Python 3.8+
- Alembic 1.7.0+

## Quick Start

### Basic Usage

```bash
# Converge all heads from a base revision
alembic-converger converge --from-revision ae1027a6acf

# Dry run to preview changes
alembic-converger converge --from-revision ae1027a6acf --dry-run

# Skip database validation (faster, less safe)
alembic-converger converge --from-revision ae1027a6acf --skip-validation

# Verbose output for debugging
alembic-converger converge --from-revision ae1027a6acf --verbose
```

### Python API

```python
from alembic_converger import converge_migrations

# Programmatic convergence
result = converge_migrations(
    base_revision="ae1027a6acf",
    config_path="alembic.ini",
    dry_run=False,
    skip_validation=False,
    verbose=True
)

print(f"Created {len(result.merges_created)} merge(s)")
print(f"Final head: {result.final_head}")
```

## How It Works

Alembic Converger treats your migrations as a **directed acyclic graph (DAG)**:

1. **Discovery**: Find all heads descending from a known base revision
2. **Validation**: Ensure all heads share a common ancestor
3. **Convergence**: Iteratively merge heads pairwise until one remains
4. **Verification**: After each merge:
   - Validate the merge contains **no schema operations**
   - Run `alembic upgrade` to test the path
   - Reload the graph and continue

### Example Scenario

```
Initial state (3 heads):
    head-1    head-2    head-3
       \        |        /
        \       |       /
         base (ae1027a6acf)

After convergence:
         final-head
            |
        merge-2
          /   \
     merge-1  head-3
       /  \
   head-1 head-2
       \   |   /
         base
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Check Alembic Convergence

on: [pull_request]

jobs:
  check-migrations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install alembic-converger
          pip install -r requirements.txt
      
      - name: Check for multiple heads
        run: |
          # Get the base revision (e.g., from main branch)
          BASE_REV=$(git merge-base origin/main HEAD)
          
          # Try to converge (will fail if conflicts exist)
          alembic-converger converge \
            --from-revision $BASE_REV \
            --dry-run
```

### Pre-deployment Hook

```bash
#!/bin/bash
# deploy.sh

echo "Checking for multiple Alembic heads..."
alembic-converger converge --from-revision $(git describe --tags --abbrev=0) --dry-run

if [ $? -eq 0 ]; then
  echo "✓ Migrations converged"
  # Continue with deployment
else
  echo "✗ Migration convergence failed"
  exit 1
fi
```

## CLI Reference

### `converge` Command

```
alembic-converger converge [OPTIONS]

Options:
  --from-revision TEXT     Base revision to converge from [required]
  --alembic-config TEXT    Path to alembic.ini [default: alembic.ini]
  --dry-run               Show what would be done without changes
  --skip-validation       Skip upgrade validation (not recommended)
  --verbose, -v           Enable debug logging
  --help                  Show this message and exit
```

### Exit Codes

- `0`: Success (already converged or successfully merged)
- `1`: Convergence failed (validation error, conflicts, etc.)
- `2`: Configuration error (invalid alembic.ini, missing files, etc.)

## FAQ

### Why not just use `alembic merge`?

`alembic merge` creates a single merge migration but:
- Doesn't validate the merge is conflict-free
- Doesn't test the upgrade path
- Requires manual intervention for each merge
- Can silently create broken migrations

Alembic Converger automates this safely with validation.

### Why not auto-resolve schema conflicts?

**Safety first.** Schema conflicts require developer judgment:
- Which column definition to keep?
- How to handle conflicting constraints?
- What about data migrations?

Auto-resolving could cause data loss or corruption. Instead, we **fail fast** and let you resolve manually.

### When should I use this tool?

Perfect for:
- ✅ CI/CD pipelines (pre-deployment checks)
- ✅ Multi-developer teams with parallel migrations
- ✅ Feature branch merges
- ✅ Automated migration management

Not suitable for:
- ❌ Resolving schema conflicts (requires manual intervention)
- ❌ Rewriting migration history (never modifies existing files)

### What if validation fails?

When validation fails, Alembic Converger:
1. Logs the detailed error
2. Rolls back created merge migrations
3. Exits with code 1

You'll need to manually resolve conflicts:
```bash
# Review the conflicting migrations
alembic history --verbose

# Manually create merge with conflict resolution
alembic merge -m "resolve conflicts" rev-1 rev-2
# Edit the generated file to resolve conflicts
```

### Can I use this without a database?

Yes, with `--skip-validation`:
```bash
alembic-converger converge --from-revision X --skip-validation
```

However, this skips upgrade testing, reducing safety guarantees. Use only when:
- Database is not available (e.g., CI without DB)
- You'll test manually later

## Architecture

Alembic Converger is built with clean separation of concerns:

```
alembic_converger/
├── cli.py          # Click-based CLI interface
├── config.py       # Alembic configuration loading
├── graph.py        # DAG analysis & traversal
├── merge.py        # Merge creation & validation
├── validate.py     # Upgrade path testing
├── converge.py     # Main orchestration algorithm
├── errors.py       # Exception hierarchy
└── utils.py        # Shared utilities
```

### Key Design Principles

1. **Graph-first thinking**: Migrations are nodes in a DAG, not files
2. **Fail fast**: Detect problems early with clear errors
3. **Idempotent**: Same input → same output every time
4. **No side effects**: Only creates merge files, never modifies existing ones
5. **Observable**: Comprehensive logging at every step

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/rishav00a/alembic_converger.git
cd alembic_converger

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=alembic_converger --cov-report=html

# Run specific test file
pytest tests/test_graph.py -v
```

### Code Quality

```bash
# Format code
black alembic_converger tests

# Lint code
ruff check alembic_converger tests

# Type checking (optional)
mypy alembic_converger
```

## Publishing to PyPI

```bash
# Install build tools
pip install build twine

# Build distribution
python -m build

# Check package
twine check dist/*

# Upload to TestPyPI (optional)
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Built with ❤️ by the open-source community.

Powered by:
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations for SQLAlchemy
- [Click](https://click.palletsprojects.com/) - Command-line interface creation
- [Colorama](https://github.com/tartley/colorama) - Cross-platform colored terminal text

## Support

- 📖 [Documentation](https://alembic-converger.readthedocs.io/en/latest/README.html)
- 🐛 [Issue Tracker](https://github.com/rishav00a/alembic_converger/issues)
- 💬 [Discussions](https://github.com/rishav00a/alembic_converger/discussions)

---

**Remember**: This tool is a *graph normalizer*, not a migration author. It safely converges parallel development paths without guessing your intent. ✨
