# OPGG.py

An unofficial Python library for accessing OPGG data.

## Prerequisites

- [Python 3.12+](https://www.python.org/downloads/)

**Note:** *Will likely work on versions slightly older or newer*

## Installation

### Automatic

This library is available as a [pip package](https://pypi.org/project/opgg.py/) and can be installed via the following command:

```cmd
py -m pip install opgg.py
```

### Manual

#### Dependencies

- [aiohttp](https://pypi.org/project/aiohttp/)
- [pydantic](https://pypi.org/project/pydantic/)
- [fake-useragent](https://pypi.org/project/fake-useragent/)

Alternatively, you can use the provided requirements.txt to install the required libraries by running the following command:

```cmd
py -m pip install -r requirements.txt
```

## Usage / Basic Example

### Importing the library

```python
from opgg.opgg import OPGG
from opgg.params import Region


def main():
    opgg = OPGG()

    results = opgg.search("HandOfTheCouncil", Region.NA)
    [print(result) for result in results]


if __name__ == "__main__":
    main()
```

### Output

**Important Note:** The information returned below is a summary view with the most important parts of each object shown "at a glance".
Many of the objects have several additional properties that can be accessed by referencing the object in code.

```txt
[NA  ] HandoftheCouncil #NA1     | Level: 556  [Summoner ID: t7NuBl5eATWiqoZMu2MzZbAX1S9IDyp4Kzut5Z_4QT3-tWs]
```

## Development

### Setting Up Development Environment

Step 1. Clone the repository:

```bash
git clone https://github.com/ShoobyDoo/OPGG.py.git
cd OPGG.py
```

Step 2. Install production dependencies:

```bash
pip install -r requirements.txt
```

### Code Quality

Run linting with ruff:

```bash
ruff check opgg/
```

Auto-fix linting issues:

```bash
ruff check --fix opgg/
```

Check code formatting:

```bash
ruff format --check opgg/
```

Auto-format code:

```bash
ruff format opgg/
```

Ensure code formatting is run prior to opening a pull request.

## Join the Discussion

Here's a link to the [Support Discord](https://discord.gg/fzRK2Sb)
