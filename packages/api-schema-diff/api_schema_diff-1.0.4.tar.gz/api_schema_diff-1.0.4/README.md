# api-schema-diff

[![PyPI version](https://img.shields.io/pypi/v/api-schema-diff.svg)](https://pypi.org/project/api-schema-diff/)
[![Python versions](https://img.shields.io/pypi/pyversions/api-schema-diff.svg)](https://pypi.org/project/api-schema-diff/)
[![CI](https://github.com/teolzr/schema-diff/actions/workflows/ci.yml/badge.svg)](https://github.com/teolzr/schema-diff/actions)
[![Docker](https://github.com/teolzr/schema-diff/actions/workflows/docker.yml/badge.svg)](https://github.com/teolzr/schema-diff/actions/workflows/docker.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Detect **breaking changes** between API schemas (OpenAPI / JSON Schema) in a **deterministic, CI-friendly** way.

`api-schema-diff` is a CLI tool designed to answer one question reliably:

> **"Will this schema change break existing clients?"**

---

## Why this exists

API changes often break clients silently.

Common causes:
- Removing endpoints
- Removing fields
- Changing parameter requirements
- Changing request/response schemas

`api-schema-diff` catches these issues **before** they reach production.

---

## Features

### Supported inputs
- OpenAPI 3.x (JSON / YAML)
- JSON Schema (generic structure diff)

### Breaking changes detected
- Removed paths or operations
- Removed query / path / header parameters
- Parameters becoming required
- Parameter schema type changes
- Request body removed
- Request body becoming required
- Request body schema breaking changes
- Removed response status codes
- Response schema breaking changes
- Removed properties in schemas
- Property type changes
- Optional → required fields

### Non-breaking changes detected
- Added paths or operations
- Added optional parameters
- Added optional request bodies
- Added response status codes
- Added optional properties

### Designed for CI
- Deterministic output
- Stable exit codes
- JSON output for automation
- Works offline (no cloud / no LLM dependency)

---

## Installation

```bash
pip install api-schema-diff
```

Or install from source:

```bash
git clone https://github.com/teolzr/schema-diff.git
cd schema-diff
pip install -e .
```

**Requirements:**
- Python 3.10 or higher
- `typer>=0.12`
- `rich>=13.7`

### Docker

Run without installing Python:

```bash
# Pull the image
docker pull ghcr.io/teolzr/schema-diff:latest

# Run with local files
docker run --rm -v $(pwd):/workspace ghcr.io/teolzr/schema-diff:latest old.yaml new.yaml

# Check version
docker run --rm ghcr.io/teolzr/schema-diff:latest --version

# Use in CI/CD
docker run --rm \
  -v $(pwd):/workspace \
  ghcr.io/teolzr/schema-diff:latest \
  schemas/v1.yaml schemas/v2.yaml \
  --format json
```

**Available tags:**
- `latest` - Latest stable release
- `v0.1.4` - Specific version
- `main` - Latest from main branch

**📚 [Full Docker documentation →](docs/DOCKER.md)**

### GitHub Action

Use in any GitHub workflow:

```yaml
- uses: teolzr/schema-diff@v1
  with:
    old: api/schema-v1.yaml
    new: api/schema-v2.yaml
```

**Compare against main branch:**

```yaml
- run: git show origin/main:api/schema.yaml > /tmp/baseline.yaml
- uses: teolzr/schema-diff@v1
  with:
    old: /tmp/baseline.yaml
    new: api/schema.yaml
```

**JSON output:**

```yaml
- uses: teolzr/schema-diff@v1
  with:
    old: old.yaml
    new: new.yaml
    format: json
    fail-on-breaking: false
```

---

## Usage

### Basic usage

```bash
api-schema-diff old.json new.json
```

**Exit codes:**
- `0` → No breaking changes found
- `1` → Breaking changes detected

### Output formats

**Text output (default):**

```bash
api-schema-diff old.json new.json
```

Output:
```
BREAKING CHANGES FOUND

┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type         ┃ Path        ┃ Old Type┃ New Type┃ Message               ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ removed_field│ User.email  │         │         │                       │
│ type_change  │ Order.amount│ <number>│ <string>│                       │
└──────────────┴─────────────┴─────────┴─────────┴───────────────────────┘
```

**JSON output:**

```bash
api-schema-diff old.json new.json --format json
```

Output:
```json
{
  "breaking": [
    {
      "type": "removed_field",
      "severity": "breaking",
      "path": "User.email",
      "old_type": null,
      "new_type": null,
      "message": null
    },
    {
      "type": "type_change",
      "severity": "breaking",
      "path": "Order.amount",
      "old_type": "<number>",
      "new_type": "<string>",
      "message": null
    }
  ],
  "non_breaking": []
}
```

### CLI Options

```bash
api-schema-diff [OPTIONS] OLD_FILE NEW_FILE
```

**Arguments:**
- `OLD_FILE` - Path to the old schema file (JSON or YAML)
- `NEW_FILE` - Path to the new schema file (JSON or YAML)

**Options:**
- `--format [text|json]` - Output format (default: `text`)
- `--fail-on-breaking / --no-fail-on-breaking` - Exit with code 1 when breaking changes are found (default: `true`)
- `--help` - Show help message

### Report-only mode

Use `--no-fail-on-breaking` to always exit with code 0 (useful for reporting without failing CI):

```bash
api-schema-diff old.json new.json --no-fail-on-breaking
```

---

## Examples

### Example 1: Generic JSON diff

**old.json:**
```json
{
  "User": {
    "email": "a@b.com",
    "age": 30
  },
  "Order": {
    "amount": 12.5
  }
}
```

**new.json:**
```json
{
  "User": {
    "age": "30"
  },
  "Order": {
    "amount": "12.5"
  },
  "NewThing": {}
}
```

```bash
api-schema-diff old.json new.json
```

**Detected changes:**
- **Breaking:** `User.email` field removed
- **Breaking:** `User.age` type changed from number to string
- **Breaking:** `Order.amount` type changed from number to string
- **Non-breaking:** `NewThing` object added

### Example 2: OpenAPI diff

**old-api.yaml:**
```yaml
openapi: 3.0.0
paths:
  /users:
    get:
      parameters:
        - name: limit
          in: query
          required: false
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
                  email:
                    type: string
```

**new-api.yaml:**
```yaml
openapi: 3.0.0
paths:
  /users:
    get:
      parameters:
        - name: limit
          in: query
          required: true  # Now required!
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
                  # email removed!
```

```bash
api-schema-diff old-api.yaml new-api.yaml
```

**Detected changes:**
- **Breaking:** Query parameter `limit` became required
- **Breaking:** Response property `email` removed

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Schema Diff Check

on:
  pull_request:
    paths:
      - 'api/schema.yaml'

jobs:
  schema-diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install api-schema-diff
        run: pip install api-schema-diff

      - name: Get old schema from main branch
        run: git show origin/main:api/schema.yaml > old-schema.yaml

      - name: Check for breaking changes
        run: api-schema-diff old-schema.yaml api/schema.yaml
```

### GitLab CI

```yaml
api-schema-diff:
  image: python:3.10
  before_script:
    - pip install api-schema-diff
  script:
    - git show origin/main:api/schema.yaml > old-schema.yaml
    - api-schema-diff old-schema.yaml api/schema.yaml
  only:
    changes:
      - api/schema.yaml
```

### Pre-commit hook

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: api-schema-diff
        name: Check API schema for breaking changes
        entry: bash -c 'git show HEAD:api/schema.yaml > /tmp/old-schema.yaml && api-schema-diff /tmp/old-schema.yaml api/schema.yaml'
        language: system
        files: 'api/schema.yaml'
        pass_filenames: false
```

---

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/teolzr/schema-diff.git
cd schema-diff

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-cov black ruff
```

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=schema_diff --cov-report=html

# Run specific test file
pytest tests/test_openapi_diff.py
```

**Note:** The Python package is still named `schema_diff` internally, but the PyPI package and CLI command are `api-schema-diff`.

### Code formatting

```bash
# Format code
black .

# Lint code
ruff check .
```

### Project structure

```
schema-diff/
├── schema_diff/
│   ├── __init__.py
│   ├── cli.py          # CLI entry point
│   ├── diff.py         # Generic JSON diff logic
│   ├── loader.py       # Schema file loading
│   ├── models.py       # Data models
│   ├── rules.py        # Breaking change rules
│   └── openapi/
│       ├── __init__.py
│       ├── diff.py             # OpenAPI-specific diff
│       ├── json_schema_diff.py # JSON Schema diffing
│       ├── normalizer.py       # Schema normalization
│       └── resolver.py         # $ref resolution
├── tests/
├── pyproject.toml
└── README.md
```

---

## How it works

1. **Schema loading**: Automatically detects schema type (OpenAPI vs generic JSON/YAML)
2. **Normalization**: Resolves `$ref` references and normalizes structure
3. **Diffing**: Compares schemas using rule-based detection
4. **Classification**: Categorizes changes as breaking or non-breaking
5. **Reporting**: Outputs results in human-readable or JSON format

### Change detection logic

**Breaking changes:**
- Removing existing fields/paths → clients expect them
- Changing types → clients may send wrong data type
- Making optional fields required → clients may not send them
- Removing response fields → clients may depend on them

**Non-breaking changes:**
- Adding new fields/paths → clients can ignore them
- Making required fields optional → clients can still send them
- Adding new optional fields → backwards compatible

---

## Roadmap

- [ ] Support for OpenAPI 2.0 (Swagger)
- [ ] GraphQL schema diffing
- [ ] Custom rule configuration
- [ ] HTML report generation
- [ ] API compatibility scoring
- [ ] Severity levels (error, warning, info)

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run tests and linting
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

MIT License - see LICENSE file for details

---

## Credits

Built with:
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting

---

## Related Projects

- [openapi-diff](https://github.com/OpenAPITools/openapi-diff) - OpenAPI comparison tool
- [swagger-diff](https://github.com/Sayi/swagger-diff) - Swagger API comparison
- [json-schema-diff](https://github.com/json-schema-tools/json-schema-diff) - JSON Schema comparison

---

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/teolzr/schema-diff/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/teolzr/schema-diff/discussions)

**Note:** Repository name is `schema-diff`, but PyPI package name is `api-schema-diff`
