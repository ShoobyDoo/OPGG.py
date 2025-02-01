[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FShoobyDoo%2FOPGG.py&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23DDDDDD&title=visits&edge_flat=false)](https://hits.seeyoufarm.com)

# OPGG.py
An unofficial Python library for accessing OPGG data.
#### You can view the current active developments on the [OPGG.py Project](https://github.com/users/ShoobyDoo/projects/2) page

## Prerequisites

* [Python 3.11+](https://www.python.org/downloads/) 
    
*Note: Will likely work on versions slightly older or newer*

## Installation

### Automatic

This library is available as a [pip package](https://pypi.org/project/opgg.py/) and can be installed via the following command:
```
py -m pip install opgg.py
```

### Manual

#### Dependencies
* [requests](https://pypi.org/project/requests/)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)
* [fake-useragent](https://pypi.org/project/fake-useragent/)

Alternatively, you can use the provided requirements.txt to install the required libraries by running the following command: <br>
```
py -m pip install -r requirements.txt
```

## Usage / Basic Example

### Importing the library (v2)
```python
from opgg.v2.opgg import OPGG
from opgg.v2.params import Region


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
```
[NA  ] HandoftheCouncil #NA1     | Level: 547  [Summoner ID: t7NuBl5eATWiqoZMu2MzZbAX1S9IDyp4Kzut5Z_4QT3-tWs]
```

## Join the Discussion
Here's a link to the [Support Discord](https://discord.gg/fzRK2Sb)
