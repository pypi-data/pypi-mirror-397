<!-- Import workspace-level CLAUDE.md configuration -->
<!-- See /home/lab/workspace/.claude/CLAUDE.md for complete rules -->

# Project-Specific Configuration

This file extends workspace-level configuration with project-specific rules.

## Project Context

**stellars_jupyterlab_favourites** - Python metapackage aggregating JupyterLab extensions, fixes, themes, and curated third-party packages.

**Technology Stack**:
- Python >= 3.10
- Hatchling build system
- PyPI distribution

**Project Structure**:
- `pyproject.toml` - Package metadata and dependencies
- `Makefile` - Build, install, and publish automation
- `README.md` - Package documentation with badges

**Build Commands**:
- `make build` - Build package (auto-increments version)
- `make install` - Install locally (auto-increments version)
- `make publish` - Publish to PyPI (auto-increments version)
- `make clean` - Remove build artifacts

**Naming Conventions**:
- Package name uses underscores: `stellars_jupyterlab_favourites`
- GitHub/PyPI URLs follow stellarshenson organization pattern
