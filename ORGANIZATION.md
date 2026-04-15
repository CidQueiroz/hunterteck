# HunterTeck - Project Organization Guide

## 📁 Overview

The project has been reorganized into a professional structure following industry best practices:

```
hunterteck/
├── backend/          # Python services (microsserviços)
├── frontend/         # Streamlit UI
├── mlops/           # Groq LLM integration
├── deployment/      # Docker, K8s, deployment scripts
├── docs/            # Documentation
├── infra/           # Infrastructure as Code
├── scripts/         # Utility scripts
├── tests/           # Test suite
├── services/        # Original code (deprecated, will migrate)
└── .github/         # GitHub workflows & CI/CD
```

---

## 🚀 Quick Start

### 1. Setup Development Environment

```bash
bash scripts/setup.sh
```

This automatically:
- Creates Python virtual environment
- Installs all dependencies (dev, streamlit, groq)
- Creates `.env` file
- Runs basic tests

### 2. Copy Configuration

```bash
cp .env.example .env
# Edit .env with your API keys (GROQ_API_KEY, SMTP credentials, etc)
```

### 3. Run the Application

**Streamlit Frontend:**
```bash
streamlit run app_hunter.py
```

**Docker (Recommended for Production):**
```bash
docker-compose up -d
```

---

## 📂 Directory Structure

### `backend/` - Core Python Services

Store the microsserviços here:
```
backend/
├── services/           # Actual microsserviços (copy from root/services)
├── config/            # Configuration management
├── tests/             # Unit tests
└── __init__.py
```

**What to do:**
1. Copy `/services/lead_extractor/` to `backend/services/lead_extractor/`
2. Update imports to point to `backend.services.*`
3. Keep original `services/` for reference during transition

### `frontend/` - UI & Streamlit

```
frontend/
├── app_hunter.py         # Streamlit app (symlink from root)
├── requirements_app.txt  # Streamlit deps (symlink from root)
└── components/          # (Optional) Reusable Streamlit components
```

**What to do:**
```bash
ln -s ../app_hunter.py frontend/app_hunter.py
ln -s ../requirements_app.txt frontend/requirements_app.txt
```

### `mlops/` - Machine Learning & Groq

```
mlops/
├── groq/
│   ├── config.py        # Groq configuration
│   └── __init__.py
├── requirements_groq.txt (symlink to root)
└── models/             # (Optional) Model configs
```

**What to do:**
```bash
ln -s ../requirements_groq.txt mlops/requirements_groq.txt
```

### `deployment/` - Docker & Kubernetes

```
deployment/
├── docker/
│   ├── Dockerfile          # Backend image
│   ├── Dockerfile.streamlit # Frontend image
│   └── .dockerignore
├── kubernetes/            # K8s manifests (future)
└── scripts/
    └── deploy.sh         # Main deployment script
```

**Commands:**
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### `docs/` - All Documentation

```
docs/
├── README.md              # Documentation index
├── guides/               # How-to guides
│   ├── development-setup.md
│   ├── docker-deployment.md
│   ├── kubernetes-deployment.md
│   ├── troubleshooting.md
│   └── performance.md
├── api/                 # API references
│   ├── backend.md
│   ├── email-generator.md
│   └── product-matcher.md
└── architecture.md      # System architecture
```

**Moved docs:**
- ✅ QUICK_START.md → docs/guides/
- ✅ ARQUITETURA.md → docs/
- ✅ GROQ_MIGRATION.md → docs/guides/
- ✅ STREAMLIT_GUIDE.md → docs/guides/
- ✅ SMTP_DISPATCHER.md → docs/api/
- ✅ README_PRODUCT_MATCHER.md → docs/api/

### `infra/` - Infrastructure as Code

```
infra/
├── terraform/         # AWS/Cloud infrastructure
├── ansible/          # Configuration management
└── helm/            # Kubernetes charts (future)
```

### `scripts/` - Utility Scripts

```
scripts/
├── setup.sh           # Dev environment setup
├── check-quality.sh   # Code quality checks
└── deploy.sh         # Deployment (symlink)
```

**Usage:**
```bash
bash scripts/setup.sh           # First time setup
bash scripts/check-quality.sh   # Pre-commit checks
bash scripts/deploy.sh          # Deploy to prod
```

---

## 🔄 Migration Checklist

