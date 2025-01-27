import getpass
import logging
import os
import sys
from argparse import ArgumentParser, Namespace
from datetime import datetime
from typing import Optional
from uuid import UUID

from requests.exceptions import HTTPError
from requests.sessions import Session
from urllib3.exceptions import NameResolutionError

from outflux.outflux import Outflux


class ConfigError(Exception): ...


def main() -> int:
    status = os.EX_OK
    logging.basicConfig(level=logging.INFO)

    try:
        try_main()
    except ConfigError as err:
        print(err)
        status = os.EX_CONFIG
    except (NameResolutionError, HTTPError) as err:
        print(err)
        status = os.EX_IOERR
    except KeyboardInterrupt:
        print("Aborting")
        status = os.EX_OSERR

    sys.exit(status)


def try_main() -> None:
    args = parse_args(sys.argv)

    if (username := os.getenv("OUTFLUX_USERNAME", args.username)) is None:
        raise ConfigError("Environment variable OUTFLUX_USERNAME not set")

    password_getpass: Optional[str] = None
    if args.password:
        password_getpass = getpass.getpass(f"Password for user {username} on {args.influx_url}: ")

    if (password := os.getenv("OUTFLUX_PASSWORD", password_getpass)) is None:
        raise ConfigError("Environment variable OUTFLUX_PASSWORD not set")

    outflux = Outflux(args.influx_url, args.db, args.measurement, args.start, args.end)
    print(f"URL: {outflux.url}")
    print(f"DB: {outflux.db}")
    print(f"Measurement: {outflux.measurement}")

    with Session() as session:
        session.auth = (username, password)
        for uuid in args.timeseries:
            process_timeseries(outflux, session, uuid)

    print("Done.")


def parse_args(argv: list[str]) -> Namespace:
    parser = ArgumentParser()
    parser.add_argument(
        "-i",
        "--influx-url",
        type=str,
        default="http://influxdb1.domain.next-kraftwerke.de:8086/query",
        help="InfluxDB query URL",
    )
    parser.add_argument("-d", "--db", type=str, required=True, help="InfluxDB DB name")
    parser.add_argument("-m", "--measurement", type=str, required=True, help="InfluxDB measurement name")
    parser.add_argument(
        "-s",
        "--start",
        type=datetime.fromisoformat,
        required=True,
        help="Start date of time range to delete in ISO format",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=datetime.fromisoformat,
        required=True,
        help="End date of time range to delete in ISO format",
    )
    parser.add_argument("-u", "--username", type=str, help="InfluxDB username")
    parser.add_argument(
        "-p", "--password", action="store_true", help="Prompt for InfluxDB password"
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("timeseries", type=UUID, nargs="+", help="Timeseries UUIDs to delete")

    return parser.parse_args(argv[1:])


def process_timeseries(outflux: Outflux, session: Session, uuid: UUID) -> None:
    query_select = outflux.query_select(uuid)
    print(f"\nSelect query: {query_select}")

    result_select = outflux.execute(session, query_select)
    print(result_select)

    confirm = input("Delete data? [y/N] ")
    if confirm.lower() not in ["y", "yes"]:
        return

    query_delete = outflux.query_delete(uuid)
    print(f"Delete query: {query_delete}")

    result_delete = outflux.execute(session, query_delete)
    print(result_delete)

