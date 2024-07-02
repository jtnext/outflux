from datetime import datetime
from typing import Any, TypedDict, cast
from uuid import UUID
from zoneinfo import ZoneInfo

from requests.sessions import Session

ZONE_INFO = ZoneInfo("Europe/Berlin")


class Params(TypedDict):
    db: str
    q: str


class Outflux:
    def __init__(self, url: str, db: str, measurement: str, start: datetime, end: datetime):
        self.url = url
        self.db = db
        self.measurement = measurement
        self.start = self._localized_isoformat(start)
        self.end = self._localized_isoformat(end)

    def execute(self, session: Session, query: str) -> Any:
        params = self._params(query)

        response = session.post(self.url, params=cast(dict[str, str], params))
        response.raise_for_status()

        return response.json()

    def query_select(self, uuid: UUID) -> str:
        return f"select * from {self.measurement} where time>='{self.start}' and time<'{self.end}' and uuid='{uuid}'"

    def query_delete(self, uuid: UUID) -> str:
        return f"delete from {self.measurement} where time>={self.start} and time<{self.end} and uuid='{uuid}'"

    def _params(self, query: str) -> Params:
        return {"db": self.db, "q": query}

    @staticmethod
    def _localized_isoformat(dt: datetime, zone_info: ZoneInfo = ZONE_INFO) -> str:
        return dt.astimezone(zone_info).isoformat()