### Step 1: Copy Core Services
```bash
cp -r services/lead_extractor backend/services/
```

### Step 2: Create Symlinks (Optional)
```bash
cd frontend && ln -s ../app_hunter.py . && cd ..
cd mlops && ln -s ../requirements_groq.txt . && cd ..
```

### Step 3: Update Imports (Gradual)
```python
# Old
from services.lead_extractor import PipelineExtracao

# New (Long-term)
from backend.services.lead_extractor import PipelineExtracao
```

**Strategy**: Use an import alias for gradual migration:
```python
# In backend/__init__.py
from .services.lead_extractor import *
```

### Step 4: Update Documentation Cross-References
```bash
# All docs in docs/ instead of root
sed -i 's|README_PRODUCT_MATCHER.md|docs/api/product-matcher.md|g' README.md
```

### Step 5: Update GitHub Workflows
```bash
# .github/workflows/ci-cd.yml already configured
# Workflow runs: tests, linting, security, build, push
```

---

## 📝 Configuration Files

### `pyproject.toml`
- Python project metadata
- Dependencies (main, dev, extras)
- Tool configurations (black, isort, mypy, pytest)
- Build system info

### `.env.example`
Template for environment variables. Users copy to `.env` and fill in.

### `docker-compose.yml`
Local development setup with both backend and frontend.

### `.github/workflows/ci-cd.yml`
GitHub Actions pipeline for automated testing and deployment.

---

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v --cov=services --cov=backend
```

### Run Specific Test
```bash
pytest tests/unit/test_email_generator.py -v
```

### Generate Coverage Report
```bash
pytest --cov=services --cov-report=html
open htmlcov/index.html
```

---

## 🎯 Development Workflow

### 1. Create Feature Branch
```bash
git checkout -b feature/my-feature
```

### 2. Make Changes
```bash
# Edit files
# Add tests
# Update docs
```

### 3. Check Quality
```bash
bash scripts/check-quality.sh
```

### 4. Run Tests
```bash
pytest tests/
```

### 5. Commit
```bash
git add .
git commit -m "feat: description of feature"
```

### 6. Push & Create PR
```bash
git push origin feature/my-feature
```

---

## 📦 Building & Deployment

### Development
```bash
# Setup dev environment
bash scripts/setup.sh

# Run Streamlit
streamlit run app_hunter.py

# Run tests
pytest
```

### Staging/Production
```bash
# Build Docker images
docker-compose build

# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Deploy script
bash deployment/scripts/deploy.sh production
```

---

## 🔧 Configuration

### Environment Variables
```bash
# Create .env from template
cp .env.example .env

# Set your keys
GROQ_API_KEY=gsk_YOUR_KEY
SMTP_PASSWORD=your_password
```

### Logs
```bash
# All logs in logs/ directory
tail -f logs/lead_extractor_*.log

# Filter by component
grep -i groq logs/*.log
```

---

## 📚 Documentation

### Update Documentation
When you make changes:
1. Update relevant `.md` file
2. Update `docs/` version if applicable
3. Update `docs/README.md` table of contents

### Add New Guide
```bash
# Create in docs/guides/
touch docs/guides/my-guide.md

# Add reference in docs/README.md
```

---

## 🚢 Deployment Checklist

- [ ] All tests passing
- [ ] Code quality checks passed
- [ ] Documentation updated
- [ ] `.env` configured
- [ ] Database migrations run
- [ ] Docker images built
- [ ] Health checks pass
- [ ] Logs reviewed

---

## ❓ FAQ

**Q: Should I still use the root `services/` directory?**  
A: Gradually migrate to `backend/services/`. Keep root version during transition.

**Q: Where should I add a new module?**  
A: If it's a microservice → `backend/services/`, if it's a script → `scripts/`, if it's docs → `docs/`.

**Q: How do I deploy to production?**  
A: Use `bash deployment/scripts/deploy.sh production` or `docker-compose up -d`.

**Q: Where are the logs?**  
A: In `logs/` directory, filtered by component and timestamp.

---

## 📞 Support

- 📖 [Documentation](docs/README.md)
- 🐛 [Report Issues](https://github.com/cdkteck/hunterteck/issues)
- 💬 [Email: sdr@cdkteck.com.br](mailto:sdr@cdkteck.com.br)

---

**Last Updated**: April 14, 2026  
**Version**: 1.0 Professional Structure
