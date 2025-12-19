# rotarex-dimes-srg-api/README.md

# Rotarex Dimes SRG API

This project provides a Python API client for interacting with the Rotarex Dimes SRG service. It allows users to fetch tank information and perform other operations related to the service.

## Installation

To install the package, you can use pip:

```bash
pip install rotarex-dimes-srg-api
```

## Usage

Here is a simple example of how to use the Rotarex API client:

```python
import asyncio
import aiohttp
from rotarex_api import RotarexApi

async def main():
    async with aiohttp.ClientSession() as session:
        api = RotarexApi(session)
        api.set_credentials("your_email@example.com", "your_password")
        tanks = await api.fetch_tanks()
        print(tanks)

if __name__ == "__main__":
    asyncio.run(main())
```

## Running Tests

To run the tests for this project, you can execute the following command:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.