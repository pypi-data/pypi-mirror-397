# TWMetro

TWMetro is a Python library that provides an interface to access and retrieve status information about the Tyne and Wear Metro system in the UK.

## Currently Supported Features

- Retrive a list of all Metro lines and their coordinate points
- Retrieve a list of all Metro stations
- Retrieve the status of all Metro trains
- Retrieve a list of all Metro incidents

## Installation

You can install the TWMetro library using pip:

```bash
pip install TWMetro
```

## Usage

> [!IMPORTANT]
> A JWT token is required to access the API. I cannot provide this token via scraping, so you will need to obtain it yourself from the Nexus website [here](https://www.nexus.org.uk/metro/updates).

```python
from TWMetro import TWMetro

client = TWMetro("your_jwt_token_here")

# Get all Metro lines
lines = client.get_lines()

# Get all Metro stations
stations = client.get_metrostations()
# Get all Metro train status
trains = client.get_trainstatus()
# Get all Metro incidents
incidents = client.get_warnings()
# Get all metro lines
lines = client.get_metrolines()
```