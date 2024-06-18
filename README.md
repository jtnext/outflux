# Outflux

_The existence of influx implies the existence of outflux._

This is a small administrative CLI tool in case in case some data needs to be removed from InfluxDB.

## Installation

Lacking CI/CD, this package is not in one of our Python package registries yes.
So for the time being, you can install it directly from git.
I'd recommend [pipx](https://pipx.pypa.io/stable/) instead of raw `pip` for that purpose.

```sh
pipx install git+ssh://git@github.com/jtnext/outflux.git --pip-args "-c https://raw.githubusercontent.com/jtnext/outflux/main/requirements.txt"
```

## Usage

See `outflux --help`:

```
usage: outflux [-h] -d DB -m MEASUREMENT -s START -e END [-u USERNAME] [-p] [-v] [-i INFLUX_URL] timeseries [timeseries ...]

positional arguments:
  timeseries            Timeseries UUIDs to delete

optional arguments:
  -h, --help            show this help message and exit
  -d DB, --db DB        InfluxDB DB name
  -m MEASUREMENT, --measurement MEASUREMENT
                        InfluxDB measurement name
  -s START, --start START
                        Start date of time range to delete in ISO format
  -e END, --end END     End date of time range to delete in ISO format
  -u USERNAME, --username USERNAME
                        InfluxDB username
  -p, --password        Prompt for InfluxDB password
  -v, --verbose         Increase output verbosity
  -i INFLUX_URL, --influx-url INFLUX_URL
                        InfluxDB query URL
```

Credentials for InfluxDB can be set via `OUTFLUX_USERNAME` and `OUTFLUX_PASSWORD` environment variables alternatively.

The `--verbose` flag has no effect yet.

## Development

To set up a development environment from scratch:

```sh
# Install UV if necessary
pipx install uv

# Configure package index for UV
export UV_INDEX_URL=https://trading.python.readonly:<PASSWORD>@nexus.domain.next-kraftwerke.de/repository/pypi-all/simple

# Clone repository
git clone git@github.com:jtnext/outflux.git && cd outflux

# Create & activate venv
uv venv -p python3.9 && source .venv/bin/activate

# Install package & development dependencies in editable mode
uv pip install -e '.[dev]' -c requirements.txt
```

Dependencies are managed in `pyproject.toml`.
After making any changes there, re-create constraints in `requirements.txt` and update your venv as follows:

```sh
# Create constraints file
uv pip compile --all-extras -o requirements.txt pyproject.toml

# Re-install package & depencencies into venv
uv pip install -e '.[dev]' -c requirements.txt
```
