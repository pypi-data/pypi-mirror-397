# Printables Stats Scraper

A Python library and CLI tool to scrape public user statistics from [Printables.com](https://www.printables.com), including detailed badge levels.

## Features

- **Public Stats**: Fetches downloads, likes, followers, following, joined date, and model count.
- **Detailed Badges**: Parses badges into a dictionary of `{Name: Level}` (e.g., `{'Designer': 1, 'Maker': 4}`).

## Installation

### From PyPI

```bash
pip install printables-stats
```

### From Source

This project uses `uv` for dependency management.

```bash
# Clone the repository
git clone https://gitlab.com/yourusername/printables-stats.git
cd printables-stats

# Install dependencies
uv sync
```

## Usage

### CLI

You can use the included script to fetch stats for a specific user via environment variable.

```bash
export PRINTABLES_USER_ID='@josefprusa'
uv run python -m printables_stats
```

**Output Example:**

```json
{
  "downloads": 4,
  "likes": 1,
  "followers": 0,
  "following": 4,
  "joined_date": "November 6, 2025",
  "models_count": 4,
  "badges": {
    "Designer": 1,
    "Maker": 4,
    "Download Maniac": 3,
    "Printables Maniac": 1
  }
}
```

### Library

```python
from printables_stats import PrintablesClient

client = PrintablesClient()
stats = client.get_user_stats('@josefprusa')

if stats:
    print(f"Downloads: {stats.get('downloads')}")
    print(f"Badges: {stats.get('badges')}")
```

## Development

Run quality checks and tests:

```bash
uv run ruff check .

uv run ruff format .

uv run ty check .

uv run pytest
```

## Releasing to PyPI

### Release Process

1. Update the version in `pyproject.toml`
2. Commit and push your changes
3. Create and push a git tag:
   ```bash
   git tag v0.1.2
   git push origin v0.1.2
   ```
4. In GitLab, navigate to CI/CD → Pipelines
5. Manually trigger the `release` job to publish to PyPI
6. Verify the package on https://pypi.org/project/printables-stats/
