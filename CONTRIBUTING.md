# Contributing to HunterTeck

Thank you for considering contributing to HunterTeck! This document provides guidelines and instructions for contributing.

## Code of Conduct

Our community is based on:
- **Respect**: Be respectful and inclusive
- **Quality**: Write clean, tested code
- **Documentation**: Document your changes
- **Collaboration**: Work together towards better solutions

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/YOUR_USERNAME/hunterteck.git`
3. **Create** a feature branch: `git checkout -b feature/my-feature`
4. **Setup** development environment: `bash scripts/setup.sh`

## Development Workflow

### Before Writing Code

1. Check existing [issues](https://github.com/cdkteck/hunterteck/issues)
2. Create an issue describing your feature/fix
3. Get feedback from maintainers before starting

### Writing Code

1. Follow Python style guide ([PEP 8](https://www.python.org/dev/peps/pep-0008/))
2. Add type hints (PEP 484)
3. Write tests for new features
4. Update documentation

### Code Quality

Run quality checks before committing:

```bash
bash scripts/check-quality.sh
```

This runs:
- **black** - Code formatting
- **flake8** - Code linting
- **mypy** - Type checking
- **isort** - Import sorting

### Testing

Add tests for your changes:

```bash
pytest tests/ -v --cov=services
```

Minimum coverage requirement: **80%**

### Committing

Use clear, descriptive commit messages:

```
feat: add retry mechanism for Groq API
fix: handle rate limits in batch processing
docs: update architecture documentation
test: add tests for email generator
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Test addition/modification
- `refactor:` - Code refactoring
- `perf:` - Performance improvement

## Pull Request Process

1. **Update** your branch with latest `main`: `git pull upstream main`
2. **Push** to your fork: `git push origin feature/my-feature`
3. **Create** a Pull Request with:
   - Clear description of changes
   - Reference to related issue (#123)
   - Test results/coverage
4. **Wait** for CI/CD to pass
5. **Address** review comments
6. **Merge** after approval

## Documentation

Update docs if you:
- Add new features
- Change existing behavior
- Modify configuration options

Documentation locations:
- **Architecture changes**: `docs/ARCHITECTURE.md`
- **API changes**: `docs/api/`
- **Guides**: `docs/guides/`
- **READMEs**: Update relevant `README.md` files

## Bug Reports

Click "Bug Report" issue template and provide:
- Clear title
- Detailed description
- Steps to reproduce
- Expected vs actual behavior
- Version info
- Relevant logs

## Feature Requests

Click "Feature Request" issue template and describe:
- Use case
- Proposed solution
- Alternatives considered
- Any additional context

## Questions?

- **Docs**: Check [documentation](docs/)
- **Issues**: Search [existing issues](https://github.com/cdkteck/hunterteck/issues)
- **Email**: sdr@cdkteck.com.br

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making HunterTeck better!** 🚀
