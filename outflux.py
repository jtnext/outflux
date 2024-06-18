#! /usr/bin/env python3

import getpass
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from typing import Any, Optional, TypedDict, cast
from uuid import UUID
from zoneinfo import ZoneInfo

from requests.sessions import Session

ZONE_INFO = ZoneInfo("Europe/Berlin")


class ConfigError(Exception): ...


class Params(TypedDict):
    db: str
    q: str


class Outflux:
    def __init__(self, url: str, db: str, measurement: str, start: datetime, end: datetime):
        self.url = url
        self.db = db
        self.measurement = measurement
        self.start_ts = self._timestamp_ns(start)
        self.end_ts = self._timestamp_ns(end)

    def execute(self, session: Session, query: str) -> Any:
        params = self._params(query)

        response = session.post(self.url, params=cast(dict[str, str], params))
        response.raise_for_status()

        return response.json()

    def query_select(self, uuid: UUID) -> str:
        return f"select * from {self.measurement} where time>={self.start_ts} and time<{self.end_ts} and uuid='{uuid}'"

    def query_delete(self, uuid: UUID) -> str:
        return f"delete from {self.measurement} where time>={self.start_ts} and time<{self.end_ts} and uuid='{uuid}'"

    def _params(self, query: str) -> Params:
        return {"db": self.db, "q": query}

    @staticmethod
    def _timestamp_ns(dt: datetime, zone_info: ZoneInfo = ZONE_INFO) -> int:
        ns_factor = 1_000_000_000
        return int(dt.astimezone(zone_info).timestamp() * ns_factor)


def main() -> int:
    status = os.EX_OK

    try:
        try_main(sys.argv)
    except ConfigError as err:
        print(err)
        status = os.EX_CONFIG

    sys.exit(status)


def try_main(argv: list[str]) -> None:
    parser = ArgumentParser()
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
    parser.add_argument(
        "-i",
        "--influx-url",
        type=str,
        default="http://influxdb1.domain.next-kraftwerke.de:8086/query",
        help="InfluxDB query URL",
    )
    parser.add_argument("timeseries", type=UUID, nargs="+", help="Timeseries UUIDs to delete")

    args = parser.parse_args(argv[1:])

    if (username := os.getenv("OUTFLUX_USERNAME", args.username)) is None:
        raise ConfigError("Environment variable OUTFLUX_USERNAME not set")

    password_getpass: Optional[str] = None
    if args.password:
        password_getpass = getpass.getpass(f"Password for user {username} on {args.influx_url}: ")

    if (password := os.getenv("OUTFLUX_PASSWORD", password_getpass)) is None:
        raise ConfigError("Environment variable OUTFLUX_PASSWORD not set")

    print(f"URL: {args.influx_url}")
    print(f"DB: {args.db}")
    print(f"Measurement: {args.measurement}")

    outflux = Outflux(args.influx_url, args.db, args.measurement, args.start, args.end)
    with Session() as session:
        session.auth = (username, password)

        for uuid in args.timeseries:
            query_select = outflux.query_select(uuid)
            print(f"Query: {query_select}")

            result_select = outflux.execute(session, query_select)
            print(result_select)

            confirm = input("Delete data? [y/N] ")
            if confirm.lower() not in {"y", "yes"}:
                continue

            query_delete = outflux.query_delete(uuid)
            print(f"Query: {query_delete}")

            result_delete = outflux.execute(session, query_delete)
            print(result_delete)

    print("Done.")



if __name__ == "__main__":
    main()
