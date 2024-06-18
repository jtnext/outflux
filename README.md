# Outflux

_The existence of influx implies the existence of outflux._

This is a small administrative CLI tool in case in case some data needs to be removed from InfluxDB.

## Installation

Lacking CI/CD, this package is not in one of our Python package registries yes.
So for the time being, you can install it directly from git.
I'd recommend [pipx](https://pipx.pypa.io/stable/) instead of raw `pip` for that purpose.

```sh
pipx install git+ssh://git@github.com/jtnext/outflux.git
```

## Usage

See `outflux --help`.

Credentials for InfluxDB can be set via `OUTFLUX_USERNAME` and `OUTFLUX_PASSWORD` environment variables alternatively.

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
