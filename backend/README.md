# Backend Services

## Overview

Backend microsserviços for HunterTeck B2B pipeline.

## Structure

```
backend/
├── services/           # Microsserviços (copy from root/services)
├── config/            # Configuration
├── tests/             # Unit tests
└── __init__.py
```

## Services

- **Lead Extractor**: Extract companies from various sources
- **Validator**: Validate extracted data quality
- **Enricher**: Enrich company data with additional info
- **Person Finder**: Find decision makers in companies
- **Email Generator**: Generate personalized emails (Groq-powered)
- **SMTP Dispatcher**: Send emails with product routing

## Development

```bash
# Install deps
pip install -e ".[dev,groq]"

# Run tests
pytest backend/tests/

# Type check
mypy backend/
```

## See Also

- [Docs](../docs/README.md)
- [Architecture](../docs/ARCHITECTURE.md)
- [API Reference](../docs/api/backend.md)
