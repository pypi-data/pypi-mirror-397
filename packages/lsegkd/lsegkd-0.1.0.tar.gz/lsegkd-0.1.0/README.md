# LSEG Knowledge Direct

[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python library for retrieving financial data using the LSEG Knowledge Direct API.

## Features

- Authentication management for LSEG Knowledge Direct API
- Retrieve headlines, transcripts, and XML data
- Command-line interface (CLI)
- Structured JSON file output

## Installation

### From PyPI (recommended)

```bash
uv add lsegkd
```

or

```bash
pip install lsegkd
```

### Development Installation

```bash
git clone https://github.com/yurukatsu/lseg-knowledge-direct.git
cd lseg-knowledge-direct
uv sync --all-groups
```

## Usage

### Command Line Usage

Retrieve documents for a specified period and countries:

```bash
uv run lsegkd -d .env load-document --from_date 2025-11-22 --to_date 2025-11-23 --countries US --countries UK
```

### Authentication Setup

Set the following environment variables:

```bash
export LSEG_KNOWLEDGE_DIRECT_USERNAME="your_username"
export LSEG_KNOWLEDGE_DIRECT_APP_ID="your_app_id"
export LSEG_KNOWLEDGE_DIRECT_PASSWORD="your_password"
```

Alternatively, you can specify credentials directly using the Credentials class:

```python
from lsegkd.credentials import Credentials

credentials = Credentials(
    username="your_username",
    app_id="your_app_id", 
    password="your_password"
)
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
