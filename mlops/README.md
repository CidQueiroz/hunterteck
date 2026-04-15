# MLOps - Groq LLM integration

## Overview

Machine Learning Operations for HunterTeck.

## Groq Integration

Using Groq (`llama3-70b-8192`) for free email generation:
- 0$ cost (Free Tier)
- Automatic retry with backoff
- Rate limit handling
- Template fallback

## Installation

```bash
pip install -e ".[groq]"
```

## Configuration

```bash
export GROQ_API_KEY="gsk_YOUR_KEY"
# or in .env: GROQ_API_KEY=gsk_YOUR_KEY
```

## Usage

```python
from services.lead_extractor.email_generator import GeradorEmails

gerador = GeradorEmails()  # Groq automatic
email = gerador.gerar_email(contexto, usar_ia=True)
```

## See Also

- [Groq Migration Guide](../GROQ_MIGRATION.md)
- [Groq Architecture](../GROQ_ARCHITECTURE.md)
