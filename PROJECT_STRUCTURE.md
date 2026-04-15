# Project Structure

```
hunterteck/
│
├── .github/                          # GitHub configuration
│   ├── workflows/                   # CI/CD pipelines
│   │   └── ci-cd.yml               # GitHub Actions workflow
│   └── ISSUE_TEMPLATE/              # Issue templates
│       └── bug_report.md           # Bug report template
│
├── backend/                          # Backend Python code
│   ├── config/                      # Configuration management
│   ├── tests/                       # Backend unit tests
│   └── __init__.py
│
├── frontend/                         # Frontend (Streamlit)
│   ├── app_hunter.py               # Main Streamlit app (symlink)
│   └── requirements_app.txt         # Streamlit dependencies
│
├── mlops/                           # MLOps & AI (Groq integration)
│   ├── groq/                        # Groq configuration
│   └── requirements_groq.txt        # Groq dependencies
│
├── deployment/                       # Deployment configuration
│   ├── docker/                      # Docker setup
│   │   ├── Dockerfile              # Backend image
│   │   └── Dockerfile.streamlit    # Frontend image
│   ├── kubernetes/                  # Kubernetes manifests
│   ├── scripts/                    # Deployment scripts
│   │   └── deploy.sh              # Main deployment script
│   └── docker-compose.yml          # Local development compose
│
├── infra/                           # Infrastructure as Code
│   ├── terraform/                   # Terraform configurations
│   ├── ansible/                     # Ansible playbooks
│   └── .gitkeep
│
├── tests/                           # Global test suite
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── scripts/                         # Utility scripts
│   ├── setup.sh                    # Development setup
│   ├── check-quality.sh           # Code quality checks
│   └── deploy.sh                  # Deployment script (symlink)
│
├── docs/                            # Documentation
│   ├── guides/                      # How-to guides
│   ├── api/                         # API documentation
│   ├── README.md                   # Documentation index
│   └── architecture.md             # Architecture docs
│
├── data/                            # Data directory
│   ├── leads.db                    # SQLite database
│   └── backups/                    # Database backups
│
├── logs/                            # Application logs
│   └── *.log                       # Log files
│
├── services/                        # Original microsservices (KEEP)
│   └── lead_extractor/            # Copied here for reference
│
├── .env.example                     # Environment template
├── .github/                         # GitHub workflows
├── .gitignore                      # Git ignore rules
├── pyproject.toml                  # Project configuration
├── docker-compose.yml              # Docker compose (DEV)
├── README.md                       # Project README
├── LICENSE                         # License file
│
└── *.md                            # Documentation files
    ├── QUICK_START.md
    ├── ARQUITETURA.md
    ├── GROQ_MIGRATION.md
    ├── STREAMLIT_GUIDE.md
    └── ...
```

## Directory Descriptions

### `.github/`
GitHub-specific files including CI/CD workflows and issue templates.

### `backend/`
Python backend code, tests, and configuration.

### `frontend/`
Streamlit frontend application and dependencies.

### `mlops/`
Machine Learning Operations - Groq LLM integration and AI configuration.

### `deployment/`
Docker, Kubernetes, and deployment scripts for various environments.

### `infra/`
Infrastructure as Code - Terraform for AWS, Ansible playbooks, etc.

### `tests/`
Global test suite including unit, integration, and end-to-end tests.

### `scripts/`
Utility and helper scripts for development and deployment.

### `docs/`
Project documentation, guides, and API references.

### `data/`
SQLite database and backups for persistent storage.

### `logs/`
Application logs from running services.

### `services/`
Original microsservices code (keep for reference/migration).

---

## File Organization Tips

1. **Backend Code**: Keep in `backend/` or `services/lead_extractor/`
2. **Tests**: Mirror structure in `tests/` directory
3. **Config**: Environment-specific configs in `backend/config/`
4. **Docs**: Guide-specific docs in `docs/guides/`
5. **Scripts**: Always put in `scripts/` with shebang + execute bit
6. **Deployment**: Env-specific files in `deployment/` subdirs

---

Last Updated: April 14, 2026
