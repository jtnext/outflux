from datetime import datetime

from hypothesis import given, strategies as st

from outflux.outflux import Outflux, ZONE_INFO


@given(db=st.text(), measurement=st.text(), start=st.datetimes(), end=st.datetimes())
def test_init(db: str, measurement: str, start: datetime, end: datetime) -> None:
    url = "http://influxdb-unittest:8086"

    outflux = Outflux(url, db, measurement, start, end)

    assert outflux.url == url
    assert outflux.db == db
    assert outflux.measurement == measurement

    assert datetime.fromisoformat(outflux.start) == start.astimezone(ZONE_INFO)
    assert datetime.fromisoformat(outflux.end) == end.astimezone(ZONE_INFO)
