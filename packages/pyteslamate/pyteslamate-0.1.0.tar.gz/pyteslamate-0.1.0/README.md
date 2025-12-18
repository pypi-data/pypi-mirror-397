# pyTeslaMate

pyTeslaMate is an asynchronous Python client for the [TeslaMateApi](https://github.com/tobiasehlert/teslamateapi).
Provides asyncio-friendly helpers to fetch cars, drives, charges, status and global settings using aiohttp and Pydantic v2 models.

[TeslaMateApi](https://github.com/tobiasehlert/teslamateapi) is a RESTful API written in Go to get data of the awesome self-hosted data logger [TeslaMate](https://github.com/teslamate-org/teslamate).

In order to use pyTeslaMate you need to have fully working:
1. TeslaMate
2. TeslaMateApi

## Installation

pyTeslaMate installation:
```bash
pip install pyteslamate
```

Install the project and development tools (requires uv):
```bash
uv sync --all-extras --dev
```
Or install from source:
```bash
uv build
uv run pip install dist/*.whl
```
## Quickstart

Create an async client and call the API:
```python
import asyncio
from datetime import datetime
from pyteslamate import Teslamate

async def main():
    async with Teslamate(base_url="https://api.example.com/api/v1/") as client:
    # fetch all cars
    cars = await client.get_cars()
    print(cars.model_dump())
    # fetch charges for car 1 in a date range
    charges = await client.get_car_charges(
        1,
        start_date=datetime(2025, 12, 1),
        end_date=datetime(2025, 12, 8),
    )
    print(charges.model_dump())

if __name__ == "__main__":
    asyncio.run(main())
```

## Models

All response payloads are validated into Pydantic v2 models under `pyteslamate.models`. Use:

- `.model_validate(data)` to validate a dict
- `.model_dump()` / `.model_dump_json()` to serialize

## Current Limitations & Future Work

### Command Operations
Currently, only read operations are implemented. Write operations for sending commands to vehicles (e.g., wake up, climate control, charging control) are planned for future releases.

### API Key Authentication
API key authentication is not yet tested or fully supported. Implementation is pending the merge of a [PR in TeslaMateApi](https://github.com/tobiasehlert/teslamateapi/pull/352) that will enable API key functionality. Once merged, authentication support will be added with comprehensive test coverage.


## Testing & Coverage

Run the tests and show missing coverage:

    uv run pytest --cov=src --cov-report=term-missing --cov-report=html

Open generated HTML report:

    xdg-open htmlcov/index.html

## Development

Run linters / formatters and pre-commit:

    pre-commit run --all-files

Key checks included: ruff, mypy, pylint, pytest, yamllint, codespell.

## Contributing

- Follow existing style (pylint / ruff)
- Add tests for new features (use `tests/response_examples.py` fixtures)
- Keep Pydantic models in `src/pyteslamate/models.py` synchronized with API payloads

## License

This project is licensed under the [MIT License](LICENSE).
